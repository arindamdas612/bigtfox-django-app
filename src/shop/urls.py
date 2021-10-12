from django.urls import path

from .views import (
    menu_content,
    get_category_details,
    get_sub_category_details,
    get_p_sku_details,
    ProdcutReview,
)

urlpatterns = [
    path('menu-content/', menu_content),
    path('category/<str:slug>', get_category_details),
    path('sub-category/<str:slug>', get_sub_category_details),
    path('product/<str:p_sku>', get_p_sku_details),
    path('product-review/<str:p_sku>', ProdcutReview.as_view())
]
