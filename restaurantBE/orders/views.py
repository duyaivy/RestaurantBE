from restaurantBE.settings.common import VNPAY_ORDER_TYPE
from restaurantBE.settings.common import VNPAY_RETURN_URL
from restaurantBE.settings.common import VNPAY_PAYMENT_URL
from restaurantBE.settings.common import VNPAY_HASH_SECRET
from restaurantBE.settings.common import CLIENT_URL
from restaurantBE.orders.vnpay import get_client_ip
from restaurantBE.settings.common import VNPAY_TMN_CODE
import logging
from urllib.parse import urlencode

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from restaurantBE.constants.choices import OrderStatus
from restaurantBE.utils.custom_pagination import CustomPagination
from restaurantBE.utils.permissions import IsAdminOrEmployee
from restaurantBE.utils.responses import apiError
from restaurantBE.utils.responses import apiSuccess
from restaurantBE.constants import OrderItemStatus
from rest_framework.exceptions import ValidationError
from restaurantBE.constants import TableStatus
from restaurantBE.tables.models import Table
from restaurantBE.guests.models import Guest
from restaurantBE.dishes.models import DishSnapshot, Dish
from restaurantBE.constants import PaymentMethod
from rest_framework.permissions import IsAuthenticated
from restaurantBE.utils.permissions import IsGuest
from restaurantBE.orders.serializers import (
    OrderCreateSerializer,
    OrderStaffCreateSerializer,
    OrderItemSerializer,
    OrderUpdateStatusSerializer,
    OrderUpdateSerializer,
    OrderItemsUpdateSerializer,
    OrderCreatePaymentSerializer,
)
from rest_framework import status
from restaurantBE.orders.models import Order, OrderItem
from restaurantBE.orders.serializers import OrderSerializer
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveDestroyAPIView,
    GenericAPIView,
)
from django.utils.translation import gettext as _
from django.db import transaction, models
from django.http.response import Http404
from django.http import HttpResponseRedirect
from restaurantBE.utils.custom_filter import OrderFilter
from restaurantBE.orders.vnpay import VNPAY
from datetime import datetime

logger = logging.getLogger(__name__)


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


