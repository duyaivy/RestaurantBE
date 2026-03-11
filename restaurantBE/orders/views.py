from logging import Logger

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from restaurantBE.utils.custom_pagination import CustomPagination
from restaurantBE.utils.permissions import IsAdminOrEmployee
from restaurantBE.utils.responses import apiError
from restaurantBE.utils.responses import apiSuccess
from restaurantBE.constants import OrderItemStatus
from rest_framework.exceptions import ValidationError
from restaurantBE.constants import TableStatus
from restaurantBE.tables.models import Table
from restaurantBE.dishes.models import DishSnapshot, Dish
from restaurantBE.constants import PaymentMethod
from rest_framework.permissions import IsAuthenticated
from restaurantBE.utils.permissions import IsGuest
from restaurantBE.orders.serializers import (
    OrderCreateSerializer,
    OrderItemSerializer,
    OrderUpdateStatusSerializer,
)
from rest_framework import status
from restaurantBE.orders.models import Order, OrderItem
from restaurantBE.orders.serializers import OrderSerializer
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    GenericAPIView,
)
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.http.response import Http404
from restaurantBE.utils.custom_filter import OrderFilter

logger = Logger(__name__)
class OrderListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    pagination_class = CustomPagination
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["created_at", "total_amount"]
    ordering = ["-created_at"]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            try:
                page = self.paginate_queryset(queryset)
            except ValidationError as e:
                return apiError(
                    e.detail,
                    msg=_("invalid_page_number"),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if page is not None:
                serializer = self.get_serializer(page, many=True)

                current_page = self.paginator.page.number
                total_pages = self.paginator.page.paginator.num_pages

                resData = {
                    "count": total_pages,
                    "current": current_page,
                    "results": serializer.data,
                }

                return apiSuccess(resData, msg=_("get_all_order_success"))

            serializer = self.get_serializer(queryset, many=True)
            return apiSuccess(serializer.data, msg=_("get_all_order_success"))

        except Exception as e:
            return apiError(
                None,
                msg=_("get_all_order_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsGuest]
    serializer_class = OrderCreateSerializer

    def post(self, request):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                table_id = serializer.validated_data["table_number_id"]
                items = serializer.validated_data["items"]

                # update status
                table = Table.objects.select_for_update().get(
                    number=table_id
                )  # lock table
                table.status = TableStatus.RESERVED
                table.save()

                # check order item
                dish_ids = [item["dish_id"] for item in items]
                dishes = Dish.objects.filter(id__in=dish_ids)
                if dishes.count() != len(dish_ids):
                    raise ValidationError(_("dish_not_found"))
                # create order

                order = Order.objects.create(
                    guest_id=request.user,
                    table_number_id=table_id,
                    order_handler_id=None,
                    payment_method=PaymentMethod.CASH,
                    total_amount=0,
                )
                total_amount = 0
                # create dish snapshot and order item
                for item in items:
                    dish = dishes.get(id=item["dish_id"])
                    # create dish snapshot
                    dish_snapshot = DishSnapshot.objects.create(
                        dish_id=dish,
                        name=dish.name,
                        price=dish.price,
                        description=dish.description,
                        image=dish.image,
                    )
                    # create order item
                    amount = dish_snapshot.price * item["quantity"]
                    OrderItem.objects.create(
                        order_id=order,
                        dish_snapshot_id=dish_snapshot,
                        quantity=item["quantity"],
                        note=item["note"],
                        item_status=OrderItemStatus.ORDERED,
                        total_amount=amount,
                    )
                    total_amount += amount
                # update total amount
                order.total_amount = total_amount
                order.save()
                response_serializer = OrderSerializer(order)
                return apiSuccess(
                    response_serializer.data,
                    _("order_created"),
                    status.HTTP_201_CREATED,
                )
        except ValidationError:
            raise
        except Exception as e:
            return apiError(
                str(e), msg=_("create_order_error"), status=status.HTTP_400_BAD_REQUEST
            )


class OrderRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            orderDetails = OrderItem.objects.filter(order_id=instance.id)

            data = dict(serializer.data)
            data["items"] = OrderItemSerializer(orderDetails, many=True).data

            return apiSuccess(data, msg=_("get_order_success"))
        except Http404:
            return apiError(
                None, msg=_("order_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return apiError(
                None,
                msg=_("get_order_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            log_data = OrderSerializer(instance).data
            logger.info(f"Deleting order: {log_data}")
            return apiSuccess(None, msg=_("delete_order_success"))
        except Http404:
            return apiError(
                None, msg=_("order_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return apiError(
                None,
                msg=_("delete_order_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return apiSuccess(serializer.data, msg=_("update_order_success"))

            return apiError(
                serializer.errors,
                msg=_("update_order_error"),
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Http404:
            return apiError(
                None, msg=_("order_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return apiError(
                None,
                msg=_("update_order_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderUpdateStatusAPIView(GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateStatusSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                instance.status = serializer.validated_data["status"]
                instance.save()
                response_serializer = OrderSerializer(instance)
                return apiSuccess(
                    response_serializer.data, msg=_("update_order_status_success")
                )

            return apiError(
                serializer.errors,
                msg=_("update_order_status_error"),
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Http404:
            return apiError(
                None, msg=_("order_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return apiError(
                None,
                msg=_("update_order_status_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )
