from app.models.performance_correlation import CorrelationInsight

def correlate_cost_with_business_value() -> list[CorrelationInsight]:
    return [
        CorrelationInsight(
            workload="Fraud Detection Pipeline",
            model_id="xgboost-4512",
            cost=70000,
            kpi_impact_score=0.85,
            roi_score=91.5,
            comment="High ROI - strong contribution to reduced churn and fraud loss."
        ),
        CorrelationInsight(
            workload="Customer Chatbot NLP",
            model_id="gpt3-turbo-1441",
            cost=95000,
            kpi_impact_score=0.30,
            roi_score=22.0,
            comment="Moderate ROI - improves CSAT but costly to run."
        ),
        CorrelationInsight(
            workload="Personalized Banner Recommender",
            model_id="bert-embedder-0978",
            cost=56000,
            kpi_impact_score=-0.20,
            roi_score=-35.0,
            comment="Negative ROI - high infra usage with low impact on conversion rate."
        )
    ]