class OrderStaffCreateAPIView(CreateAPIView):
    """API for staff/employee to create order for guest"""

    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    serializer_class = OrderStaffCreateSerializer

    def post(self, request):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                guest_id = serializer.validated_data["guest_id"]
                table_id = serializer.validated_data["table_number_id"]
                items = serializer.validated_data["items"]

                # Get guest instance
                guest = Guest.objects.get(id=guest_id)

                # Update table status
                table = Table.objects.select_for_update().get(
                    number=table_id
                )  # lock table
                table.status = TableStatus.RESERVED
                table.save()

                # Check order items
                dish_ids = [item["dish_id"] for item in items]
                dishes = Dish.objects.filter(id__in=dish_ids)
                if dishes.count() != len(dish_ids):
                    raise ValidationError(_("dish_not_found"))

                # Create order with staff as order_handler
                order = Order.objects.create(
                    guest_id=guest,
                    table_number_id=table_id,
                    order_handler_id=request.user,  # Staff creating the order
                    payment_method=PaymentMethod.CASH,
                    total_amount=0,
                )

                total_amount = 0
                # Create dish snapshot and order items
                for item in items:
                    dish = dishes.get(id=item["dish_id"])

                    # Create dish snapshot
                    dish_snapshot = DishSnapshot.objects.create(
                        dish_id=dish,
                        name=dish.name,
                        price=dish.price,
                        description=dish.description,
                        image=dish.image,
                    )

                    # Create order item
                    amount = dish_snapshot.price * item["quantity"]
                    OrderItem.objects.create(
                        order_id=order,
                        dish_snapshot_id=dish_snapshot,
                        quantity=item["quantity"],
                        note=item.get("note", ""),
                        item_status=OrderItemStatus.ORDERED,
                        total_amount=amount,
                    )
                    total_amount += amount

                # Update total amount
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
        except Guest.DoesNotExist:
            return apiError(
                None, msg=_("guest_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return apiError(
                str(e), msg=_("create_order_error"), status=status.HTTP_400_BAD_REQUEST
            )


class OrderRetrieveDestroyAPIView(RetrieveDestroyAPIView):
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
            if instance.status == OrderStatus.CANCELLED:
                return apiError(
                    None,
                    msg=_("order_already_cancelled"),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance.status = OrderStatus.CANCELLED
            instance.save()
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


class OrderUpdateStatusAPIView(GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateStatusSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                data=request.data, context={"instance": instance}
            )

            if serializer.is_valid():
                instance.status = serializer.validated_data["status"]
                instance.save()
                if instance.status == OrderStatus.COMPLETED:
                    table = Table.objects.get(number=instance.table_number_id)
                    table.status = TableStatus.AVAILABLE
                    table.save()
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


class OrderUpdateAPIView(GenericAPIView):
    """API để update order - các trường: status, payment_method, table_number, order_handler_id"""

    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            # Validate order chưa bị cancelled hoặc completed
            if instance.status in [OrderStatus.CANCELLED, OrderStatus.COMPLETED]:
                return apiError(
                    None,
                    msg=_("cannot_update_cancelled_or_completed_order"),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                # Trả về response đầy đủ với items
                response_serializer = OrderSerializer(instance)
                order_items = OrderItem.objects.filter(order_id=instance.id)

                data = dict(response_serializer.data)
                data["items"] = OrderItemSerializer(order_items, many=True).data

                return apiSuccess(data, msg=_("update_order_success"))

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
                str(e),
                msg=_("update_order_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderUpdateItemsAPIView(GenericAPIView):
    """API để thêm/cập nhật/xóa dishes trong order

    Request body:
    {
        "add_items": [
            {"dish_id": 1, "quantity": 2, "note": "Không hành"},
            {"dish_id": 3, "quantity": 1}
        ],
        "update_items": [
            {"order_item_id": 5, "quantity": 3, "note": "Thêm hành"},
            {"order_item_id": 7, "quantity": 1}
        ],
        "cancel_item_ids": [10, 12]
    }
    """

    queryset = Order.objects.all()
    serializer_class = OrderItemsUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                order = self.get_object()

                # Validate order chưa bị cancelled hoặc completed
                if order.status in [OrderStatus.CANCELLED, OrderStatus.COMPLETED]:
                    return apiError(
                        None,
                        msg=_("cannot_update_cancelled_or_completed_order"),
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Validate request data
                serializer = self.get_serializer(
                    data=request.data, context={"order_id": order.id}
                )

                if not serializer.is_valid():
                    return apiError(
                        serializer.errors,
                        msg=_("invalid_request_data"),
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )

                validated_data = serializer.validated_data
                add_items = validated_data.get("add_items", [])
                update_items = validated_data.get("update_items", [])
                cancel_item_ids = validated_data.get("cancel_item_ids", [])

                # Xử lý cancel items
                if cancel_item_ids:
                    cancelled_count = OrderItem.objects.filter(
                        id__in=cancel_item_ids, order_id=order
                    ).update(item_status=OrderItemStatus.CANCELLED)

                    logger.info(
                        f"Cancelled {cancelled_count} items for order {order.id}"
                    )

                # Xử lý update items
                updated_items = []
                if update_items:
                    for item_data in update_items:
                        order_item = OrderItem.objects.select_for_update().get(
                            id=item_data["order_item_id"], order_id=order
                        )

                        # Update quantity và note
                        order_item.quantity = item_data["quantity"]
                        if "note" in item_data:
                            order_item.note = item_data["note"]

                        # Recalculate total_amount
                        order_item.total_amount = (
                            order_item.dish_snapshot_id.price * order_item.quantity
                        )
                        order_item.save()
                        updated_items.append(order_item)

                    logger.info(
                        f"Updated {len(updated_items)} items for order {order.id}"
                    )

                # Xử lý add items
                added_items = []
                if add_items:
                    dish_ids = [item["dish_id"] for item in add_items]
                    dishes = Dish.objects.filter(id__in=dish_ids)

                    # Tạo dict để lookup nhanh
                    dishes_dict = {dish.id: dish for dish in dishes}

                    for item_data in add_items:
                        dish = dishes_dict.get(item_data["dish_id"])
                        if not dish:
                            continue

                        # Tạo DishSnapshot
                        dish_snapshot = DishSnapshot.objects.create(
                            dish_id=dish,
                            name=dish.name,
                            price=dish.price,
                            description=dish.description,
                            image=dish.image,
                        )

                        # Tạo OrderItem
                        quantity = item_data["quantity"]
                        total_amount = dish_snapshot.price * quantity

                        order_item = OrderItem.objects.create(
                            order_id=order,
                            dish_snapshot_id=dish_snapshot,
                            quantity=quantity,
                            note=item_data.get("note", ""),
                            item_status=OrderItemStatus.ORDERED,
                            total_amount=total_amount,
                        )
                        added_items.append(order_item)

                    logger.info(f"Added {len(added_items)} items to order {order.id}")

                # Recalculate total_amount của order
                # Chỉ tính các items chưa bị cancel
                total_amount = (
                    OrderItem.objects.filter(order_id=order)
                    .exclude(item_status=OrderItemStatus.CANCELLED)
                    .aggregate(total=models.Sum("total_amount"))["total"]
                    or 0
                )

                order.total_amount = total_amount
                order.save()

                # Prepare response
                order_serializer = OrderSerializer(order)
                order_items = OrderItem.objects.filter(order_id=order.id)

                response_data = dict(order_serializer.data)
                response_data["items"] = OrderItemSerializer(
                    order_items, many=True
                ).data
                response_data["summary"] = {
                    "added_count": len(added_items),
                    "updated_count": len(updated_items),
                    "cancelled_count": len(cancel_item_ids),
                }

                return apiSuccess(response_data, msg=_("update_order_items_success"))

        except Http404:
            return apiError(
                None, msg=_("order_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return apiError(
                str(e),
                msg=_("validation_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error updating order items: {str(e)}")
            return apiError(
                str(e),
                msg=_("update_order_items_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderCreatePaymentView(GenericAPIView):
    serializer_class = OrderCreatePaymentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return apiError(
                serializer.errors,
                msg=_("invalid_request_data"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        paymentMethod = request.data.get("payment_method")
        order_id = self.kwargs["pk"]
        order = Order.objects.get(pk=order_id)

        # save payment method
        order.payment_method = paymentMethod
        order.save()

        # data for vnpay
        order_type = VNPAY_ORDER_TYPE
        order_id = order.id
        amount = int(order.total_amount)
        order_desc = _("order_desc") + str(order_id)
        vnp_txn_ref = f"{order_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        language = request.headers.get("language")
        ipaddr = get_client_ip(request)
        # Build URL Payment
        vnp = VNPAY()
        vnp.requestData["vnp_Version"] = "2.1.0"
        vnp.requestData["vnp_Command"] = "pay"
        vnp.requestData["vnp_TmnCode"] = VNPAY_TMN_CODE
        vnp.requestData["vnp_Amount"] = amount * 100
        vnp.requestData["vnp_CurrCode"] = "VND"
        vnp.requestData["vnp_TxnRef"] = vnp_txn_ref
        vnp.requestData["vnp_OrderInfo"] = order_desc
        vnp.requestData["vnp_OrderType"] = order_type
        # Check language, default: vn
        if language and language != "":
            vnp.requestData["vnp_Locale"] = language
        else:
            vnp.requestData["vnp_Locale"] = "vn"

        vnp.requestData["vnp_CreateDate"] = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )  # 20150410063022
        vnp.requestData["vnp_IpAddr"] = ipaddr
        vnp.requestData["vnp_ReturnUrl"] = VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET)
        # print(vnpay_payment_url)

        if paymentMethod == PaymentMethod.QR_CODE:
            return apiSuccess(
                {"url": vnpay_payment_url}, msg=_("order_qr_code_create_url_success")
            )
        else:
            return apiSuccess(None, msg=_("order_cash_create_success"))


class VerifyOrderVNpayView(GenericAPIView):
    def _redirect_client(self, payment_status, order_id=None, code=None):
        query_data = {"payment_status": payment_status}
        if order_id:
            query_data["order_id"] = order_id
        if code:
            query_data["code"] = code

        separator = "&" if "?" in CLIENT_URL else "?"
        return HttpResponseRedirect(f"{CLIENT_URL}{separator}{urlencode(query_data)}")

    def get(self, request):
        input_data = request.GET

        if not input_data:
            # return JsonResponse({"RspCode": "99", "Message": "Invalid request"})
            return self._redirect_client("invalid")

        try:
            vnp = VNPAY()
            vnp.responseData = input_data.dict()

            txn_ref = input_data.get("vnp_TxnRef")
            response_code = input_data.get("vnp_ResponseCode")

            order_id = txn_ref.split("-")[0] if txn_ref else None

            if not order_id:
                # return JsonResponse({"RspCode": "01", "Message": "Order not found"})
                return self._redirect_client("failed", code="01")

            if not vnp.validate_response(VNPAY_HASH_SECRET):
                # return JsonResponse({"RspCode": "97", "Message": "Invalid Signature"})
                return self._redirect_client("failed", order_id=order_id, code="97")

            with transaction.atomic():
                order = Order.objects.select_for_update().filter(pk=order_id).first()
                if not order:
                    # return JsonResponse({"RspCode": "01", "Message": "Order not found"})
                    return self._redirect_client("failed", order_id=order_id, code="01")

                if order.status == OrderStatus.COMPLETED:
                    # return JsonResponse({"RspCode": "02", "Message": "Order Already Update"})
                    return self._redirect_client(
                        "success", order_id=order_id, code="02"
                    )

                if response_code == "00":
                    order.status = OrderStatus.COMPLETED
                    order.save(update_fields=["status", "updated_at"])
                    logger.info(
                        f"VNPay IPN success: order {order.id} marked as COMPLETED"
                    )
                    # return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})
                    return self._redirect_client(
                        "success", order_id=order_id, code=response_code
                    )
                else:
                    logger.info(
                        f"VNPay IPN non-success code for order {order.id}: {response_code}"
                    )
                    # return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})
                    return self._redirect_client(
                        "failed", order_id=order_id, code=response_code
                    )

        except Exception as exc:
            logger.error(f"VNPay IPN error: {str(exc)}")
            # return JsonResponse({"RspCode": "99", "Message": "Invalid request"})
            return self._redirect_client("invalid")
