import pandas as pd
import razorpay

from django.db import connection

from .models import (
    Order,
    OrderItem,
    OrderActivity,
    OrderPayment,
)
from cart.models import (
    Cart,
    CartItem
)
from user.models import (
    UserAddress
)
from .sqls import order_sumary_query


def add_order_activity(order, new_status):
    last_activity = OrderActivity.objects.filter(
        order=order).order_by('-created').first()
    order_activity = OrderActivity(
        order=order,
        from_status=last_activity.to_status,
        to_status=new_status
    )
    order_activity.save()


def get_order_summary(user_id):
    cursor = connection.cursor()
    cursor.execute(order_sumary_query(user_id))
    df = pd.DataFrame(cursor.cursor.fetchall())
    df.columns = ['item_total', 'discount', 'tax', 'grand_total']
    summary = df.to_dict('records')
    return summary[0]


def create_order(user, ship_addr_id, bill_addr_id, notes):
    cart = Cart.objects.filter(user=user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    ship_addr = UserAddress.objects.get(pk=ship_addr_id)
    bill_addr = UserAddress.objects.get(pk=bill_addr_id)

    order_details = get_order_summary(user.id)
    order_summary_created = False
    try:
        order = Order(
            user=user,
            name=user.get_full_name(),
            mobile=user.mobile,
            shipping=ship_addr.get_address_text(),
            billing=bill_addr.get_address_text(),
            status='CR',
            item_total=order_details.get('item_total'),
            discount=order_details.get('discount'),
            tax=order_details.get('tax'),
            grand_total=order_details.get('grand_total'),
            notes=notes
        )
        order.save()

        initial_activity = OrderActivity(
            order=order,
            from_status='-',
            to_status='CR'
        )
        initial_activity.save()
        order_summary_created = True
    except Exception as e:
        print(e)
        if order_summary_created:
            order.delete()
    finally:
        if order_summary_created:
            for item in cart_items:
                order_item = OrderItem(
                    order=order,
                    product=item.product,
                    qty=item.qty,
                    unit_price=item.product.listing_price -
                    (item.product.listing_price *
                     (item.product.additional_discount/100))
                )
                order_item.save()
                item.delete()

            cart.delete()
        return order.id


def create_razorpay_order(order_id):
    client = razorpay.Client(
        auth=("rzp_test_SrbG27vnZni92A", "ktdpqLfd7WN5yQL2ObW4w0HS"))
    order = Order.objects.get(pk=order_id)
    data = {
        "amount": order.grand_total * 100,
        "currency": "INR",
        "receipt": f"order_{order.id}",
        "notes": {'Shipping address': order.shipping}
    }
    payment = client.order.create(data=data)
    checkout_options = {
        'currency': 'INR',
        'amount': str(int(order.grand_total * 100)),
        'name': "Big Fox",
        'description': "Thank You for shopping with us",
        'order_id': payment.get('id'),
        'notes': {
            'id': order.id,
        },
        'prefill': {
            'name': order.user.get_full_name(),
            'email': order.user.email,
            'contact': str(order.user.mobile),
        },
    }
    return checkout_options


def confirm_payment(data):
    order = Order.objects.get(pk=data.get('order_id'))
    pmt_info = OrderPayment(
        order=order,
        rp_payment_id=data.get('razorpay_payment_id'),
        rp_order_id=data.get('razorpay_order_id'),
        success=data.get('status')
    )
    pmt_info.save()
    new_status = 'PL' if data.get('status') else 'FL'
    add_order_activity(order, new_status)
    order.status = new_status
    order.save()
