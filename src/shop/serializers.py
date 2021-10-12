from rest_framework import serializers


class ProductReviewSerializer(serializers.Serializer):
    p_sku = serializers.CharField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    content = serializers.CharField()
