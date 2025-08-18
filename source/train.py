import duckdb
import pathlib
import lightgbm as lgb
import sklearn
import numpy as np
import os
import mlflow

data_path = pathlib.Path(__file__).parents[1] / "data"
MLFLOW_TRACKING_URL = os.getenv("MLFLOW_URL")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URL)
mlflow.set_experiment("electric-demand-prediction")

def smape(
    true_yields: np.ndarray,
    predicted_yields: np.ndarray
) -> np.ndarray:
    
    v = (
        2 * np.abs(predicted_yields - true_yields)
        / (np.abs(predicted_yields) + np.abs(true_yields))
    )
    score = np.mean(v) * 100
    return score

query = f"""
    SELECT
        building_type,
        temperature_celsius,
        rainfall_mm,
        windspeed_mps,
        humidity_percent,
        sunshine_hour,
        solar_radiation_wpm2,
        solar_panel_capacity_kw,
        ess_storage_capacity_kwh,
        pcs_capacity_kw,
        cos_hour,
        sin_hour,
        cos_month,
        sin_month,
        cos_week,
        sin_week,
        cooling_area_ratio,
        power_consumption_kwh
    FROM '{str(data_path / "preprocessed_data.parquet")}'
"""

data_frame = duckdb.query(query).to_df()

target_column = ["power_consumption_kwh"]

X = data_frame.drop(columns=target_column)
y = data_frame[target_column]

X_train, X_test, y_train, y_test = (
    sklearn.model_selection.train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )
)

params = {
    "categorical_feature": 0,
    
}

with mlflow.start_run():
    mlflow.log_params(params)
    model = lgb.LGBMRegressor(**params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mlflow.lightgbm.log_model(
        lgb_model=model,
        input_example=X_train,
    )

    mlflow.log_metrics({
            "smape": smape(y_test, y_pred)
        })

print(smape(y_test, y_pred))