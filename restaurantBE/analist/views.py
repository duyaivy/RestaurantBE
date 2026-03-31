from django.db import connection
from rest_framework.views import APIView

from restaurantBE.analist.serializers import AnalistDateRangeSerializer
from restaurantBE.utils.permissions import IsAdminOrEmployee
from restaurantBE.utils.responses import apiSuccess
from django.utils.translation import gettext_lazy as _


class AnalistPingAPIView(APIView):
    permission_classes = [IsAdminOrEmployee]

    def get(self, request):

        serializer = AnalistDateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        from_datetime = serializer.validated_data["from_datetime"]
        to_datetime = serializer.validated_data["to"]

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
            LIMIT 5;
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
            cursor.execute(raw_query_stats, [from_datetime, to_datetime])
            stats_row = cursor.fetchone()

            cursor.execute(raw_query_top_tier_dishes, [from_datetime, to_datetime])
            top_tier_dishes = cursor.fetchall()

            cursor.execute(raw_query_revenue_chart, [from_datetime, to_datetime])
            revenue_chart_rows = cursor.fetchall()

        stats = {
            "revenue": stats_row[0],
            "guest": stats_row[1],
            "tables_reserving": stats_row[2],
            "total_tables": stats_row[3],
            "orders": stats_row[4],
        }
        top_dishes = [
            {
                "dish_id": row[0],
                "dish_name": row[1],
                "total_quantity": row[2],
            }
            for row in top_tier_dishes
        ]
        revenue_chart = [
            {
                "date": row[0].strftime("%d-%m") if row[0] else None,
                "revenue": row[1],
            }
            for row in revenue_chart_rows
        ]

        return apiSuccess(
            {
                "stats": stats,
                "top_dishes": top_dishes,
                "revenue_chart": revenue_chart,
            },
            _("analist_ping_success"),
        )
