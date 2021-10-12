from collections import defaultdict
import pandas as pd
from datetime import datetime
from django.db import connection
from pandas.core.indexes import category

from .models import (
    AttributeMaster,
    AttributeValue,
    PrimaryCategory,
    Category,
    Brand,
    Product,
    ProductSKU,
    ProductAttribute,
    ProductImage,
    SharedImage,
    ProductTag,
)
from user.models import User
from .sqls import (
    menu_query,
    product_by_psku,
    product_by_pcat_slug,
    product_by_cat_slug,
    product_variation_query,
    get_code_details,
    product_rating,
    product_reviews,
)

COLOR_CODES = {
    'Black': {
        'abbr': 'BK',
        'codes': ['#000000'],
    },
    'White': {
        'abbr': 'WH',
        'codes': ['#ffffff'],
    },
    'Blue': {
        'abbr': 'BL',
        'codes': ['#0000ff'],
    },
    'Brown': {
        'abbr': 'BR',
        'codes': ['#964b00'],
    },
    'Tan': {
        'abbr': 'TN',
        'codes': ['#d2b48c'],
    },
    'Mehndi': {
        'abbr': 'MD',
        'codes': ['#493313'],
    },
    'Red': {
        'abbr': 'RD',
        'codes': ['#ff0000'],
    },
    'Yellow': {
        'abbr': 'YL',
        'codes': ['#ffff00'],
    },
    'Green': {
        'abbr': 'GN',
        'codes': ['#00ff00'],
    },
    'Grey': {
        'abbr': 'GY',
        'codes': ['#808080'],
    },
    'Beige': {
        'abbr': 'BG',
        'codes': ['#f5f5dc'],
    },
    'Orange': {
        'abbr': 'Or',
        'codes': ['#ffa500'],
    }
}

PRODUCT_COLUMNS = [
    'id', 'sku', 'legacy_sku', 'brand_name',
    'title', 'in_stock', 'description', 'category_id', 'category_name',
    'category_slug', 'primary_category_id', 'for_gender',
    'primary_category_name', 'primary_category_slug',
    'maximum_retail_price', 'listing_price', 'selling_price',
    'additional_discount', 'listing_date', 'is_active',
    'attribute', 'cover_image', 'other_images',
    'created_ts', 'modified_ts'
]


def transform_product_data(product_master):
    cursor = connection.cursor()
    try:
        product_master.attribute = product_master.apply(
            lambda row: [{
                'name': attr.split('<|>')[0],
                'value': attr.split('<|>')[1],
            } for attr in row.attribute.split(',')], axis=1
        )
        product_master.other_images = product_master.apply(
            lambda row: row.other_images.split(','), axis=1
        )

        product_master['p_sku'] = product_master.apply(
            lambda row: ('_').join(row.sku.split('_')[0:3]), axis=1)

        id_list = [str(id) for id in list(product_master.id)]

        cursor.execute(product_variation_query(id_list))

        variations = pd.DataFrame(cursor.fetchall())
        variations.columns = ['sku', 'title', 'value']
        variations = variations.pivot(
            index='sku', columns='title', values='value').reset_index()
        variations.columns = ['sku', 'color', 'available_sizes']
        variations['p_sku'] = variations.apply(
            lambda row: ('_').join(row.sku.split('_')[0:3]), axis=1)
        variations = variations[[
            'p_sku', 'color', 'available_sizes']]
        variations = variations.groupby(
            ['p_sku', 'color'], as_index=False).agg({'available_sizes': list})

        cursor.execute(get_code_details())
        color_codes = pd.DataFrame(cursor.fetchall())
        color_codes.columns = ['color', 'codes']
        color_codes.codes = color_codes.apply(
            lambda row: row.codes.split(';'), axis=1)

        prd_variations = pd.merge(variations,
                                  color_codes, on='color', how='inner')

        prd_variations['variations'] = prd_variations.apply(lambda row: {
            'color': row.color,
            'color_codes': row.codes,
            'available_sizes': row.available_sizes
        }, axis=1)
        prd_variations = prd_variations[['p_sku', 'variations']]
        prd_variations = prd_variations.groupby(
            ['p_sku'], as_index=False).agg({'variations': list})

        product_details = product_master

        unique_products = list(product_details.p_sku.unique())
        cursor.execute(product_rating('","'.join(unique_products)))
        prd_rating = pd.DataFrame(cursor.fetchall())
        if not prd_rating.empty:
            prd_rating.columns = ['p_sku', 'rating']

        data = list()
        for prd in unique_products:
            if not prd_rating.empty:
                rating = prd_rating[prd_rating.p_sku == prd]
                p_rating = list(rating.rating)[0] if not rating.empty else 2.5
            else:
                p_rating = 2.5
            data.append({
                'parent': prd,
                'details': product_details[product_details.p_sku == prd].to_dict('records'),
                'variations': prd_variations[prd_variations.p_sku == prd].to_dict('records')[0]['variations'],
                'rating': p_rating
            })
        return data
    except Exception as e:
        print(e)
        return []


