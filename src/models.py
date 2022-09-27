from typing import List
from ngboost import NGBRegressor
from sklearn.tree import DecisionTreeRegressor
import pandas as pd
import numpy as np
from sklearn.utils import check_array
#from sklearn.datasets import fetch_california_housing
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_squared_error
#from sklearn.model_selection import cross_val_predict

class RONGBA(NGBRegressor):
    """Subclass of NGBRegressor that uses predefined parameter set (RONGBA).

    Returns:
        RONGBA object that can be fit.
    """

    def __init__(self) -> None:
        base = DecisionTreeRegressor(
            criterion="friedman_mse",
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.0,
            max_leaf_nodes=75,
            splitter="best",
            random_state=42,
            max_depth=10,
        )
        super().__init__(
            Base=base,
            random_state=42,
            learning_rate=0.01,
            n_estimators=1000,
            verbose_eval=100,
        )

    def pred_dist_compat(self, X: np.array, max_iter: int = None) -> np.array:
        """Utility function that provides sklearn compatible predictions for use in
        cross_val_predict().

        Args:
            X (np.array): Input data to predict on.
            max_iter (int, optional): Iteration flag for staged prediction. Defaults to None.

        Returns:
            np.array: (N, 2) shaped array of mean, sd predictions
        """
        X = check_array(X, accept_sparse=True)

        if max_iter is not None:
            dist = self.staged_pred_dist(X, max_iter=max_iter)[-1]
        else:
            params = np.asarray(self.pred_param(X, max_iter))
            dist = self.Dist(params.T)

        return np.vstack((dist.params["loc"], dist.params["scale"])).T

    def pred_frame(
        self,
        X: np.array,
        with_X: bool = False,
        y: np.array = None,
        features: List = None,
    ) -> pd.DataFrame:
        """Utility prediction function that returns a dataframe of predictions (mean and sd) that includes
        optional X and y values.

        Args:
            X (np.array):  Input data to predict on.
            with_X (Boolean, optional): Inlcude predictions and X in dataframe result. Defaults to False.
            y (np.array, optional): Y value to include in dataframe result. Defaults to None.
            features (List, optional): List of column names for X. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe with predictions and corresponding X and/or y values.
        """
        prediction_dict = self.pred_dist(X)

        if with_X:
            prediction_frame = pd.DataFrame(X, columns=features)
            prediction_frame["mean"] = prediction_dict.loc[0:]
            prediction_frame["sd"] = prediction_dict.scale[0:]

        else:
            prediction_frame = pd.DataFrame(
                {"mean": prediction_dict.loc[0:], "sd": prediction_dict.scale[0:]}
            )
        if y is not None:
            prediction_frame["actual"] = y

        return prediction_frame