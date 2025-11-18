"""
Customer behavior summary pipeline using KayGraph SQL nodes.
Demonstrates weekly customer analytics and segmentation.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, Node
from sql_nodes import SQLNode

logger = logging.getLogger(__name__)


class AggregateCustomerBehaviorNode(SQLNode):
    """Aggregate customer behavior metrics for the week."""

    def __init__(self):
        # Calculate weekly customer stats
        query = """
            INSERT INTO customer_weekly_summary (
                customer_id,
                week_start_date,
                total_purchases,
                total_revenue,
                avg_order_value,
                days_active,
                favorite_category,
                customer_segment,
                created_at
            )
            SELECT
                s.customer_id,
                DATE_TRUNC('week', %(week_start)s) as week_start_date,
                COUNT(*) as total_purchases,
                SUM(s.quantity * s.unit_price) as total_revenue,
                AVG(s.quantity * s.unit_price) as avg_order_value,
                COUNT(DISTINCT DATE(s.sale_date)) as days_active,
                (
                    SELECT p.category_id
                    FROM sales s2
                    JOIN products p ON s2.product_id = p.product_id
                    WHERE s2.customer_id = s.customer_id
                      AND s2.sale_date >= %(week_start)s
                      AND s2.sale_date < %(week_end)s
                    GROUP BY p.category_id
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ) as favorite_category,
                c.customer_segment,
                NOW() as created_at
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.sale_date >= %(week_start)s
              AND s.sale_date < %(week_end)s
              AND s.status = 'completed'
            GROUP BY s.customer_id, c.customer_segment
            ON CONFLICT (customer_id, week_start_date)
            DO UPDATE SET
                total_purchases = EXCLUDED.total_purchases,
                total_revenue = EXCLUDED.total_revenue,
                avg_order_value = EXCLUDED.avg_order_value,
                days_active = EXCLUDED.days_active,
                favorite_category = EXCLUDED.favorite_category,
                customer_segment = EXCLUDED.customer_segment,
                created_at = EXCLUDED.created_at
        """
        super().__init__(
            query=query,
            timeout=300,
            node_id="aggregate_customer_behavior"
        )

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare week range for customer analysis."""
        # Default to last week if not specified
        week_offset = shared.get("week_offset", 1)

        # Calculate week boundaries
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday() + (week_offset * 7))
        week_end = week_start + timedelta(days=7)

        shared["customer_week"] = {
            "week_start": week_start,
            "week_end": week_end,
            "week_offset": week_offset
        }

        return {
            "query": self.query,
            "params": {
                "week_start": week_start,
                "week_end": week_end
            },
            "use_transaction": True,
            "timeout": self.timeout
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Log aggregation results."""
        result = exec_res["result"]

        shared["customer_stats"] = {
            "customers_analyzed": result["row_count"],
            "week": shared["customer_week"]
        }

        logger.info(f"Aggregated behavior for {result['row_count']} customers")
        return "segment"


class UpdateCustomerSegmentsNode(SQLNode):
    """Update customer segments based on behavior patterns."""

    def __init__(self):
        # Recalculate customer segments based on recent behavior
        query = """
            UPDATE customers c
            SET
                customer_segment = CASE
                    WHEN recent.total_revenue >= 1000 AND recent.total_purchases >= 10 THEN 'VIP'
                    WHEN recent.total_revenue >= 500 AND recent.total_purchases >= 5 THEN 'Premium'
                    WHEN recent.total_revenue >= 100 AND recent.total_purchases >= 2 THEN 'Regular'
                    WHEN recent.total_purchases = 1 THEN 'New'
                    ELSE 'Inactive'
                END,
                last_segment_update = NOW()
            FROM (
                SELECT
                    customer_id,
                    SUM(total_revenue) as total_revenue,
                    SUM(total_purchases) as total_purchases
                FROM customer_weekly_summary
                WHERE week_start_date >= %(lookback_date)s
                GROUP BY customer_id
            ) recent
            WHERE c.customer_id = recent.customer_id
              AND c.customer_segment != CASE
                    WHEN recent.total_revenue >= 1000 AND recent.total_purchases >= 10 THEN 'VIP'
                    WHEN recent.total_revenue >= 500 AND recent.total_purchases >= 5 THEN 'Premium'
                    WHEN recent.total_revenue >= 100 AND recent.total_purchases >= 2 THEN 'Regular'
                    WHEN recent.total_purchases = 1 THEN 'New'
                    ELSE 'Inactive'
                END
        """
        super().__init__(
            query=query,
            timeout=120,
            node_id="update_customer_segments"
        )

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare lookback period for segmentation."""
        # Look back 8 weeks for segment calculation
        lookback_weeks = 8
        lookback_date = datetime.utcnow().date() - timedelta(weeks=lookback_weeks)

        shared["segmentation_lookback"] = {
            "lookback_date": lookback_date,
            "lookback_weeks": lookback_weeks
        }

        return {
            "query": self.query,
            "params": {
                "lookback_date": lookback_date
            },
            "use_transaction": True,
            "timeout": self.timeout
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Log segment updates."""
        result = exec_res["result"]

        shared["segment_updates"] = {
            "customers_updated": result["row_count"],
            "lookback": shared["segmentation_lookback"]
        }

        logger.info(f"Updated segments for {result['row_count']} customers")
        return "report"


class GenerateCustomerReportNode(SQLNode):
    """Generate summary report of customer segments."""

    def __init__(self):
        # Get segment distribution
        query = """
            SELECT
                customer_segment,
                COUNT(*) as customer_count,
                ROUND(AVG(recent.total_revenue), 2) as avg_revenue,
                ROUND(AVG(recent.total_purchases), 2) as avg_purchases
            FROM customers c
            LEFT JOIN (
                SELECT
                    customer_id,
                    SUM(total_revenue) as total_revenue,
                    SUM(total_purchases) as total_purchases
                FROM customer_weekly_summary
                WHERE week_start_date >= %(lookback_date)s
                GROUP BY customer_id
            ) recent ON c.customer_id = recent.customer_id
            GROUP BY customer_segment
            ORDER BY
                CASE customer_segment
                    WHEN 'VIP' THEN 1
                    WHEN 'Premium' THEN 2
                    WHEN 'Regular' THEN 3
                    WHEN 'New' THEN 4
                    WHEN 'Inactive' THEN 5
                END
        """
        super().__init__(
            query=query,
            timeout=60,
            node_id="generate_customer_report"
        )

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Use same lookback as segmentation."""
        lookback = shared["segmentation_lookback"]

        return {
            "query": self.query,
            "params": {
                "lookback_date": lookback["lookback_date"]
            },
            "use_transaction": False,
            "timeout": self.timeout
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Display customer segment report."""
        result = exec_res["result"]

        if result["row_count"] == 0:
            logger.warning("No customer data for report")
            return None

        # Format report
        columns = result["columns"]
        rows = result["rows"]

        logger.info("\n" + "="*60)
        logger.info("CUSTOMER SEGMENT REPORT")
        logger.info("="*60)

        for row in rows:
            row_dict = dict(zip(columns, row))
            logger.info(
                f"{row_dict['customer_segment']:10s} | "
                f"Count: {row_dict['customer_count']:5d} | "
                f"Avg Revenue: ${row_dict['avg_revenue'] or 0:8.2f} | "
                f"Avg Purchases: {row_dict['avg_purchases'] or 0:5.1f}"
            )

        logger.info("="*60)

        shared["customer_report"] = [
            dict(zip(columns, row)) for row in rows
        ]

        return None  # End of pipeline


def create_customer_pipeline() -> Graph:
    """
    Create the customer behavior summary pipeline.

    Pipeline flow:
    1. Aggregate customer behavior for the week
    2. Update customer segments based on recent activity
    3. Generate summary report

    Returns:
        Graph: The configured customer pipeline
    """
    # Create nodes
    aggregate = AggregateCustomerBehaviorNode()
    segment = UpdateCustomerSegmentsNode()
    report = GenerateCustomerReportNode()

    # Build graph
    aggregate >> ("segment", segment)
    segment >> ("report", report)

    graph = Graph(aggregate)

    logger.info("Customer behavior pipeline created")
    return graph


if __name__ == "__main__":
    # Simple test to verify pipeline structure
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    pipeline = create_customer_pipeline()

    print("✅ Customer pipeline created successfully")
    print(f"   Start node: {pipeline.start_node.node_id}")
    print(f"   Total nodes: 3 (aggregate_customer_behavior, update_customer_segments, generate_customer_report)")
    print(f"   Actions: segment -> report")