def get_menu_content():
    cursor = connection.cursor()
    cursor.execute(menu_query())
    df = pd.DataFrame(cursor.fetchall())
    try:
        df.columns = ['gender', 'category', 'sub_category',
                      'catgory_slug', 'sub_category_slug']

        df.sub_category = df.sub_category.fillna('')
        df.sub_category_slug = df.sub_category_slug.fillna('')

        df = df.groupby(['gender', 'category', 'catgory_slug']).agg(
            {
                'sub_category': lambda scat: ','.join(scat),
                'sub_category_slug': lambda scats: ','.join(scats)
            }
        ).reset_index()

        df.sub_category = df.apply(lambda row: row.sub_category.split(
            ',') if row.sub_category != '' else [], axis=1)
        df.sub_category_slug = df.apply(lambda row: row.sub_category_slug.split(
            ',') if row.sub_category_slug != '' else [], axis=1)

        df_2 = df[['gender', 'category']]

        df_2 = df_2.groupby('gender')['category'].apply(list).reset_index()

        data_dict = df_2.to_dict('records')

        data = list()

        for p_index in range(0, len(data_dict)):
            row = data_dict[p_index]
            gender_name = row['gender']
            category_list = row['category']
            temp = dict()
            temp['gender'] = gender_name
            categories = list()
            for c_index in range(0, len(category_list)):
                category_name = category_list[c_index]
                sub_categories = df[(df.gender == gender_name)
                                    & (df.category == category_name)]
                sub_cats = list(sub_categories.sub_category)[0]
                slugs = list(sub_categories.sub_category_slug)[0]
                all_category_slug = list(sub_categories['catgory_slug'])[0]

                categories.append({
                    'name': category_name,
                    'subCategories': [f'All {category_name}'] + sub_cats if len(sub_cats) >= 1 else sub_cats,
                    'subCategoryslugs': [all_category_slug] + slugs if len(slugs) >= 1 else slugs,

                })
            data.append({
                'name': gender_name,
                'categories': categories
            })

        return data
    except Exception as e:
        return []


