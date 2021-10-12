def cart_details_query(condition=None):
    query = f'''
select 
	item_id, 
    sku, 
    brand_name, 
    title, 
    attribute, 
    maximum_retail_price, 
    qty, 
    unit_price,
    unit_discount,
    round((
		((unit_discount)/(unit_price + unit_discount)) * 100), 
		0
	) as discount_percent,
    unit_price * (unit_tax_percent/100) as unit_tax,
    image_url
from (
	select distinct
			ci.id as item_id,
			sku.sku,
			brand.name as brand_name,
			prd.title as title,
			attr_details.attribute,
			prd.maximum_retail_price,
			ci.qty,
            prd.maximum_retail_price - (prd.listing_price + (prd.listing_price * (prd.additional_discount/100))) as unit_discount,
            prd.listing_price + (prd.listing_price * (prd.additional_discount/100)) as unit_price,
            prd.tax as unit_tax_percent,
			cvr_img.image_url
	from cart_cart crt
	join cart_cartitem ci on ci.cart_id = crt.id
	left join user_user usr on usr.id = crt.user_id
	join shop_product prd on prd.id = ci.product_id
	join shop_productsku sku ON prd.id = sku.product_id
	join shop_brand brand ON brand.id = prd.brand_id
	join(
		select 
			prd_attr.product_id,
			GROUP_CONCAT(attr.attribute) AS attribute
		from shop_productattribute prd_attr
		join (
			select 
				attr1.id,
				CONCAT(attr1.title, '<|>', attr1.value) as attribute
			from (
				select 
					val.id,
					ky.name as title,
					val.display_value as value
				from shop_attributevalue val
				join shop_attributemaster ky on ky.id = val.attribute_master_id
											and ( ky.type like '%SIZE%' or ky.type = 'COLOR')
			) attr1
		) attr on attr.id = prd_attr.attribute_id
		group by prd_attr.product_id
		order by prd_attr.product_id
	) attr_details ON attr_details.product_id = prd.id
	join (
		select 
			img_lookup.id product_id, img_lookup.look_up_id
		from (
			select 
				prd.id,
				case
					when
					cvr_img.id is not null
					and shrd_cvr_img.parent_product_id is null then
						cvr_img.product_id
					else shrd_cvr_img.parent_product_id
				end as look_up_id
			from shop_product prd
			left join shop_productimage cvr_img on prd.id = cvr_img.product_id and cvr_img.is_cover = 1
			left join shop_sharedimage shrd_cvr_img on prd.id = shrd_cvr_img.product_id
		) img_lookup
		where img_lookup.look_up_id is not null
	) img_lkp on img_lkp.product_id = prd.id
	join (
			select 
				product_id,
				image_link as image_url
			from shop_productimage
			where is_cover = 1
			order by product_id
	) cvr_img on cvr_img.product_id = img_lkp.look_up_id
	{condition}
) a
    '''
    return query


def user_cart_details_query(user_id):
    condition = f'''where usr.id = {user_id}'''
    return cart_details_query(condition)


def guest_cart_details_query(token):
    condition = f'''where crt.guest_code = "{token}"'''
    return cart_details_query(condition)


def cart_item_details_query(item_id):
    condition = f'''where ci.id = {item_id}'''
    return cart_details_query(condition)


def consolidate_cart(guest_code, id):
    query = f"""
    select 
        items.id, 
        sum(items.qty) as qty
    from (
        select
            prd.id,
            ci.qty 
        from cart_cart crt 
        join cart_cartitem ci on ci.cart_id = crt.id
        join shop_product prd on prd.id = ci.product_id
        where crt.guest_code = '{guest_code}'
        union all
        select 
            prd.id,
            ci.qty 
        from cart_cart crt 
        join user_user usr 	 on usr.id = crt.user_id 
                            and usr.id = {id}
        join cart_cartitem ci on ci.cart_id = crt.id
        join shop_product prd on prd.id = ci.product_id
    ) items
    group by items.id;
    """
    return query
