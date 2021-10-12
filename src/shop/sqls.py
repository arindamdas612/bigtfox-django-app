
def menu_query():
    query = '''
    select 
        a.gender,
        a.wear_type,
        a.category,
        a.slug,
        a.slug1
    from (
        select
            pcat.gender as gender,
            pcat.name as wear_type,
            cat.name as category,
            pcat.slug as slug,
            cat.slug as slug1,
            pcat.display_order
        from
        shop_primarycategory pcat
        left join shop_category cat
        on pcat.id = cat.p_cat_id
        order by pcat.display_order
    ) a;
    '''
    return query


def all_product_query(condition=''):
    query = f"""
    SELECT 
        prd.id,
        sku.sku,
        prd.legacy_sku,
        brand.name AS brand_name,
        prd.title,
        CASE
            WHEN prd.qty < 3 THEN
                0
            ELSE
                1
        END AS in_stock,
        prd.description,
        prd.category_id,
        cat.name AS category_name,
        cat.slug AS category_slug,
        p_cat.id AS primary_category_id,
        p_cat.gender AS for_gender,
        p_cat.name AS primary_category_name,
        p_cat.slug AS primary_category_slug,
        prd.maximum_retail_price,
        prd.listing_price,
        CASE
            WHEN prd.additional_discount = 0 THEN prd.listing_price
            ELSE prd.listing_price - ((prd.additional_discount / 100) * prd.listing_price)
        END AS selling_price,
        prd.additional_discount,
        prd.listing_date,
        prd.is_active,
        attr_details.attribute,
        cvr_img.image_url as cover_image,
        oth_img.image_urls as other_images,
        prd.created as created_ts,
        prd.modified as modified_ts
    FROM shop_product prd
    JOIN shop_productsku sku ON prd.id = sku.product_id
    JOIN shop_brand brand ON brand.id = prd.brand_id
    JOIN shop_category cat ON cat.id = prd.category_id
    JOIN shop_primarycategory p_cat ON p_cat.id = cat.p_cat_id
    JOIN(
            SELECT 
            prd_attr.product_id,
            GROUP_CONCAT(attr.attribute) AS attribute
        FROM shop_productattribute prd_attr
        JOIN (
                    SELECT 
                    attr1.id,
                CONCAT(attr1.title, '<|>', attr1.value, '<|>', IFNULL(attr1.codes, 'na')) AS attribute
            FROM (
                            SELECT 
                                    val.id,
                                    ky.name AS title,
                                    val.display_value AS value,
                                    CASE
                                            WHEN val.total_codes = 1 THEN code_1
                                            WHEN val.total_codes = 2 THEN CONCAT(code_1, ';', code_2)
                                            WHEN val.total_codes = 3 THEN CONCAT(code_1, ';', code_2, ';', code_3)
                                            WHEN val.total_codes = 4 THEN CONCAT(code_1, ';', code_2, ';', code_3, ';', code_4)
                                            ELSE NULL
                                    END AS codes
                    FROM
                    shop_attributevalue val
                    JOIN shop_attributemaster ky ON ky.id = val.attribute_master_id
                    ) attr1
            ) attr ON attr.id = prd_attr.attribute_id
        GROUP BY prd_attr.product_id
        ORDER BY prd_attr.product_id
    ) attr_details ON attr_details.product_id = prd.id
    JOIN (
        SELECT 
            img_lookup.id product_id, img_lookup.look_up_id
            FROM
            (
                    SELECT 
                            prd.id,
                            CASE
                                    WHEN
                                            cvr_img.id IS NOT NULL
                                                    AND shrd_cvr_img.parent_product_id IS NULL
                                    THEN
                                            cvr_img.product_id
                                    ELSE shrd_cvr_img.parent_product_id
                            END AS look_up_id
                    FROM
                    shop_product prd
                    LEFT JOIN shop_productimage cvr_img ON prd.id = cvr_img.product_id AND cvr_img.is_cover = 1
                    LEFT JOIN shop_sharedimage shrd_cvr_img ON prd.id = shrd_cvr_img.product_id) img_lookup
                    WHERE img_lookup.look_up_id IS NOT NULL
    ) img_lkp ON img_lkp.product_id = prd.id
    JOIN (
            SELECT 
                    product_id,
                    image_link AS image_url
            FROM shop_productimage
            WHERE is_cover = 1
            ORDER BY product_id
    ) cvr_img ON cvr_img.product_id = img_lkp.look_up_id
    JOIN (
            SELECT 
            img.product_id, 
            GROUP_CONCAT(img.image_url) AS image_urls
            FROM (
                    SELECT 
                            product_id,
                            image_link AS image_url
                    FROM shop_productimage
                    WHERE is_cover = 0
                    ORDER BY product_id , display_order
            ) img
            GROUP BY img.product_id
    ) oth_img ON oth_img.product_id = img_lkp.look_up_id
    {condition}
    order by prd.id desc
    ;
	"""
    return query


