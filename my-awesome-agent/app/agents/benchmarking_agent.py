# app/agents/benchmarking_agent.py

from typing import List
from datetime import datetime
from google.adk.agents import LlmAgent
from app.models.benchmark import BenchmarkResult
from app.services.bigquery_service import BigQueryService
from app.services.vertex_ai_service import VertexAIService
from app.utils.config import PlatformConfig

class BenchmarkingAgent(LlmAgent):
    def __init__(
        self,
        config: PlatformConfig,
        bq_service: BigQueryService,
        vertex_service: VertexAIService
    ):
        # Call parent constructor first
        super().__init__(
            name="benchmarking_agent",
            model="gemini-2.0-flash",
            description="Benchmarks AI workloads vs. industry or internal baselines",
            tools=[self.benchmark_ai_systems],
        )
        
        # Initialize services using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, '_bq', bq_service)
        object.__setattr__(self, '_vertex', vertex_service)
        object.__setattr__(self, '_config', config)

    @property
    def bq(self):
        return self._bq

    @property
    def vertex(self):
        return self._vertex

    @property
    def config(self):
        return self._config

    def benchmark_ai_systems(self) -> List[BenchmarkResult]:
        # 1) Possibly fetch past performance from BigQuery
        # (omitted for brevity)

        # 2) Generate benchmarks via service
        benchmarks = self.vertex.generate_benchmark_comparisons()

        # 3) Transform + persist
        results: List[BenchmarkResult] = []
        rows = []
        ts = datetime.utcnow().isoformat()
        for b in benchmarks:
            bm = BenchmarkResult(**b)
            results.append(bm)
            rows.append({
                "timestamp": ts,
                "benchmark_type": bm.benchmark_type,
                "entity_name": bm.entity_name,
                "baseline_name": bm.baseline_name,
                "performance_score": bm.performance_score,
                "baseline_score": bm.baseline_score,
                "metric": bm.metric,
                "score_unit": bm.score_unit,
                "deviation": bm.deviation,
                "comment": bm.comment,
            })
        self.bq.insert_rows("benchmarks", rows)
        return results