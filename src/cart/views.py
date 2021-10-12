import json

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions, status

from .utils import (
    guest_token,
    user_cart_details,
    guest_cart_details,
    cart_item_details,
    combine_user_guest_cart
)
from .models import Cart, CartItem
from user.models import User
from shop.models import (
    ProductSKU,
    Product
)


@api_view(['GET'])
def generate_guest_cart_token(request, format=None):
    token = guest_token()
    return Response({'guest_token': token})


@ api_view(['POST'])
def add_to_cart(request, format=None):
    data = json.loads(request.body)
    required_fields = ['is_guest', 'guest_token', 'email', 'sku', 'qty']

    other_fields = list(set(required_fields) - set(data))
    if len(other_fields) > 0:
        return Response({
            'missing_fields': other_fields
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    sku_object = ProductSKU.objects.filter(sku=data.get('sku')).first()
    if not sku_object:
        return Response({
            'error': 'Invalid product SKU'
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if not data.get('is_guest'):
        user = User.objects.filter(email=data.get('email')).first()
        if not user:
            return Response({
                'error': 'Invalid EMAIL'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            cart = Cart(user=user, total_items=0)
    else:
        cart = Cart.objects.filter(guest_code=data.get('guest_token')).first()
        if not cart:
            cart = Cart(guest_code=data.get('guest_token'), total_items=0)

    if not cart.id:
        cart.save()

    cartItem = CartItem.objects.filter(
        cart=cart, product=sku_object.product).first()
    if not cartItem:
        cartItem = CartItem(
            cart=cart,
            product=sku_object.product,
            qty=0,
        )
        cart.total_items = cart.total_items + 1
        cart.save()

    cartItem.qty = cartItem.qty + 1
    cartItem.save()

    if not data.get('is_guest'):
        cart = Cart.objects.filter(user=user).first()
        data = user_cart_details(user.id)

        return Response({
            'total_items': cart.total_items,
            'cart_items': data,
        })
    else:
        cart = Cart.objects.filter(guest_code=data.get('guest_token')).first()
        data = guest_cart_details(data.get('guest_token'))
        return Response({
            'total_items': cart.total_items,
            'cart_items': data,
        })


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def user_cart(request, format=None):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        data = user_cart_details(request.user.id)
        return Response({
            'total_items': cart.total_items,
            'cart_items': data,
        })
    return Response({
        'total_items': 0,
        'cart_items': [],
    })


@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def modify_cart_item(request, item_id, format=None):
    data = json.loads(request.body)
    if 'qty' not in list(data.keys()):
        return Response({'error': 'Qty not present'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    cart_item = CartItem.objects.filter(id=item_id).first()
    if not cart_item:
        return Response({'error': 'Invalid Cart Item'}, status=status.HTTP_400_BAD_REQUEST)

    if not cart_item.cart.user == request.user:
        return Response({'error': "Cannot Modify other's Cart item"}, status=status.HTTP_400_BAD_REQUEST)

    cart_item.qty = data.get('qty')
    cart_item.save()
    return Response(cart_item_details(item_id))


@api_view(['DELETE'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def delete_cart_item(request, item_id, format=None):
    cart_item = CartItem.objects.filter(id=item_id).first()
    if not cart_item:
        return Response({'error': 'Invalid Cart Item'}, status=status.HTTP_400_BAD_REQUEST)

    if not cart_item.cart.user == request.user:
        return Response({'error': "Cannot Modify other's Cart item"}, status=status.HTTP_400_BAD_REQUEST)

    cart_item.delete()

    cart = Cart.objects.filter(user=request.user).first()
    cart.total_items = cart.total_items - 1
    cart.save()

    data = user_cart_details(request.user.id)

    return Response({
        'total_items': cart.total_items,
        'cart_items': data,
    })


@ api_view(['GET'])
def guest_cart(request, guest_token, format=None):
    cart = Cart.objects.filter(guest_code=guest_token).first()
    data = guest_cart_details(guest_token)
    return Response({
        'total_items': cart.total_items,
        'cart_items': data,
    })


@api_view(['POST'])
def modify_guest_cart_item(request, item_id, format=None):
    data = json.loads(request.body)
    if 'token' not in list(data.keys()):
        return Response({'error': 'Guest UID not present'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if 'qty' not in list(data.keys()):
        return Response({'error': 'Qty not present'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    cart_item = CartItem.objects.filter(id=item_id).first()
    if not cart_item:
        return Response({'error': 'Invalid Cart Item'}, status=status.HTTP_400_BAD_REQUEST)

    if not cart_item.cart.guest_code == data.get('token'):
        return Response({'error': "Cannot Modify other's Cart item"}, status=status.HTTP_400_BAD_REQUEST)

    cart_item.qty = data.get('qty')
    cart_item.save()
    return Response(cart_item_details(item_id))


@api_view(['DELETE'])
def delete_guest_cart_item(request, item_id, format=None):
    cart_item = CartItem.objects.filter(id=item_id).first()
    if not cart_item:
        return Response({'error': 'Invalid Cart Item'}, status=status.HTTP_400_BAD_REQUEST)
    guest_code = cart_item.cart.guest_code
    cart_item.delete()

    cart = Cart.objects.filter(guest_code=guest_code).first()
    cart.total_items = cart.total_items - 1
    cart.save()

    data = guest_cart_details(guest_code)
    return Response({
        'total_items': cart.total_items,
        'cart_items': data,
    })


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def validate_cart(request, format=None):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return Response({
            'error': 'Invalid Cart ID'
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    invalid_items = list()
    cartItems = CartItem.objects.filter(cart=cart)
    for cartItem in cartItems:
        remaing_qty = cartItem.product.qty - cartItem.qty
        if remaing_qty < 3:
            recomended_qty = cartItem.product.qty - 3
            invalid_items.append({
                'id': cartItem.id,
                'requested': cartItem.qty,
                'recomeded': recomended_qty if recomended_qty > 0 else 0
            })
    return Response({
        'valid': len(invalid_items) == 0,
        'items': invalid_items
    })


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def transfer_cart(request, guest_code, format=None):
    guest_cart = Cart.objects.filter(guest_code=guest_code).first()
    user_cart = Cart.objects.filter(user=request.user).first()

    if not user_cart:
        user_cart = Cart(user=request.user, total_items=0)
        user_cart.save()

    if not guest_cart:
        return Response({
            'total_items': user_cart.total_items,
            'cart_items': user_cart_details(request.user.id),
        })

    cart_item_details = combine_user_guest_cart(guest_code, request.user.id)
    if not cart_item_details:
        return Response({
            'total_items': 0,
            'cart_items': [],
        })

    for item in cart_item_details:
        cart_item = CartItem.objects.filter(
            cart=user_cart, product__id=item.get('id')).first()
        if cart_item:
            cart_item.qty = item.get('qty')
        else:
            product = Product.objects.get(id=item.get('id'))
            cart_item = CartItem(
                cart=user_cart,
                product=product,
                qty=item.get('qty'),
                unit_price=product.listing_price,
                unit_discount=(product.maximum_retail_price - product.listing_price) + (
                    product.listing_price * (product.additional_discount/100))
            )
        cart_item.save()

    user_cart.total_items = len(cart_item_details)
    user_cart.save()
    guest_cart.delete()

    data = user_cart_details(request.user.id)

    return Response({
        'total_items': user_cart.total_items,
        'cart_items': data,
    })