def product_by_pcat_slug(slug):
    condition = f'where p_cat.slug = "{slug}"'
    return all_product_query(condition)


def product_by_cat_slug(slug):
    condition = f'where cat.slug = "{slug}"'
    return all_product_query(condition)


def product_by_psku(p_sku):
    condition = f'where sku.sku like "{p_sku}%"'
    query = all_product_query(condition)
    return query


def product_variation_query(ids):
    query = f'''
    select 
        prd_sku.sku sku,
        attr.title, 
        attr.value
    from  shop_product prd
    join shop_productsku prd_sku on prd_sku.product_id = prd.id
    join shop_productattribute prd_attr on prd_attr.product_id = prd.id
    join (
        select 
            val.id, 
            ky.name as title,
            val.display_value as value
        from shop_attributevalue val
        join shop_attributemaster ky on ky.id = val.attribute_master_id
        where ky.type in ('COLOR', 'FOOTSIZE', 'SIZE')
    ) attr on attr.id = prd_attr.attribute_id
    where prd.id in ({(',').join(ids)})
    order by prd.id, attr.title;
    '''
    return query


def get_code_details():
    query = f"""
        select 
            vl.display_value as color,
            case 
                when vl.total_codes = 4 then
                    concat(vl.code_1, ';', vl.code_2, ';', vl.code_3, ';', vl.code_4)
                when vl.total_codes = 3 then
                    concat(vl.code_1, ';', vl.code_2, ';', vl.code_3)
                when vl.total_codes = 2 then
                    concat(vl.code_1, ';', vl.code_2)
                else
                    vl.code_1
            end code
        from shop_attributemaster ms
        join shop_attributevalue vl on ms.id = vl.attribute_master_id where type = 'COLOR'
        order by color;
    """
    return query


def product_rating(p_sku):
    query = f'''
    select 
        parent_sku, 
        avg(user_rating) as rating
    from shop_productreview
    where parent_sku in ("{p_sku}")
    group by parent_sku
    ;
    '''
    return query


def product_reviews(p_sku, email):
    query = f'''
    select
        rv.id, 
        substring(usr.firstname, 1, 1) as initial,
        concat(usr.lastname, ', ', usr.firstname) as name,
        usr.email,
        rv.user_rating,
        rv.user_review as content,
        case 
            when rc.dislike_count is not null then 
                rc.dislike_count 
            else 0 
        end as dislikes,
        case 
            when rc.like_count is not null then 
                rc.like_count 
            else 0 
        end as likes,
        case 
            when usr_rctn.reaction is not null then 
                usr_rctn.reaction 
            else -1 
        end as user_reaction,
        date_format(rv.created, '%d %b, %Y') as date
    from shop_productreview rv
    join user_user usr on usr.id = rv.created_by_id
    left join (
        select 
            a.review_id,
            sum(dislike_count) as dislike_count,
            sum(like_count) as like_count
        from (
            select
                rc.review_id,
                rc.reaction,
                case when rc.reaction = 0 then 1 else 0 end as dislike_count,
                case when rc.reaction = 1 then 1 else 0 end as like_count
            from shop_reviewreaction rc
            join user_user usr on usr.id = rc.created_by_id
        ) a 
        group by a.review_id
    )rc on rc.review_id = rv.id
    left join (
        select
            rc.review_id,
            rc.reaction,
            usr.email
        from shop_reviewreaction rc
        join user_user usr on usr.id = rc.created_by_id
        where usr.email = '{email}'
    ) usr_rctn on usr_rctn.review_id = rv.id
    where parent_sku = '{p_sku}'
    order by rv.created desc
    ;
    '''
    return query
