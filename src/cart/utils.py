import string
import random

import pandas as pd
from django.db import connection

from .models import (
    Cart
)
from .sqls import (
    user_cart_details_query,
    guest_cart_details_query,
    cart_item_details_query,
    consolidate_cart,
)

CART_QUERY_COLUMNS = [
    'item_id', 'sku', 'brand_name', 'title', 'attribute', 'maximum_retail_price',
    'qty', 'unit_price', 'unit_discount', 'discount_percent', 'unit_tax', 'image_url'
]


def transform_cart_details(details):
    details.columns = CART_QUERY_COLUMNS
    details.attribute = details.apply(
        lambda row: [{
            'name': attr.split('<|>')[0],
            'value': attr.split('<|>')[1],
        } for attr in row.attribute.split(',')], axis=1
    )
    details['p_sku'] = details.apply(
        lambda row: ('_').join(row.sku.split('_')[0:3]), axis=1)
    details.attribute = details.apply(lambda row: sorted(
        row.attribute, key=lambda k: k['name']), axis=1)
    return details.to_dict('records')


def guest_token():
    invalid = True

    while invalid:
        token = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=20))
        cart = Cart.objects.filter(guest_code=token).first()
        if not cart:
            cart = Cart(
                guest_code=token,
                total_items=0,
            )
            cart.save()
            invalid = False
    return token


def user_cart_details(user_id):
    cursor = connection.cursor()
    cursor.execute(user_cart_details_query(user_id))
    df = pd.DataFrame(cursor.cursor.fetchall())
    if not df.empty:
        return transform_cart_details(df)
    else:
        return list()


def guest_cart_details(token):
    cursor = connection.cursor()
    cursor.execute(guest_cart_details_query(token))
    df = pd.DataFrame(cursor.cursor.fetchall())
    if not df.empty:
        return transform_cart_details(df)
    else:
        return list()


def cart_item_details(item_id):
    cursor = connection.cursor()
    cursor.execute(cart_item_details_query(item_id))
    df = pd.DataFrame(cursor.cursor.fetchall())
    if not df.empty:
        return transform_cart_details(df)[0]
    else:
        return list()


def combine_user_guest_cart(code, id):
    cursor = connection.cursor()
    cursor.execute(consolidate_cart(code, id))
    df = pd.DataFrame(cursor.cursor.fetchall())
    if df.empty:
        return
    df.columns = ['id', 'qty']
    df.qty = df.apply(lambda row: int(row.qty), axis=1)
    return df.to_dict('records')
