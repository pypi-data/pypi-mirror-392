# -*- coding: utf-8 -*-
from __future__ import annotations

import warnings
from typing import Dict, Tuple, Optional

import numpy as np
import xarray as xr
from scipy.stats import norm

# scikit-learn
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from sklearn.model_selection import RandomizedSearchCV
from sklearn.cluster import KMeans


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _standardize_timeseries(da: xr.DataArray, clim_year_start: int | str, clim_year_end: int | str) -> xr.DataArray:
    """Z-score along T using the climatology window [start,end].
    Works for shapes (T,Y,X) and (T,M,Y,X). Returns same shape as input.
    """
    if 'T' not in da.dims:
        raise ValueError("DataArray must have a 'T' dimension")
    clim = da.sel(T=slice(str(clim_year_start), str(clim_year_end)))

    # compute mean/std over T preserving other dims
    mean = clim.mean('T')
    std = clim.std('T')
    std = xr.where(std == 0, np.nan, std)
    out = (da - mean) / std
    return out.fillna(0.0)


def _compute_terciles(y: xr.DataArray, clim_year_start: int | str, clim_year_end: int | str) -> Tuple[xr.DataArray, xr.DataArray]:
    """Return (T1, T2) with dims (Y,X)."""
    y = y.transpose('T', 'Y', 'X')
    clim = y.sel(T=slice(str(clim_year_start), str(clim_year_end)))
    q = clim.quantile([0.33, 0.67], dim='T')
    T1 = q.isel(quantile=0).drop_vars('quantile')
    T2 = q.isel(quantile=1).drop_vars('quantile')
    return T1, T2


def _cluster_grid_from_predictand(
    predictand: xr.DataArray,
    n_clusters: int,
    clim_year_start: int | str,
    clim_year_end: int | str,
    random_state: int = 42,
) -> xr.DataArray:
    """Cluster (Y,X) into n_clusters using 2 features: climatological mean and std.
    Returns an integer DataArray of shape (Y,X) with NaN where predictand is missing.
    """
    y = predictand.transpose('T','Y','X')
    clim = y.sel(T=slice(str(clim_year_start), str(clim_year_end)))
    feat_mean = clim.mean('T')
    feat_std = clim.std('T')

    df = xr.Dataset({'f1': feat_mean, 'f2': feat_std}).to_dataframe().reset_index()
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    if df.empty:
        raise ValueError("No finite grid cells available for clustering.")
    kmeans = KMeans(n_clusters=int(n_clusters), random_state=int(random_state), n_init='auto')
    labels = kmeans.fit_predict(df[['f1','f2']].values)
    df['cluster'] = labels

    lab = df.set_index(['Y','X'])['cluster'].to_xarray()
    # reindex to full grid, NaN where missing
    lab = lab.reindex_like(feat_mean)
    return lab.astype(float)


def _build_kernel(length_scale: float, noise_level: float) -> RBF:
    return RBF(length_scale=float(length_scale)) + WhiteKernel(noise_level=float(noise_level))


