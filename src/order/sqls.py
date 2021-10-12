from cart.sqls import (
    user_cart_details_query
)


def order_sumary_query(user_id):
    sub_query = user_cart_details_query(user_id)
    query = f'''
select 
	sum(unit_price * qty) as item_total,
    sum(unit_discount * qty) as discount,
    sum(unit_tax * qty) as tax,
    (sum(unit_price * qty) + sum(unit_tax * qty)) as grand_total
from (
{sub_query}
) item
    '''
    return query