def pre_load_products():
    # ['Sku Id', 'Brand', 'Product Title', 'Product Description', 'Material', 'Product Category', 'Sub Category',
    #     'Color', 'Size', 'MRP', 'Selling Price', 'Listing Date', 'Quantity', 'Status', 'Discount(in %)']
    # df = pd.read_csv('prd.csv')
    # columns = list(df.columns)

    # new_columns = list()

    # for col in columns:
    #     if not col.startswith('Unnamed:'):
    #         new_columns.append(col)

    # df = df[new_columns]
    # df = df.assign(Size=df['Size'].str.split(',')).explode('Size')
    # df.to_csv('products.csv')

    data = pd.read_csv('products.csv')
    admin_user = User.objects.get(pk=1)
    columns = ['Sku Id', 'Brand', 'Product Title', 'Product Description', 'Material', 'Product Category', 'Sub Category',
               'Color', 'Size', 'MRP', 'Selling Price', 'Listing Date', 'Quantity', 'Status', 'Discount(in %)']

    data = data[columns]
    data = data[data['Sku Id'].str.startswith('BFS_500')]

    for index, row in data.iterrows():
        print(index)
        create_new_image_record = True
        image_product = Product.objects.filter(
            legacy_sku=row['Sku Id']).first()
        if image_product:
            create_new_image_record = False
        code = row['Sku Id'].split('_')[1]
        brand = Brand.objects.get(name=row['Brand'])
        if row['Product Category'] == 'Mens footwear':
            parent_category = PrimaryCategory.objects.get(slug='men-footwears')
        category = Category.objects.filter(
            name__iexact=row['Sub Category'], p_cat=parent_category).first()
        material_attribute = AttributeValue.objects.filter(
            display_value__iexact=row['Material'],
            attribute_master__name='Material',
            attribute_master__type="MATERIAL"
        ).first()
        color_attribute = AttributeValue.objects.filter(
            display_value__iexact=row['Color'],
            attribute_master__name='Color',
            attribute_master__type="COLOR"
        ).first()
        size_attribute = AttributeValue.objects.filter(
            display_value__iexact=row['Size'],
            attribute_master__name='Size (UK)',
            attribute_master__type="FOOTSIZE"
        ).first()
        listing_date = datetime.strptime(row['Listing Date'], '%d/%m/%Y')
        product = Product(
            title='Genuine Leather Slippers For Men',  # row['Product Title'],
            legacy_sku=row['Sku Id'],
            code=code,
            brand=brand,
            category=category,
            description=row['Product Description'],
            listing_date=listing_date,
            is_active=True if['Status'] == 'Active' else False,
            qty=row['Quantity'],
            maximum_retail_price=row['MRP'],
            listing_price=row['Selling Price'],
            additional_discount=0,
            created_by=admin_user
        )
        product.save()

        material = ProductAttribute(
            product=product,
            attribute=material_attribute
        )
        material.save()

        color = ProductAttribute(
            product=product,
            attribute=color_attribute
        )
        color.save()

        size = ProductAttribute(
            product=product,
            attribute=size_attribute
        )
        size.save()

        product_sku = ProductSKU(product=product)
        product_sku.save()

        if create_new_image_record:
            cover_image = ProductImage(
                product=product,
                is_cover=1,
                image_link='https://s3-us-west-2.amazonaws.com/s.cdpn.io/245657/t-shirt.png'
            )
            cover_image.save()

            other_image_1 = ProductImage(
                product=product,
                is_cover=0,
                image_link='https://s3-us-west-2.amazonaws.com/s.cdpn.io/245657/t-shirt-large.png',
                display_order=1
            )
            other_image_1.save()
            other_image_2 = ProductImage(
                product=product,
                is_cover=0,
                image_link='https://s3-us-west-2.amazonaws.com/s.cdpn.io/245657/t-shirt-large2.png',
                display_order=2
            )
            other_image_2.save()
            other_image_3 = ProductImage(
                product=product,
                is_cover=0,
                image_link='https://s3-us-west-2.amazonaws.com/s.cdpn.io/245657/t-shirt-large3.png',
                display_order=3
            )
            other_image_3.save()
        else:
            shared_images = SharedImage(
                product=product,
                parent_product=image_product
            )
            shared_images.save()

    ######################
    # Material Attribute #
    ######################
    # materials = data.Material.unique()
    # transformed_materials = list()
    # for mat in materials:
    #     words = mat.split(" ")
    #     words = [word if word == 'and' else word.capitalize()
    #              for word in words]
    #     transformed_materials.append(" ".join(words))
    # material_master = AttributeMaster.objects.filter(
    #     name="Material",
    #     type="MATERIAL"
    # ).first()
    # transformed_materials.sort()

    # for mat in transformed_materials:
    #     material_value = AttributeValue.objects.filter(
    #         attribute_master=material_master,
    #         display_value=mat
    #     ).first()
    #     if not material_value:
    #         material_value = AttributeValue(
    #             attribute_master=material_master,
    #             display_value=mat,
    #             created_by=admin_user
    #         )
    #         material_value.save()
    #         print('Value record created for material -->', mat)
    #     else:
    #         print('Value already exists in DB')

    ######################
    # Color Attribute #
    ######################
    # colors = data.Color.unique()
    # colors.sort()

    # color_master = AttributeMaster.objects.filter(
    #     name="Color",
    #     type="COLOR"
    # ).first()
    # for color in colors:
    #     color = color.capitalize()

    #     color_properties = COLOR_CODES[color]

    #     abbr = color_properties['abbr']
    #     codes = color_properties['codes']

    #     color_value = AttributeValue.objects.filter(
    #         attribute_master=color_master,
    #         display_value=color,
    #         color_abbr=abbr,
    #         total_codes=len(codes),
    #     ).first()

    #     if not color_value:
    #         color_value = AttributeValue(
    #             attribute_master=color_master,
    #             display_value=color,
    #             color_abbr=abbr,
    #             total_codes=len(codes),
    #             created_by=admin_user,
    #         )
    #         for i in range(0, len(codes)):
    #             if (i == 0):
    #                 color_value.code_1 = codes[i]
    #             elif (i == 1):
    #                 color_value.code_2 = codes[i]
    #             elif (i == 2):
    #                 color_value.code_3 = codes[i]
    #             elif (i == 3):
    #                 color_value.code_4 = codes[i]
    #             else:
    #                 pass
    #         color_value.save()
    #         print('created color value for', color)
    #     else:
    #         print('color value already exists', color)

    ######################
    # category Attribute #
    ######################
    # categories = data['Sub Category'].unique()
    # categories.sort()
    # primary_cat = PrimaryCategory.objects.get(slug="men-footwears")

    # for cat in categories:
    #     category = Category.objects.filter(
    #         p_cat=primary_cat,
    #         name=cat
    #     ).first()

    #     if not category:
    #         category = Category(
    #             p_cat=primary_cat,
    #             name=cat,
    #             created_by=admin_user
    #         )
    #         category.save()
    #         print('created category for', primary_cat, ' - ', cat)
    #     else:
    #         print(cat, 'category already exists in the data base')


