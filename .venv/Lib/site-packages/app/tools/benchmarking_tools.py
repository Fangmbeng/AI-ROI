from app.models.benchmark import BenchmarkResult

def generate_benchmark_comparisons() -> list[BenchmarkResult]:
    return [
        BenchmarkResult(
            benchmark_type="Model",
            entity_name="Churn Model v2",
            baseline_name="Industry Avg",
            performance_score=0.89,
            baseline_score=0.86,
            metric="Accuracy",
            score_unit="score",
            deviation=3.49,
            comment="Model outperforms industry average by ~3.5%"
        ),
        BenchmarkResult(
            benchmark_type="Infra",
            entity_name="us-central1",
            baseline_name="europe-west1",
            performance_score=1.12,
            baseline_score=1.00,
            metric="Cost per Inference",
            score_unit="USD",
            deviation=12.0,
            comment="us-central1 is 12% more expensive than europe-west1"
        ),
        BenchmarkResult(
            benchmark_type="Cost",
            entity_name="GKE Training Pipeline",
            baseline_name="Q1 Internal Target",
            performance_score=18250,
            baseline_score=15000,
            metric="Monthly Cost",
            score_unit="USD",
            deviation=21.7,
            comment="Cost exceeded target due to prolonged pipeline duration"
        )
    ]
