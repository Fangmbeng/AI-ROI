from app.models.optimization_recommendation import OptimizationRecommendation
from app.tools.correlation_tools import correlate_cost_with_business_value

def generate_optimization_recommendations() -> list[OptimizationRecommendation]:
    insights = correlate_cost_with_business_value()
    recommendations = []

    for insight in insights:
        if insight.roi_score > 75:
            recommendations.append(OptimizationRecommendation(
                workload=insight.workload,
                model_id=insight.model_id,
                action="Scale Up",
                expected_impact="Increased revenue and user engagement",
                rationale=f"High ROI score ({insight.roi_score}). Scaling up can enhance KPI impact."
            ))
        elif insight.roi_score < -20:
            recommendations.append(OptimizationRecommendation(
                workload=insight.workload,
                model_id=insight.model_id,
                action="Decommission",
                expected_impact="Reduced cloud spending with minimal KPI loss",
                rationale=f"Negative ROI ({insight.roi_score}). Model is underperforming with high cost."
            ))
        else:
            recommendations.append(OptimizationRecommendation(
                workload=insight.workload,
                model_id=insight.model_id,
                action="Monitor and Optimize",
                expected_impact="Maintain moderate performance while reducing cost",
                rationale=f"Moderate ROI ({insight.roi_score}). Worth optimizing but not scaling aggressively."
            ))

    return recommendations