# def get_products():
#     cursor = connection.cursor()
#     cursor.execute(all_product_query())
#     df = pd.DataFrame(cursor.fetchall())
#     df.columns = ['id', 'sku', 'legacy_sku', 'description', 'brand_name', 'title', 'category_id', 'category_name', 'category_slug', 'primary_category_id', 'for_gender', 'primary_category_name',
#                   'primary_category_slug', 'maximum_retail_price', 'listing_price', 'selling_price', 'additional_discount', 'listing_date', 'is_active', 'attribute', 'cover_image', 'other_images']
#     df.to_csv('test.csv')


def product_by_primary_category(slug):
    cursor = connection.cursor()
    cursor.execute(product_by_pcat_slug(slug))
    try:
        product_master = pd.DataFrame(cursor.fetchall())
        product_master.columns = PRODUCT_COLUMNS
        transformed_data = transform_product_data(product_master)
        return transformed_data
    except Exception as e:
        return []


def product_by_category(slug):
    cursor = connection.cursor()
    cursor.execute(product_by_cat_slug(slug))
    try:
        product_master = pd.DataFrame(cursor.fetchall())
        product_master.columns = PRODUCT_COLUMNS
        transformed_data = transform_product_data(product_master)
        return transformed_data
    except Exception as e:
        return []


def product_by_parent_sku(p_sku):
    cursor = connection.cursor()
    cursor.execute(product_by_psku(p_sku))
    try:
        product_master = pd.DataFrame(cursor.fetchall())
        product_master.columns = PRODUCT_COLUMNS
        transformed_data = transform_product_data(product_master)
        return transformed_data
    except Exception as e:
        return []


def fetch_product_reviews(p_sku, email):
    cursor = connection.cursor()
    cursor.execute(product_reviews(p_sku, email))
    df = pd.DataFrame(cursor.fetchall())
    if not df.empty:
        df.columns = [
            'id', 'initial', 'name',
            'email', 'givenRating', 'content',
            'dislikes', 'likes', 'userReaction', 'date'
        ]
        df.userReaction = df.userReaction.fillna(-1)
        return df.to_dict('records')
    else:
        return []
