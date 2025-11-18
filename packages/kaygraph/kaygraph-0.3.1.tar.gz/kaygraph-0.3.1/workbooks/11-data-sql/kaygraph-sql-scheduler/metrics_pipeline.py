"""
Metrics aggregation pipeline using KayGraph SQL nodes.
Demonstrates hourly metrics calculation and rollup.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, Node
from sql_nodes import SQLNode, BulkInsertNode

logger = logging.getLogger(__name__)


class CalculateHourlyMetricsNode(SQLNode):
    """Calculate hourly aggregated metrics."""

    def __init__(self):
        # Aggregate sales by hour
        query = """
            INSERT INTO hourly_metrics (
                metric_date,
                metric_hour,
                total_sales,
                total_revenue,
                unique_customers,
                avg_order_value,
                created_at
            )
            SELECT
                DATE(sale_date) as metric_date,
                EXTRACT(HOUR FROM sale_date) as metric_hour,
                COUNT(*) as total_sales,
                SUM(quantity * unit_price) as total_revenue,
                COUNT(DISTINCT customer_id) as unique_customers,
                AVG(quantity * unit_price) as avg_order_value,
                NOW() as created_at
            FROM sales
            WHERE sale_date >= %(start_time)s
              AND sale_date < %(end_time)s
              AND status = 'completed'
            GROUP BY DATE(sale_date), EXTRACT(HOUR FROM sale_date)
            ON CONFLICT (metric_date, metric_hour)
            DO UPDATE SET
                total_sales = EXCLUDED.total_sales,
                total_revenue = EXCLUDED.total_revenue,
                unique_customers = EXCLUDED.unique_customers,
                avg_order_value = EXCLUDED.avg_order_value,
                created_at = EXCLUDED.created_at
        """
        super().__init__(
            query=query,
            timeout=180,
            node_id="calculate_hourly_metrics"
        )

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare time range for metrics calculation."""
        # Default to last hour if not specified
        end_time = shared.get("end_time", datetime.utcnow())

        # Calculate window based on metrics_window_hours parameter
        window_hours = shared.get("metrics_window_hours", 24)
        start_time = end_time - timedelta(hours=window_hours)

        shared["metrics_window"] = {
            "start_time": start_time,
            "end_time": end_time,
            "window_hours": window_hours
        }

        return {
            "query": self.query,
            "params": {
                "start_time": start_time,
                "end_time": end_time
            },
            "use_transaction": True,
            "timeout": self.timeout
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Log metrics calculation results."""
        result = exec_res["result"]

        shared["metrics_stats"] = {
            "rows_affected": result["row_count"],
            "window": shared["metrics_window"]
        }

        logger.info(f"Calculated metrics for {result['row_count']} hours")
        return "validate"


class ValidateMetricsNode(SQLNode):
    """Validate metrics calculations for anomalies."""

    def __init__(self):
        # Check for anomalies in the calculated metrics
        query = """
            SELECT
                metric_date,
                metric_hour,
                total_revenue,
                avg_order_value,
                CASE
                    WHEN total_revenue > (
                        SELECT AVG(total_revenue) * 3
                        FROM hourly_metrics
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                    ) THEN 'high_revenue_anomaly'
                    WHEN total_revenue < (
                        SELECT AVG(total_revenue) * 0.3
                        FROM hourly_metrics
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                    ) THEN 'low_revenue_anomaly'
                    ELSE 'normal'
                END as anomaly_type
            FROM hourly_metrics
            WHERE created_at >= %(start_time)s
              AND created_at < %(end_time)s
            ORDER BY metric_date DESC, metric_hour DESC
        """
        super().__init__(
            query=query,
            timeout=60,
            node_id="validate_metrics"
        )

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Use same time window as calculation."""
        window = shared["metrics_window"]

        return {
            "query": self.query,
            "params": {
                "start_time": window["start_time"],
                "end_time": window["end_time"]
            },
            "use_transaction": False,
            "timeout": self.timeout
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Check for anomalies and route accordingly."""
        result = exec_res["result"]

        if result["row_count"] == 0:
            logger.warning("No metrics to validate")
            return None

        # Check for anomalies
        columns = result["columns"]
        rows = result["rows"]

        anomalies = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            if row_dict["anomaly_type"] != "normal":
                anomalies.append(row_dict)

        shared["anomalies"] = anomalies
        shared["anomaly_count"] = len(anomalies)

        if anomalies:
            logger.warning(f"Found {len(anomalies)} anomalies in metrics")
            for anomaly in anomalies[:5]:  # Log first 5
                logger.warning(
                    f"  {anomaly['metric_date']} {anomaly['metric_hour']}:00 - "
                    f"{anomaly['anomaly_type']} (${anomaly['total_revenue']:.2f})"
                )
        else:
            logger.info("All metrics within expected ranges")

        return None  # End of pipeline


def create_metrics_pipeline() -> Graph:
    """
    Create the metrics aggregation pipeline.

    Pipeline flow:
    1. Calculate hourly metrics
    2. Validate for anomalies

    Returns:
        Graph: The configured metrics pipeline
    """
    # Create nodes
    calculate = CalculateHourlyMetricsNode()
    validate = ValidateMetricsNode()

    # Build graph
    calculate >> ("validate", validate)

    graph = Graph(calculate)

    logger.info("Metrics aggregation pipeline created")
    return graph


if __name__ == "__main__":
    # Simple test to verify pipeline structure
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    pipeline = create_metrics_pipeline()

    print("✅ Metrics pipeline created successfully")
    print(f"   Start node: {pipeline.start_node.node_id}")
    print(f"   Total nodes: 2 (calculate_hourly_metrics, validate_metrics)")
    print(f"   Actions: validate")
