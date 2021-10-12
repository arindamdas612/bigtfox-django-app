from django.contrib import admin

from .models import (
    Order,
    OrderItem,
    OrderRefund,
    OrderPayment,
    OrderActivity,
)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderRefund)
admin.site.register(OrderPayment)
admin.site.register(OrderActivity)
