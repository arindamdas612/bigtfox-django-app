from django.contrib import admin
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
    ProductReview,
    ReviewReaction
)

admin.site.register(AttributeMaster)
admin.site.register(AttributeValue)
admin.site.register(PrimaryCategory)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductSKU)
admin.site.register(ProductAttribute)
admin.site.register(ProductImage)
admin.site.register(SharedImage)
admin.site.register(ProductTag)
admin.site.register(ProductReview)
admin.site.register(ReviewReaction)
