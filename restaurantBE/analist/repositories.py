"""
Analytics Repository
Repository pattern: tập trung toàn bộ raw SQL queries cho analytics.
View không được import django.db.connection trực tiếp.
"""

from typing import Any, Dict, List
from django.db import connection


class AnalyticsRepository:
    """
    Repository pattern: tập trung toàn bộ raw SQL queries cho analytics.
    View không được import django.db.connection trực tiếp.
    """

    @staticmethod
    def get_summary_stats(from_dt, to_dt) -> Dict[str, Any]:
        """
        Trả về dict với keys: revenue, guest, tables_reserving, total_tables, orders.
        Lấy từ raw SQL query (giữ nguyên SQL logic hiện tại).
        """
        raw_query_stats = """
            SELECT
                COALESCE(SUM(o.total_amount), 0) AS revenue,
                COALESCE(COUNT(o.guest_id_id), 0) AS guest,
                (
                    SELECT COUNT(t.number)
                    FROM "Table" t
                    WHERE t.status = 'RESERVED'
                ) AS tables_reserving,
                (
                    SELECT COUNT(t.number)
                    FROM "Table" t
                ) AS total_tables,
                COUNT(o.id) AS orders
            FROM orders o
            WHERE o.status = 'COMPLETED'
                AND o.created_at >= %s
                AND o.created_at < %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(raw_query_stats, [from_dt, to_dt])
            stats_row = cursor.fetchone()

        return {
            "revenue": stats_row[0] if stats_row else 0,
            "guest": stats_row[1] if stats_row else 0,
            "tables_reserving": stats_row[2] if stats_row else 0,
            "total_tables": stats_row[3] if stats_row else 0,
            "orders": stats_row[4] if stats_row else 0,
        }

    @staticmethod
    def get_top_dishes(from_dt, to_dt, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Trả về list[{"dish_id": int, "dish_name": dict, "total_quantity": int}].
        """
        raw_query_top_tier_dishes = """
            SELECT
                d.id,
                d.name,
                SUM(oi.quantity) AS total_quantity
            FROM orders o
            JOIN order_items oi
                ON oi.order_id_id = o.id
            JOIN dish_snapshot ds
                ON ds.id = oi.dish_snapshot_id_id
            JOIN dish d
                ON d.id = ds.dish_id_id
            WHERE o.created_at >= %s
              AND o.created_at < %s
              AND oi.item_status = 'SERVED'
            GROUP BY d.id, d.name
            ORDER BY total_quantity DESC
            LIMIT %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(raw_query_top_tier_dishes, [from_dt, to_dt, limit])
            top_tier_dishes = cursor.fetchall()

        return [
            {
                "dish_id": row[0],
                "dish_name": row[1],
                "total_quantity": row[2],
            }
            for row in top_tier_dishes
        ]

    @staticmethod
    def get_revenue_chart(from_dt, to_dt) -> List[Dict[str, Any]]:
        """
        Trả về list[{"date": str, "revenue": Decimal}] theo từng ngày.
        """
        raw_query_revenue_chart = """
            WITH date_range AS (
                SELECT generate_series(
                    DATE(%s),
                    DATE(%s),
                    INTERVAL '1 day'
                )::date AS revenue_date
            )
            SELECT
                dr.revenue_date,
                COALESCE(SUM(o.total_amount), 0) AS total_revenue
            FROM date_range dr
            LEFT JOIN orders o
                ON DATE(o.created_at) = dr.revenue_date
               AND o.status = 'COMPLETED'
            GROUP BY dr.revenue_date
            ORDER BY dr.revenue_date ASC;
        """
        with connection.cursor() as cursor:
            cursor.execute(raw_query_revenue_chart, [from_dt, to_dt])
            revenue_chart_rows = cursor.fetchall()

        return [
            {
                "date": row[0].strftime("%d-%m") if row[0] else None,
                "revenue": row[1],
            }
            for row in revenue_chart_rows
        ]
