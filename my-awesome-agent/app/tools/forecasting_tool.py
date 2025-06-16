from app.models.forecast import Forecast

def generate_forecasts() -> list[Forecast]:
    return [
        Forecast(
            category="Cost",
            metric_name="Vertex GPU Costs",
            forecast_value=15320.75,
            unit="USD",
            prediction_horizon="next 30 days",
            confidence_interval="95%",
            insights="GPU costs expected to increase by 25% due to planned model training jobs"
        ),
        Forecast(
            category="KPI",
            metric_name="Model Accuracy (Churn Predictor)",
            forecast_value=0.91,
            unit="accuracy score",
            prediction_horizon="next 14 days",
            confidence_interval="90%",
            insights="Retraining expected to improve accuracy based on customer segment shifts"
        ),
        Forecast(
            category="Usage",
            metric_name="Prediction API Calls",
            forecast_value=320000,
            unit="calls/day",
            prediction_horizon="next 7 days",
            confidence_interval="85%",
            insights="Spike expected due to upcoming product launch campaign"
        )
    ]
