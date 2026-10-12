"""
Analist Views
Handles: Analytics reporting endpoints.
"""

from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from restaurantBE.analist.repositories import AnalyticsRepository
from restaurantBE.analist.serializers import AnalistDateRangeSerializer
from restaurantBE.utils.permissions import IsAdminOrEmployee
from restaurantBE.utils.responses import apiSuccess


class AnalistPingAPIView(APIView):
    permission_classes = [IsAdminOrEmployee]

    def get(self, request):
        serializer = AnalistDateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        from_dt = serializer.validated_data["from_datetime"]
        to_dt = serializer.validated_data["to"]

        stats = AnalyticsRepository.get_summary_stats(from_dt, to_dt)
        top_dishes = AnalyticsRepository.get_top_dishes(from_dt, to_dt)
        revenue_chart = AnalyticsRepository.get_revenue_chart(from_dt, to_dt)

        return apiSuccess(
            {
                "stats": stats,
                "top_dishes": top_dishes,
                "revenue_chart": revenue_chart,
            },
            _("analist_ping_success"),
        )