def _cdf_probs_from_gaussian(mu: np.ndarray, sig: np.ndarray, q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    sig = np.maximum(sig, 1e-8)
    F1 = norm.cdf(q1, loc=mu, scale=sig)
    F2 = norm.cdf(q2, loc=mu, scale=sig)
    pb = F1
    pn = np.clip(F2 - F1, 0.0, 1.0)
    pa = 1.0 - F2
    out = np.vstack([pb, pn, pa])
    # normalize just in case of tiny numeric drift
    s = out.sum(axis=0)
    good = s > 0
    out[:, good] /= s[good]
    return out


# ------------------------------------------------------------
# Main class
# ------------------------------------------------------------
class WAS_mme_GP:
    """
    Gaussian-Process-based probabilistic MME with spatial homogenization and per-zone hyperparameter tuning.

    - Clusters the grid (Y,X) into `n_clusters` zones using predictand climatology (mean & std).
    - Tunes RBF+WhiteKernel hyperparameters per zone via RandomizedSearchCV.
    - Trains a zone-specific GPR and returns PB/PN/PA from the Gaussian predictive distribution.

    Parameters
    ----------
    length_scale_range : list[float]
        Candidate length_scales for RBF.
    noise_level_range : list[float]
        Candidate noise_levels for WhiteKernel.
    random_state : int
        RNG seed.
    dist_method : str
        Must be 'normal' (Gaussian predictive). Other values are not supported.
    n_iter_search : int
        Randomized search iterations.
    cv_folds : int
        CV folds for hyperparameter search.
    n_clusters : int
        Number of spatial zones.
    """

    def __init__(
        self,
        length_scale_range: list[float] | None = None,
        noise_level_range: list[float] | None = None,
        random_state: int = 42,
        dist_method: str = 'normal',
        n_iter_search: int = 10,
        cv_folds: int = 3,
        n_clusters: int = 4,
    ) -> None:
        if length_scale_range is None:
            length_scale_range = np.logspace(-1, 1, 5).tolist()
        if noise_level_range is None:
            noise_level_range = np.logspace(-5, -1, 5).tolist()
        self.length_scale_range = length_scale_range
        self.noise_level_range = noise_level_range
        self.random_state = int(random_state)
        self.dist_method = str(dist_method).lower()
        self.n_iter_search = int(n_iter_search)
        self.cv_folds = int(cv_folds)
        self.n_clusters = int(n_clusters)

        if self.dist_method != 'normal':
            warnings.warn("WAS_mme_GP uses the Gaussian predictive distribution; 'dist_method' is forced to 'normal'.")
            self.dist_method = 'normal'

        self.gp_by_cluster: Dict[int, GaussianProcessRegressor] = {}

    # --------------------- hyperparameters per zone ---------------------
    def compute_hyperparameters(
        self,
        Predictors: xr.DataArray,  # (T,M,Y,X)
        Predictand: xr.DataArray,  # (T,Y,X)
        clim_year_start: int | str,
        clim_year_end: int | str,
    ) -> Tuple[Dict[int, Dict[str, float]], xr.DataArray]:
        if 'M' in Predictand.coords:
            Predictand = Predictand.isel(M=0).drop_vars('M').squeeze()

        # standardize predictors & predictand across T (per member / grid)
        Xs = _standardize_timeseries(Predictors.transpose('T','M','Y','X'), clim_year_start, clim_year_end)
        ys = _standardize_timeseries(Predictand.transpose('T','Y','X'), clim_year_start, clim_year_end)
        Xs = Xs.assign_coords(T=Predictors['T'])
        ys = ys.assign_coords(T=Predictand['T'])

        # cluster grid
        cluster_da = _cluster_grid_from_predictand(Predictand, self.n_clusters, clim_year_start, clim_year_end, self.random_state)

        # param space
        param_dist = {
            'kernel__k1__length_scale': self.length_scale_range,
            'kernel__k2__noise_level': self.noise_level_range,
        }

        best: Dict[int, Dict[str, float]] = {}
        for c in range(self.n_clusters):
            mask_3d = (cluster_da == c).expand_dims({'T': ys['T']})
            X_mat = Xs.where(mask_3d).stack(sample=('T','Y','X')).transpose('sample','M')
            y_vec = ys.where(mask_3d).stack(sample=('T','Y','X'))

            Xv = X_mat.values
            yv = y_vec.values.ravel()
            ok = np.isfinite(yv) & np.all(np.isfinite(Xv), axis=1)
            Xv, yv = Xv[ok], yv[ok]
            if Xv.size == 0:
                continue

            base = GaussianProcessRegressor(kernel=RBF(1.0) + WhiteKernel(1e-5), n_restarts_optimizer=3, random_state=self.random_state, normalize_y=False)
            rs = RandomizedSearchCV(
                base,
                param_distributions=param_dist,
                n_iter=self.n_iter_search,
                cv=self.cv_folds,
                scoring='neg_mean_squared_error',
                random_state=self.random_state,
                error_score=np.nan,
                n_jobs=None,
            )
            rs.fit(Xv, yv)
            if hasattr(rs, 'best_params_') and rs.best_params_ is not None:
                best[c] = {
                    'kernel__k1__length_scale': float(rs.best_params_['kernel__k1__length_scale']),
                    'kernel__k2__noise_level': float(rs.best_params_['kernel__k2__noise_level']),
                }
        return best, cluster_da

    # -------------------------- hindcast (probs) --------------------------
    def compute_model(
        self,
        X_train: xr.DataArray,  # (T,M,Y,X)
        y_train: xr.DataArray,  # (T,Y,X)
        X_test: xr.DataArray,   # (T,M,Y,X)
        y_test: Optional[xr.DataArray],  # ignored for probs
        clim_year_start: int | str,
        clim_year_end: int | str,
        best_params: Optional[Dict[int, Dict[str, float]]] = None,
        cluster_da: Optional[xr.DataArray] = None,
    ) -> xr.DataArray:
        # standardize
        Xs_train = _standardize_timeseries(X_train.transpose('T','M','Y','X'), clim_year_start, clim_year_end)
        ys_train = y_train.transpose('T','Y','X')  # thresholds from raw y_train
        Xs_test  = _standardize_timeseries(X_test.transpose('T','M','Y','X'),  clim_year_start, clim_year_end)

        # compute terciles from y_train
        T1, T2 = _compute_terciles(y_train, clim_year_start, clim_year_end)

        # clusters
        if best_params is None or cluster_da is None:
            best_params, cluster_da = self.compute_hyperparameters(X_train, y_train, clim_year_start, clim_year_end)

        # prepare output
        Tcoord, Ycoord, Xcoord = X_test['T'], X_test['Y'], X_test['X']
        probs = np.full((3, Tcoord.size, Ycoord.size, Xcoord.size), np.nan, dtype=float)

        # per cluster
        for c in range(self.n_clusters):
            if c not in best_params:
                continue
            bp = best_params[c]
            # training data for cluster
            mask_tr = (cluster_da == c).expand_dims({'T': Xs_train['T']})
            Xm = Xs_train.where(mask_tr).stack(sample=('T','Y','X')).transpose('sample','M')
            ym = y_train.where(mask_tr).stack(sample=('T','Y','X'))
            Xi = Xm.values
            yi = ym.values.ravel()
            ok_tr = np.isfinite(yi) & np.all(np.isfinite(Xi), axis=1)
            Xi, yi = Xi[ok_tr], yi[ok_tr]
            if Xi.size == 0:
                continue

            # fit GP for this cluster
            kernel = _build_kernel(bp['kernel__k1__length_scale'], bp['kernel__k2__noise_level'])
            gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, random_state=self.random_state, normalize_y=False)
            gpr.fit(Xi, yi)
            self.gp_by_cluster[c] = gpr

            # test data for this cluster (keep mapping to indices)
            mask_te = (cluster_da == c).expand_dims({'T': Xs_test['T']})
            Xs = Xs_test.where(mask_te).stack(sample=('T','Y','X')).transpose('sample','M')
            Xi_te = Xs.values
            idx = Xs['sample'].to_index()  # pandas.MultiIndex (T,Y,X)
            ok_te = np.all(np.isfinite(Xi_te), axis=1)
            Xi_te = Xi_te[ok_te]
            idx = idx[ok_te]
            if Xi_te.size == 0:
                continue

            mu, sigma = gpr.predict(Xi_te, return_std=True)
            # per-sample thresholds from T1/T2 at (Y,X)
            q1 = np.array([float(T1.sel(Y=iy, X=ix, method='nearest')) for (_, iy, ix) in idx])
            q2 = np.array([float(T2.sel(Y=iy, X=ix, method='nearest')) for (_, iy, ix) in idx])

            pc = _cdf_probs_from_gaussian(mu, sigma, q1, q2)  # (3, n_samples)

            # write back into full grid
            for k in range(len(idx)):
                t, y, x = idx[k]
                ti = int(np.where(Tcoord.values == t)[0][0])
                yi = int(np.where(Ycoord.values == y)[0][0])
                xi = int(np.where(Xcoord.values == x)[0][0])
                probs[:, ti, yi, xi] = pc[:, k]

        return xr.DataArray(
            probs,
            coords={'probability': ['PB','PN','PA'], 'T': Tcoord, 'Y': Ycoord, 'X': Xcoord},
            dims=['probability','T','Y','X'],
        )

    # ---------------------------- forecast (probs) ----------------------------
    def forecast(
        self,
        Predictant: xr.DataArray,            # (T,Y,X) or (T,M,Y,X) -> we use (T,Y,X)
        clim_year_start: int | str,
        clim_year_end: int | str,
        hindcast_det: xr.DataArray,          # (T,M,Y,X) for training predictors
        hindcast_det_cross: xr.DataArray,    # unused here; kept for API parity
        Predictor_for_year: xr.DataArray,    # (T,M,Y,X) target period predictors
        best_params: Optional[Dict[int, Dict[str, float]]] = None,
        cluster_da: Optional[xr.DataArray] = None,
    ) -> xr.DataArray:
        # ensure Predictant is (T,Y,X)
        if 'M' in Predictant.coords:
            Predictant = Predictant.isel(M=0).drop_vars('M').squeeze()
        Predictant = Predictant.transpose('T','Y','X')

        # thresholds from predictant climatology
        T1, T2 = _compute_terciles(Predictant, clim_year_start, clim_year_end)

        # standardize predictors
        Xs_tr = _standardize_timeseries(hindcast_det.transpose('T','M','Y','X'), clim_year_start, clim_year_end)
        Xs_te = _standardize_timeseries(Predictor_for_year.transpose('T','M','Y','X'), clim_year_start, clim_year_end)

        # clusters + hyperparams
        if best_params is None or cluster_da is None:
            best_params, cluster_da = self.compute_hyperparameters(hindcast_det, Predictant, clim_year_start, clim_year_end)

        # output array
        Tcoord, Ycoord, Xcoord = Predictor_for_year['T'], Predictor_for_year['Y'], Predictor_for_year['X']
        probs = np.full((3, Tcoord.size, Ycoord.size, Xcoord.size), np.nan, dtype=float)

        # per cluster evaluation
        for c in range(self.n_clusters):
            if c not in best_params:
                continue
            bp = best_params[c]

            # train GP on hindcast for this cluster
            mask_tr = (cluster_da == c).expand_dims({'T': Xs_tr['T']})
            Xm = Xs_tr.where(mask_tr).stack(sample=('T','Y','X')).transpose('sample','M')
            ym = Predictant.where(mask_tr).stack(sample=('T','Y','X'))
            Xi = Xm.values
            yi = ym.values.ravel()
            ok_tr = np.isfinite(yi) & np.all(np.isfinite(Xi), axis=1)
            Xi, yi = Xi[ok_tr], yi[ok_tr]
            if Xi.size == 0:
                continue

            kernel = _build_kernel(bp['kernel__k1__length_scale'], bp['kernel__k2__noise_level'])
            gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, random_state=self.random_state, normalize_y=False)
            gpr.fit(Xi, yi)
            self.gp_by_cluster[c] = gpr

            # test rows and threshold mapping
            mask_te = (cluster_da == c).expand_dims({'T': Xs_te['T']})
            Xs = Xs_te.where(mask_te).stack(sample=('T','Y','X')).transpose('sample','M')
            Xi_te = Xs.values
            idx = Xs['sample'].to_index()
            ok_te = np.all(np.isfinite(Xi_te), axis=1)
            Xi_te = Xi_te[ok_te]
            idx = idx[ok_te]
            if Xi_te.size == 0:
                continue

            mu, sigma = gpr.predict(Xi_te, return_std=True)
            q1 = np.array([float(T1.sel(Y=iy, X=ix, method='nearest')) for (_, iy, ix) in idx])
            q2 = np.array([float(T2.sel(Y=iy, X=ix, method='nearest')) for (_, iy, ix) in idx])
            pc = _cdf_probs_from_gaussian(mu, sigma, q1, q2)

            for k in range(len(idx)):
                t, y, x = idx[k]
                ti = int(np.where(Tcoord.values == t)[0][0])
                yi = int(np.where(Ycoord.values == y)[0][0])
                xi = int(np.where(Xcoord.values == x)[0][0])
                probs[:, ti, yi, xi] = pc[:, k]

        # set forecast timestamp to the month of the first predictand entry, but forecast year
        try:
            year = int(Predictor_for_year['T'].values.astype('datetime64[Y]').astype(int)[0] + 1970)
            month1 = int(Predictant['T'].values[0].astype('datetime64[M]').astype(int) % 12 + 1)
            new_T = np.datetime64(f"{year}-{month1:02d}-01")
            Tcoord = xr.DataArray([new_T], dims=['T'])
            probs = probs[:, :1, :, :]  # ensure one time step
        except Exception:
            pass

        return xr.DataArray(
            probs,
            coords={'probability': ['PB','PN','PA'], 'T': Tcoord, 'Y': Ycoord, 'X': Xcoord},
            dims=['probability','T','Y','X']
        )
