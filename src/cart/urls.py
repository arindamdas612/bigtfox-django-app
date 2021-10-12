from django.urls import path

from .views import (
    generate_guest_cart_token,
    add_to_cart,
    user_cart,
    guest_cart,
    modify_cart_item,
    delete_cart_item,
    modify_guest_cart_item,
    delete_guest_cart_item,
    validate_cart,
    transfer_cart,
)
urlpatterns = [
    path('generate-guest-token/', generate_guest_cart_token),

    path('add/', add_to_cart),

    path('user/', user_cart),
    path('user/modify/<int:item_id>', modify_cart_item),
    path('user/item/<int:item_id>', delete_cart_item),
    path('user/validate/', validate_cart),
    path('user/transfer/<str:guest_code>', transfer_cart),

    path('guest/<str:guest_token>', guest_cart),
    path('guest/modify/<int:item_id>', modify_guest_cart_item),
    path('guest/item/<int:item_id>', delete_guest_cart_item),
]
