import json
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import authentication, permissions, status
from rest_framework.response import Response

from .utils import (
    create_order,
    create_razorpay_order,
    confirm_payment,
)

from user.models import (
    UserAddress
)


@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def place_order(request, format=None):
    data = json.loads(request.body)
    keys_required = ['ship_addr_id', 'bill_addr_id', 'notes']
    invalid = list(set(keys_required) - set(list(data.keys())))
    if len(invalid) > 0:
        return Response({
            'missing_fields': invalid
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    sys_order_id = create_order(request.user, data.get('ship_addr_id'),
                                data.get('bill_addr_id'), data.get('notes'))
    rp_options = create_razorpay_order(sys_order_id)
    return Response(rp_options, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def capture_payment_details(request, format=None):
    data = json.loads(request.body)
    keys_required = ['razorpay_payment_id',
                     'razorpay_order_id', 'razorpay_signature', 'order_id', 'status', 'status_reason']
    invalid = list(set(keys_required) - set(list(data.keys())))
    if len(invalid) > 0:
        return Response({
            'missing_fields': invalid
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    confirm_payment(data)
    return Response({'msg': 'acknowledged'})
