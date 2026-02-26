from django.http.response import Http404
from restaurantBE.utils.random import RandomUtils
from restaurantBE.utils.responses import apiError, apiSuccess
from rest_framework import status
from restaurantBE.utils.permissions import IsAdminOrEmployee
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateDestroyAPIView
from restaurantBE.tables.models import Table
from restaurantBE.tables.serializers import TableSerializer
import logging
from django.utils.translation import gettext_lazy as _
logger = logging.getLogger(__name__)

class TableRetrieveListAPIView(RetrieveAPIView):
    queryset = Table.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = 'number'
    lookup_url_kwarg = 'number'
    serializer_class = TableSerializer
    def get(self, request, *args, **kwargs):
        data = self.get_queryset().all()
        serializer = self.get_serializer(data, many=True)
        return apiSuccess(serializer.data,msg=_("get_all_table_success"))

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        logger.info(serializer)
        if serializer.is_valid():
            # Create table
            table = serializer.save()
            
            # Generate and set token
            token = RandomUtils.generateToken()
            table.token = token
            table.save()
            
            # Serialize full table object to return all fields
            response_serializer = TableSerializer(table)
            return apiSuccess(response_serializer.data, msg=_("create_table_success"))
        
        return apiError(serializer.errors, msg=_("create_table_error"), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
class TableRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = 'number'
    lookup_url_kwarg = 'number'

    def retrieve(self, request, *args, **kwargs):
        try: 
            instance = self.get_object()
        except Http404:
            return apiError(None, msg=_("table_not_found"), status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return apiSuccess(serializer.data,msg=_("get_table_success"))
    def destroy(self, request, *args, **kwargs):
        try: 
            instance = self.get_object()
        except Http404:
            return apiError(None, msg=_("table_not_found"), status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return apiSuccess(None, msg=_("delete_table_success"))
    def update(self, request, *args, **kwargs):
        try: 
            instance = self.get_object()
        except Http404:
            return apiError(None, msg=_("table_not_found"), status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return apiSuccess(serializer.data, msg=_("update_table_success"))
        return apiError(serializer.errors, msg=_("update_table_error"), status=status.HTTP_422_UNPROCESSABLE_ENTITY)