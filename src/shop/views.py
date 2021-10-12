import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProductReview, ReviewReaction
from user.models import User
from .utils import (
    get_menu_content,
    product_by_primary_category,
    pre_load_products,
    product_by_parent_sku,
    fetch_product_reviews,
    product_by_category
)


@api_view(['GET'])
def menu_content(request, format=None):
    data = get_menu_content()
    return Response(data)


@api_view(['GET'])
def get_category_details(request, slug, format=None):
    data = product_by_primary_category(slug)
    return Response(data)


@api_view(['GET'])
def get_sub_category_details(request, slug, format=None):
    data = product_by_category(slug)
    return Response(data)


@api_view(['GET'])
def get_p_sku_details(request, p_sku, format=None):
    data = product_by_parent_sku(p_sku)
    return Response(data)


class ProdcutReview(APIView):

    def get(self, request, p_sku, format=None):
        email = request.GET.get('email', None)
        data = fetch_product_reviews(p_sku, email)
        return Response(data)

    def post(self, request, p_sku, format=None):
        data = json.loads(request.body)
        required_fields = ['email', 'rating', 'content']

        other_fields = list(set(required_fields) - set(data))

        if len(other_fields) == 0:
            user = User.objects.filter(email=data.get('email')).first()
            if not user:
                return Response({
                    'error': f"User does not exist with Email '{data.get('email')}'"
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            review = ProductReview(
                parent_sku=p_sku,
                user_rating=data.get('rating'),
                user_review=data.get('content'),
                created_by=user
            )
            review.save()
            data = fetch_product_reviews(p_sku, user.email)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'missing_fields': other_fields
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def put(self, request, p_sku, format=None):
        data = json.loads(request.body)
        required_fields = ['review_id', 'email', 'reaction']

        other_fields = list(set(required_fields) - set(data))

        if len(other_fields) == 0:
            user = User.objects.filter(email=data.get('email')).first()
            if not user:
                return Response({
                    'error': f"User does not exist with Email '{data.get('email')}'"
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            review = ProductReview.objects.filter(
                id=data.get('review_id')).first()
            if not review:
                return Response({
                    'error': f"Invalid review to react"
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

            reaction = ReviewReaction.objects.filter(
                created_by=user, review=review).first()
            if reaction:
                reaction.reaction = data.get('reaction')
            else:
                reaction = ReviewReaction(
                    review=review,
                    reaction=data.get('reaction'),
                    created_by=user,
                )
            reaction.save()
            data = fetch_product_reviews(p_sku, user.email)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'missing_fields': other_fields
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
