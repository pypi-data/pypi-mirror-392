class WAS_mme_hpELM:
    """
    Extreme Learning Machine (ELM) based Multi-Model Ensemble (MME) forecasting using hpelm library.
    This class implements a single-model forecasting approach using HPELM for deterministic predictions,
    with optional tercile probability calculations using various statistical distributions.
    Implements hyperparameter optimization via randomized search.
    Parameters
    ----------
    neurons_range : list of int, optional
        List of neuron counts to tune for HPELM (default is [10, 20, 50, 100]).
    activation_options : list of str, optional
        Activation functions to tune for HPELM (default is ['sigm', 'tanh', 'relu', 'rbf_linf', 'rbf_gauss']).
    norm_range : list of float, optional
        Regularization parameters to tune for HPELM (default is [0.1, 1.0, 10.0, 100.0]).
    random_state : int, optional
        Seed for reproducibility (default is 42).
    dist_method : str, optional
        Distribution method for tercile probabilities ('t', 'gamma', etc.) (default is 'gamma').
    n_iter_search : int, optional
        Number of iterations for randomized search (default is 10).
    cv_folds : int, optional
        Number of cross-validation folds (default is 3).
    n_clusters : int, optional
        Number of clusters for homogenized zones (default is 4).
    """
    def __init__(self,
                 neurons_range=[10, 20, 50, 100],
                 activation_options=['sigm', 'tanh', 'relu', 'rbf_linf', 'rbf_gauss'],
                 norm_range=[0.1, 1.0, 10.0, 100.0],
                 random_state=42,
                 dist_method="gamma",
                 n_iter_search=10,
                 cv_folds=3,
                 n_clusters=4):
        self.neurons_range = neurons_range
        self.activation_options = activation_options
        self.norm_range = norm_range
        self.random_state = random_state
        self.dist_method = dist_method
        self.n_iter_search = n_iter_search
        self.cv_folds = cv_folds
        self.n_clusters = n_clusters
        self.hpelm = None

    def compute_hyperparameters(self, Predictors, Predictand, clim_year_start, clim_year_end):
        """
        Independently computes the best hyperparameters using randomized search on stacked training data for each homogenized zone.
        Parameters
        ----------
        Predictors : xarray.DataArray
            Training predictor data with dimensions (T, M, Y, X).
        Predictand : xarray.DataArray
            Training predictand data with dimensions (T, Y, X).
        clim_year_start : int
            Start year of the climatology period.
        clim_year_end : int
            End year of the climatology period.
        Returns
        -------
        best_params_dict : dict
            Best hyperparameters for each cluster.
        cluster_da : xarray.DataArray
            Cluster labels with dimensions (Y, X).
        """
        if "M" in Predictand.coords:
            Predictand = Predictand.isel(M=0).drop_vars('M').squeeze()

            
        X_train_std = standardize_timeseries(Predictors, clim_year_start, clim_year_end)
        Predictand.name = "varname"

        # # Cluster on standardized predictand time series
        # y_for_cluster = y_train_std.stack(space=('Y', 'X')).transpose('space', 'T').values
        # print(y_for_cluster)
        # print(y_for_cluster.shape)
        # finite_mask = np.all(np.isfinite(y_for_cluster), axis=1)
        # y_cluster = y_for_cluster[finite_mask]

        # kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        # labels = kmeans.fit_predict(y_cluster)

        # full_labels = np.full(y_for_cluster.shape[0], np.nan)   # -1
        # full_labels[finite_mask] = labels

        # cluster_da = xr.DataArray(
        #     full_labels.reshape(len(y_train_std['Y']), len(y_train_std['X'])),
        #     coords={'Y': y_train_std['Y'], 'X': y_train_std['X']},
        #     dims=['Y', 'X']
        # )
        # cluster_da.plot()


        # Step 1: Perform KMeans clustering based on predictand's spatial distribution
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        Predictand_dropna = Predictand.to_dataframe().reset_index().dropna().drop(columns=['T'])
        variable_column = Predictand_dropna.columns[2]
        Predictand_dropna['cluster'] = kmeans.fit_predict(
           Predictand_dropna[[variable_column]]
        )
        
        # Convert cluster assignments back into an xarray structure
        df_unique = Predictand_dropna.drop_duplicates(subset=['Y', 'X'])
        dataset = df_unique.set_index(['Y', 'X']).to_xarray()
        mask = xr.where(~np.isnan(Predictand.isel(T=0)), 1, np.nan)
        Cluster = (dataset['cluster'] * mask)
               
        # Align cluster array with the predictand array
        xarray1, xarray2 = xr.align(Predictand, Cluster, join="outer")
        
        # Identify unique cluster labels
        clusters = np.unique(xarray2)
        clusters = clusters[~np.isnan(clusters)]
        cluster_da = xarray2

        y_train_std = standardize_timeseries(Predictand, clim_year_start, clim_year_end)
        X_train_std['T'] = y_train_std['T']
        # Prepare parameter distributions
        param_dist = {
            'neurons': self.neurons_range,
            'activation': self.activation_options,
            'norm': self.norm_range
        }

        best_params_dict = {}
        for c in clusters: #range(self.n_clusters):
            mask_3d = (cluster_da == c).expand_dims({'T': y_train_std['T']})
            X_stacked_c = X_train_std.where(mask_3d).stack(sample=('T', 'Y', 'X')).transpose('sample', 'M').values
            y_stacked_c = y_train_std.where(mask_3d).stack(sample=('T', 'Y', 'X')).values.ravel()

            nan_mask_c = np.any(~np.isfinite(X_stacked_c), axis=1) | ~np.isfinite(y_stacked_c)
            X_clean_c = X_stacked_c[~nan_mask_c]
            y_clean_c = y_stacked_c[~nan_mask_c]

            if len(X_clean_c) == 0:
                continue

            # Initialize HPELM wrapper for scikit-learn compatibility
            model = HPELMWrapper(random_state=self.random_state)

            # Randomized search
            random_search = RandomizedSearchCV(
                model, param_distributions=param_dist, n_iter=self.n_iter_search,
                cv=self.cv_folds, scoring='neg_mean_squared_error',
                random_state=self.random_state, error_score=np.nan
            )
            random_search.fit(X_clean_c, y_clean_c)
            best_params_dict[c] = random_search.best_params_

        return best_params_dict, cluster_da

    def compute_model(self, X_train, y_train, X_test, y_test, best_params=None, cluster_da=None):
        """
        Compute deterministic hindcast using the HPELM model with injected hyperparameters for each zone.
        Parameters
        ----------
        X_train : xarray.DataArray
            Training predictor data with dimensions (T, M, Y, X).
        y_train : xarray.DataArray
            Training predictand data with dimensions (T, Y, X).
        X_test : xarray.DataArray
            Testing predictor data with dimensions (T, M, Y, X).
        y_test : xarray.DataArray
            Testing predictand data with dimensions (T, Y, X).
        best_params : dict, optional
            Pre-computed best hyperparameters per cluster. If None, computes internally.
        cluster_da : xarray.DataArray, optional
            Pre-computed cluster labels. If None, computes internally.
        Returns
        -------
        predicted_da : xarray.DataArray
            Deterministic hindcast with dimensions (T, Y, X).
        """
        # Standardize inputs
        X_train_std = X_train
        y_train_std = y_train
        X_test_std = X_test
        y_test_std = y_test

        # Extract coordinate variables from X_test
        time = X_test_std['T']
        lat = X_test_std['Y']
        lon = X_test_std['X']
        n_time = len(time)
        n_lat = len(lat)
        n_lon = len(lon)

        # Use provided best_params and cluster_da or compute if None
        if best_params is None:
            best_params, cluster_da = self.compute_hyperparameters(X_train_std, y_train_std, clim_year_start, clim_year_end)

        # Initialize predictions array
        predictions = np.full((n_time, n_lat, n_lon), np.nan)

        self.hpelm = {}  # Dictionary to store models per cluster

        for c in range(self.n_clusters):
            if c not in best_params:
                continue

            bp = best_params[c]

            # Mask for this cluster
            mask_3d_train = (cluster_da == c).expand_dims({'T': X_train_std['T']})
            mask_3d_test = (cluster_da == c).expand_dims({'T': X_test_std['T']})

            # Stack training data for cluster
            X_train_stacked_c = X_train_std.where(mask_3d_train).stack(sample=('T', 'Y', 'X')).transpose('sample', 'M').values
            y_train_stacked_c = y_train_std.where(mask_3d_train).stack(sample=('T', 'Y', 'X')).values.ravel()

            train_nan_mask_c = np.any(~np.isfinite(X_train_stacked_c), axis=1) | ~np.isfinite(y_train_stacked_c)
            X_train_clean_c = X_train_stacked_c[~train_nan_mask_c]
            y_train_clean_c = y_train_stacked_c[~train_nan_mask_c]

            # Stack testing data for cluster
            X_test_stacked_c = X_test_std.where(mask_3d_test).stack(sample=('T', 'Y', 'X')).transpose('sample', 'M').values
            y_test_stacked_c = y_test_std.where(mask_3d_test).stack(sample=('T', 'Y', 'X')).values.ravel()

            test_nan_mask_c = np.any(~np.isfinite(X_test_stacked_c), axis=1) | ~np.isfinite(y_test_stacked_c)
            X_test_clean_c = X_test_stacked_c[~test_nan_mask_c]

            # Initialize and train the HPELM model for this cluster
            hpelm_c = HPELM(
                inputs=X_train_clean_c.shape[1],
                outputs=1,
                classification='r',
                norm=bp['norm']
            )

            # Initialize weights and biases for the neurons
            # Use a random number generator for reproducibility
            # rng = np.random.default_rng(1234)    # isolated RNG
            # n = bp['neurons']
            # W = rng.standard_normal((X_train_clean_c.shape[1], n))
            # B = rng.standard_normal(n)
            # hpelm_c.add_neurons(bp['neurons'], bp['activation'],W=W, B=B)
            
            hpelm_c.add_neurons(bp['neurons'], bp['activation'])
            hpelm_c.train(X_train_clean_c, y_train_clean_c, 'r')
            self.hpelm[c] = hpelm_c

            # Predict
            y_pred_c = hpelm_c.predict(X_test_clean_c).ravel()

            # Reconstruct predictions for this cluster
            full_stacked_c = np.full(len(y_test_stacked_c), np.nan)
            full_stacked_c[~test_nan_mask_c] = y_pred_c
            pred_c_reshaped = full_stacked_c.reshape(n_time, n_lat, n_lon)

            # Fill in the predictions array
            predictions = np.where(np.isnan(predictions), pred_c_reshaped, predictions)

        predicted_da = xr.DataArray(
            data=predictions,
            coords={'T': time, 'Y': lat, 'X': lon},
            dims=['T', 'Y', 'X']
        )
        return predicted_da

    # ------------------ Probability Calculation Methods ------------------
    @staticmethod
    def calculate_tercile_probabilities(best_guess, error_variance, first_tercile, second_tercile, dof):
        """
        Student's t-based method
        """
        n_time = len(best_guess)
        pred_prob = np.empty((3, n_time))
        if np.all(np.isnan(best_guess)):
            pred_prob[:] = np.nan
        else:
            error_std = np.sqrt(error_variance)
            first_t = (first_tercile - best_guess) / error_std
            second_t = (second_tercile - best_guess) / error_std
            pred_prob[0, :] = t.cdf(first_t, df=dof)
            pred_prob[1, :] = t.cdf(second_t, df=dof) - t.cdf(first_t, df=dof)
            pred_prob[2, :] = 1 - t.cdf(second_t, df=dof)
        return pred_prob

    @staticmethod
    def calculate_tercile_probabilities_weibull_min(best_guess, error_variance, first_tercile, second_tercile, dof):
        """
        Weibull minimum-based method.
        """
        n_time = len(best_guess)
        pred_prob = np.empty((3, n_time))
        if np.all(np.isnan(best_guess)):
            pred_prob[:] = np.nan
        else:
            error_std = np.sqrt(error_variance)
            pred_prob[0, :] = weibull_min.cdf(first_tercile, c=dof, loc=best_guess, scale=error_std)
            pred_prob[1, :] = weibull_min.cdf(second_tercile, c=dof, loc=best_guess, scale=error_std) - \
                              weibull_min.cdf(first_tercile, c=dof, loc=best_guess, scale=error_std)
            pred_prob[2, :] = 1 - weibull_min.cdf(second_tercile, c=dof, loc=best_guess, scale=error_std)
        return pred_prob

    @staticmethod
    def calculate_tercile_probabilities_gamma(best_guess, error_variance, T1, T2, dof=None):
        """Gamma-distribution based method."""
        n_time = len(best_guess)
        pred_prob = np.empty((3, n_time), dtype=float)
        if np.any(np.isnan(best_guess)) or np.any(np.isnan(error_variance)):
            pred_prob[:] = np.nan
            return pred_prob
        best_guess = np.asarray(best_guess, dtype=float)
        error_variance = np.asarray(error_variance, dtype=float)
        T1 = np.asarray(T1, dtype=float)
        T2 = np.asarray(T2, dtype=float)
        alpha = (best_guess ** 2) / error_variance
        theta = error_variance / best_guess
        cdf_t1 = gamma.cdf(T1, a=alpha, scale=theta)
        cdf_t2 = gamma.cdf(T2, a=alpha, scale=theta)
        pred_prob[0, :] = cdf_t1
        pred_prob[1, :] = cdf_t2 - cdf_t1
        pred_prob[2, :] = 1.0 - cdf_t2
        return pred_prob

    @staticmethod
    def calculate_tercile_probabilities_nonparametric(best_guess, error_samples, first_tercile, second_tercile):
        """Non-parametric method using historical error samples."""
        n_time = len(best_guess)
        pred_prob = np.full((3, n_time), np.nan, dtype=float)
        for t in range(n_time):
            if np.isnan(best_guess[t]):
                continue
            dist = best_guess[t] + error_samples
            dist = dist[np.isfinite(dist)]
            if len(dist) == 0:
                continue
            p_below = np.mean(dist < first_tercile)
            p_between = np.mean((dist >= first_tercile) & (dist < second_tercile))
            p_above = 1.0 - (p_below + p_between)
            pred_prob[0, t] = p_below
            pred_prob[1, t] = p_between
            pred_prob[2, t] = p_above
        return pred_prob

    @staticmethod
    def calculate_tercile_probabilities_normal(best_guess, error_variance, first_tercile, second_tercile):
        """Normal-distribution based method."""
        n_time = len(best_guess)
        pred_prob = np.empty((3, n_time))
        if np.all(np.isnan(best_guess)):
            pred_prob[:] = np.nan
        else:
            error_std = np.sqrt(error_variance)
            pred_prob[0, :] = norm.cdf(first_tercile, loc=best_guess, scale=error_std)
            pred_prob[1, :] = norm.cdf(second_tercile, loc=best_guess, scale=error_std) - norm.cdf(first_tercile, loc=best_guess, scale=error_std)
            pred_prob[2, :] = 1 - norm.cdf(second_tercile, loc=best_guess, scale=error_std)
        return pred_prob

    @staticmethod
    def calculate_tercile_probabilities_lognormal(best_guess, error_variance, first_tercile, second_tercile):
        """Lognormal-distribution based method."""
        n_time = len(best_guess)
        pred_prob = np.empty((3, n_time))
        if np.any(np.isnan(best_guess)) or np.any(np.isnan(error_variance)):
            pred_prob[:] = np.nan
            return pred_prob
        sigma = np.sqrt(np.log(1 + error_variance / (best_guess ** 2)))
        mu = np.log(best_guess) - sigma ** 2 / 2
        pred_prob[0, :] = lognorm.cdf(first_tercile, s=sigma, scale=np.exp(mu))
        pred_prob[1, :] = lognorm.cdf(second_tercile, s=sigma, scale=np.exp(mu)) - lognorm.cdf(first_tercile, s=sigma, scale=np.exp(mu))
        pred_prob[2, :] = 1 - lognorm.cdf(second_tercile, s=sigma, scale=np.exp(mu))
        return pred_prob

    def compute_prob(self, Predictant, clim_year_start, clim_year_end, hindcast_det):
        """
        Compute tercile probabilities using the chosen distribution method.
        Predictant is expected to be an xarray DataArray with dims (T, Y, X).
        """
        if "M" in Predictant.coords:
            Predictant = Predictant.isel(M=0).drop_vars('M').squeeze()
        mask = xr.where(~np.isnan(Predictant.isel(T=0)), 1, np.nan).drop_vars(['T']).squeeze().to_numpy()
        Predictant = Predictant.transpose('T', 'Y', 'X')
        index_start = Predictant.get_index("T").get_loc(str(clim_year_start)).start
        index_end = Predictant.get_index("T").get_loc(str(clim_year_end)).stop
        rainfall_for_tercile = Predictant.isel(T=slice(index_start, index_end))
        terciles = rainfall_for_tercile.quantile([0.33, 0.67], dim='T')
        error_variance = (Predictant - hindcast_det).var(dim='T')
        dof = len(Predictant.get_index("T")) - 2
        if self.dist_method == "t":
            calc_func = self.calculate_tercile_probabilities
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                hindcast_det,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                kwargs={'dof': dof},
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "weibull_min":
            calc_func = self.calculate_tercile_probabilities_weibull_min
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                hindcast_det,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                kwargs={'dof': dof},
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "gamma":
            calc_func = self.calculate_tercile_probabilities_gamma
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                hindcast_det,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "nonparam":
            calc_func = self.calculate_tercile_probabilities_nonparametric
            error_samples = Predictant - hindcast_det
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                hindcast_det,
                error_samples,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), ('T',), (), ()],
                output_core_dims=[('probability', 'T')],
                vectorize=True,
                dask='parallelized',
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "normal":
            calc_func = self.calculate_tercile_probabilities_normal
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                hindcast_det,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "lognormal":
            calc_func = self.calculate_tercile_probabilities_lognormal
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                hindcast_det,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        else:
            raise ValueError(f"Invalid dist_method: {self.dist_method}.")
        hindcast_prob = hindcast_prob.assign_coords(probability=('probability', ['PB', 'PN', 'PA']))
        return hindcast_prob.transpose('probability', 'T', 'Y', 'X')

    @staticmethod
    def _reshape_and_filter_data(da):
        """
        Helper: stack the DataArray from (T, Y, X[, M]) to (n_samples, n_features)
        and remove rows containing NaNs.
        """
        da_stacked = da.stack(sample=('T', 'Y', 'X'))
        if 'M' in da.dims:
            da_stacked = da_stacked.transpose('sample', 'M')
        else:
            da_stacked = da_stacked.transpose('sample')
        da_values = da_stacked.values
        nan_mask = np.any(np.isnan(da_values), axis=1)
        return da_values[~nan_mask], nan_mask, da_values

    def forecast(self, Predictant, clim_year_start, clim_year_end, hindcast_det, hindcast_det_cross, Predictor_for_year, best_params=None, cluster_da=None):
        """
        Forecast method using a single HPELM model with optimized hyperparameters.
        Parameters
        ----------
        Predictant : xarray.DataArray
            Observed predictand data with dimensions (T, Y, X) or (T, M, Y, X).
        clim_year_start : int or str
            Start year of the climatology period.
        clim_year_end : int or str
            End year of the climatology period.
        hindcast_det : xarray.DataArray
            Deterministic hindcast data for training with dimensions (T, M, Y, X).
        hindcast_det_cross : xarray.DataArray
            Deterministic hindcast data for error estimation with dimensions (T, Y, X).
        Predictor_for_year : xarray.DataArray
            Predictor data for the target year with dimensions (T, M, Y, X).
        best_params : dict, optional
            Pre-computed best hyperparameters. If None, computes internally.
        cluster_da : xarray.DataArray, optional
            Pre-computed cluster labels. If None, computes internally.
        Returns
        -------
        forecast_det : xarray.DataArray
            Deterministic forecast with dimensions (T, Y, X).
        forecast_prob : xarray.DataArray
            Tercile probabilities with dimensions (probability, T, Y, X).
        """
        if "M" in Predictant.coords:
            Predictant_no_m = Predictant.isel(M=0).drop_vars('M').squeeze()
        else:
            Predictant_no_m = Predictant
        mask = xr.where(~np.isnan(Predictant_no_m.isel(T=0)), 1, np.nan).drop_vars(['T']).squeeze().to_numpy()
        # Standardize Predictor_for_year using hindcast climatology
        mean_val = hindcast_det.sel(T=slice(str(clim_year_start), str(clim_year_end))).mean(dim='T')
        std_val = hindcast_det.sel(T=slice(str(clim_year_start), str(clim_year_end))).std(dim='T')
        Predictor_for_year_st = (Predictor_for_year - mean_val) / std_val
        hindcast_det_st = standardize_timeseries(hindcast_det, clim_year_start, clim_year_end)
        Predictant_st = standardize_timeseries(Predictant_no_m, clim_year_start, clim_year_end)
        hindcast_det_st['T'] = Predictant_st['T']
        
        # Extract coordinates from X_test
        time = Predictor_for_year_st['T']
        lat = Predictor_for_year_st['Y']
        lon = Predictor_for_year_st['X']
        n_time = len(time)
        n_lat = len(lat)
        n_lon = len(lon)
        # Use provided best_params and cluster_da or compute if None
        if best_params is None:
            best_params, cluster_da = self.compute_hyperparameters(hindcast_det, Predictant_no_m, clim_year_start, clim_year_end)
        # Initialize predictions array
        predictions = np.full((n_time, n_lat, n_lon), np.nan)
        self.hpelm = {}  # Dictionary to store models per cluster
        for c in range(self.n_clusters):
            if c not in best_params:
                continue
            bp = best_params[c]
            # Mask for this cluster
            mask_3d_train = (cluster_da == c).expand_dims({'T': hindcast_det_st['T']})
            mask_3d_test = (cluster_da == c).expand_dims({'T': Predictor_for_year_st['T']})
            # Stack training data for cluster
            X_train_stacked_c = hindcast_det_st.where(mask_3d_train).stack(sample=('T', 'Y', 'X')).transpose('sample', 'M').values
            y_train_stacked_c = Predictant_st.where(mask_3d_train).stack(sample=('T', 'Y', 'X')).values.ravel()
            train_nan_mask_c = np.any(~np.isfinite(X_train_stacked_c), axis=1) | ~np.isfinite(y_train_stacked_c)
            X_train_clean_c = X_train_stacked_c[~train_nan_mask_c]
            y_train_clean_c = y_train_stacked_c[~train_nan_mask_c]
            # Stack testing data for cluster
            X_test_stacked_c = Predictor_for_year_st.where(mask_3d_test).stack(sample=('T', 'Y', 'X')).transpose('sample', 'M').values
            test_nan_mask_c = np.any(~np.isfinite(X_test_stacked_c), axis=1)
            X_test_clean_c = X_test_stacked_c[~test_nan_mask_c]
            # Initialize and train the HPELM model for this cluster
            hpelm_c = HPELM(
                inputs=X_train_clean_c.shape[1],
                outputs=1,
                classification='r',
                norm=bp['norm']
            )

            # Initialize weights and biases for the neurons
            # Use a random number generator for reproducibility
            # rng = np.random.default_rng(1234)    # isolated RNG
            # n = bp['neurons']
            # W = rng.standard_normal((X_train_clean_c.shape[1], n))
            # B = rng.standard_normal(n)
            # hpelm_c.add_neurons(bp['neurons'], bp['activation'],W=W, B=B)
    
            hpelm_c.add_neurons(bp['neurons'], bp['activation'])
            hpelm_c.train(X_train_clean_c, y_train_clean_c, 'r')
            self.hpelm[c] = hpelm_c
            # Predict
            y_pred_c = hpelm_c.predict(X_test_clean_c).ravel()
            # Reconstruct predictions for this cluster
            full_stacked_c = np.full(X_test_stacked_c.shape[0], np.nan)
            full_stacked_c[~test_nan_mask_c] = y_pred_c
            pred_c_reshaped = full_stacked_c.reshape(n_time, n_lat, n_lon)
            # Fill in the predictions array
            predictions = np.where(np.isnan(predictions), pred_c_reshaped, predictions)
        result_da = xr.DataArray(
            data=predictions,
            coords={'T': time, 'Y': lat, 'X': lon},
            dims=['T', 'Y', 'X']
        ) * mask
        result_da = reverse_standardize(result_da, Predictant_no_m, clim_year_start, clim_year_end)
        year = Predictor_for_year.coords['T'].values.astype('datetime64[Y]').astype(int)[0] + 1970
        T_value_1 = Predictant_no_m.isel(T=0).coords['T'].values
        month_1 = T_value_1.astype('datetime64[M]').astype(int) % 12 + 1
        new_T_value = np.datetime64(f"{year}-{month_1:02d}-01")
        result_da = result_da.assign_coords(T=xr.DataArray([new_T_value], dims=["T"]))
        result_da['T'] = result_da['T'].astype('datetime64[ns]')
        # Compute tercile probabilities
        index_start = Predictant_no_m.get_index("T").get_loc(str(clim_year_start)).start
        index_end = Predictant_no_m.get_index("T").get_loc(str(clim_year_end)).stop
        rainfall_for_tercile = Predictant_no_m.isel(T=slice(index_start, index_end))
        terciles = rainfall_for_tercile.quantile([0.33, 0.67], dim='T')
        error_variance = (Predictant_no_m - hindcast_det_cross).var(dim='T')
        dof = len(Predictant_no_m.get_index("T")) - 2
        if self.dist_method == "t":
            calc_func = self.calculate_tercile_probabilities
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                result_da,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                kwargs={'dof': dof},
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "weibull_min":
            calc_func = self.calculate_tercile_probabilities_weibull_min
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                result_da,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                kwargs={'dof': dof},
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "gamma":
            calc_func = self.calculate_tercile_probabilities_gamma
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                result_da,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "normal":
            calc_func = self.calculate_tercile_probabilities_normal
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                result_da,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "lognormal":
            calc_func = self.calculate_tercile_probabilities_lognormal
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                result_da,
                error_variance,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), (), (), ()],
                vectorize=True,
                dask='parallelized',
                output_core_dims=[('probability', 'T')],
                output_dtypes=['float'],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        elif self.dist_method == "nonparam":
            calc_func = self.calculate_tercile_probabilities_nonparametric
            error_samples = Predictant_no_m - hindcast_det_cross
            error_samples = error_samples.rename({'T': 'S'})
            hindcast_prob = xr.apply_ufunc(
                calc_func,
                result_da,
                error_samples,
                terciles.isel(quantile=0).drop_vars('quantile'),
                terciles.isel(quantile=1).drop_vars('quantile'),
                input_core_dims=[('T',), ('S',), (), ()],
                output_core_dims=[('probability', 'T')],
                vectorize=True,
                dask='parallelized',
                output_dtypes=[float],
                dask_gufunc_kwargs={'output_sizes': {'probability': 3}, 'allow_rechunk': True}
            )
        else:
            raise ValueError(f"Invalid dist_method: {self.dist_method}.")
        hindcast_prob = hindcast_prob.assign_coords(probability=('probability', ['PB', 'PN', 'PA']))
        return result_da * mask, mask * hindcast_prob.transpose('probability', 'T', 'Y', 'X')