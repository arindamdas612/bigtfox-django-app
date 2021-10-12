import json

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authtoken.models import Token

from .models import User, UserAddress
from .serializers import UserSerializer, ProfilesSerializer, UserAddressSerializer
from .permissions import RetrieveOwnProfile


class UserLoginAPIView(ObtainAuthToken):
    """Handle creating user Authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class Users(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        users = UserSerializer(User.objects.all(), many=True)
        return Response(users.data)

    def post(self, request, format=None):
        user = UserSerializer(data=json.loads(request.body))
        if user.is_valid():
            created_user = user.create(user.validated_data)
            created_user = UserSerializer(created_user)
            return Response({'user_data': created_user.data}, status=status.HTTP_201_CREATED)
        else:
            errors = []
            error_fields = list(user.errors.keys())
            for error in error_fields:
                errors.append({
                    error: user.errors.get(error)[0]
                })
            return Response({'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def patch(self, request, format=None):
        data = json.loads(request.body)

        if 'id' not in list(data.keys()):
            return Response({'error': 'no id was provided to update'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if 'data_to_update' not in list(data.keys()):
            return Response({'error': 'data to update missing'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user = User.objects.get(pk=data.get('id', None))
        update_data = data.get('data_to_update')
        fields = list(update_data.keys())

        if 'password' in fields:
            user.set_password(update_data.get('password'))
            if len(fields) == 1:
                user.save()
                return Response({'updated': True}, status=status.HTTP_202_ACCEPTED)
            fields = list(set(fields) - {'password'})

        if 'email' in fields:
            user_by_email = User.objects.filter(
                email=update_data.get('email')).first()
            print(user_by_email, update_data.get('email'))
            if user_by_email:
                return Response({'error': 'E-Mail already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if 'mobile' in fields:
            user_by_mobile = User.objects.filter(
                mobile=update_data.get('mobile')).first()
            if user_by_mobile:
                return Response({'error': 'Mobiles already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        user.email = update_data.get('email', user.email)
        user.initial = update_data.get('initial', user.initial)
        user.firstname = update_data.get('firstname', user.firstname)
        user.lastname = update_data.get('lastname', user.lastname)
        user.mobile = update_data.get('mobile', user.mobile)
        user.is_superuser = update_data.get('is_superuser', user.is_superuser)
        user.is_staff = update_data.get('is_staff', user.is_staff)
        user.is_active = update_data.get('is_active', user.is_active)

        user.save()
        return Response({'updated': True}, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, format=None):
        data = json.loads(request.body)

        if 'id' not in list(data.keys()):
            return Response({'error': 'Id not provided to delete'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        user_to_delete = User.objects.get(pk=data.get('id', None))
        user_to_delete.delete()
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class UserProfile(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, RetrieveOwnProfile]

    def get(self, request, format=None):
        requested_user = ProfilesSerializer(request.user)
        return Response({'user': requested_user.data})

    def post(self, request, format=None):
        update_data = json.loads(request.body)
        user = request.user

        fields = list(update_data.keys())

        if 'password' in fields:
            user.set_password(update_data.get('password'))
            if len(fields) == 1:
                user.save()
                user_data = ProfilesSerializer(user)
                return Response({'updated': True, 'user_data': user_data.data}, status=status.HTTP_202_ACCEPTED)
            fields = list(set(fields) - {'password'})

        if 'email' in fields and user.email != update_data.get('email'):
            user_by_email = User.objects.filter(
                email=update_data.get('email')).first()
            print(user_by_email, update_data.get('email'))
            if user_by_email:
                return Response({'error': 'E-Mail already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if 'mobile' in fields and user.mobile != update_data.get('mobile'):
            user_by_mobile = User.objects.filter(
                mobile=update_data.get('mobile')).first()
            if user_by_mobile:
                return Response({'error': 'Mobiles already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        user.email = update_data.get('email', user.email)
        user.initial = update_data.get('initial', user.initial)
        user.firstname = update_data.get('firstname', user.firstname)
        user.lastname = update_data.get('lastname', user.lastname)
        user.mobile = update_data.get('mobile', user.mobile)

        user.save()

        user_data = ProfilesSerializer(user)

        return Response({
            'updated': True,
            'user_data': user_data.data
        }, status=status.HTTP_202_ACCEPTED)


class UserAddresses(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, RetrieveOwnProfile]

    def get(self, request, format=None):
        addresses = UserAddress.objects.filter(user=request.user)
        addresses = UserAddressSerializer(addresses, many=True)
        return Response({
            'addresses': addresses.data,
        }, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data = json.loads(request.body)
        address_to_add = UserAddressSerializer(data=data)
        if address_to_add.is_valid():
            address = address_to_add.save(user=request.user)
            address = UserAddressSerializer(address)
            return Response({
                'address': address.data,
            }, status=status.HTTP_201_CREATED)
        else:
            errors = []
            error_fields = list(address_to_add.errors.keys())
            for error in error_fields:
                errors.append({
                    error: address_to_add.errors.get(error)[0]
                })
            return Response({'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def put(self, request, format=None):
        data = json.loads(request.body)

        if 'id' not in list(data.keys()):
            return Response({'error': 'no id was provided to update'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if 'data_to_update' not in list(data.keys()):
            return Response({'error': 'data to update missing'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        address = UserAddress.objects.get(pk=data.get('id', None))
        update_data = data.get('data_to_update')

        address.name = update_data.get('name', address.name)
        address.contact_name = update_data.get(
            'contact_name', address.contact_name)
        address.contact_mobile = update_data.get(
            'contact_mobile', address.contact_mobile)
        address.line1 = update_data.get('line1', address.line1)
        address.line2 = update_data.get('line2', address.line2)
        address.line3 = update_data.get('line3', address.line3)
        address.landmark = update_data.get('landmark', address.landmark)
        address.district = update_data.get('district', address.district)
        address.state = update_data.get('state', address.state)
        address.pincode = update_data.get('pincode', address.pincode)
        address.type = update_data.get('type', address.type)

        address.save()
        address_data = UserAddressSerializer(address)

        return Response({
            'updated': True,
            'address_data': address_data.data
        }, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, format=None):
        data = json.loads(request.body)
        if 'id' not in list(data.keys()):
            return Response({'error': 'Id not provided to delete'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        address_to_delete = UserAddress.objects.get(id=data.get('id', None))
        print(address_to_delete)
        address_to_delete.delete()
        return Response({'deleted': True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def regiester_user(request, format=None):
    data = json.loads(request.body)
    user_to_be_created = ProfilesSerializer(data=data)
    if user_to_be_created.is_valid():
        created_user = user_to_be_created.create(
            user_to_be_created.validated_data)
        token = Token.objects.create(user=created_user)
        created_user = UserSerializer(created_user)
        return Response({'user_data': created_user.data, 'token': token.key}, status=status.HTTP_201_CREATED)
    else:
        errors = []
        error_fields = list(user_to_be_created.errors.keys())
        for error in error_fields:
            errors.append({
                error: user_to_be_created.errors.get(error)[0]
            })
        return Response({'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, RetrieveOwnProfile])
@authentication_classes([authentication.TokenAuthentication])
def logout(request, format=None):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def validate_mobile(request, format=None):
    data = json.loads(request.body)
    if 'mobile' not in list(data.keys()):
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_by_mobile = User.objects.filter(mobile=data.get('mobile')).first()
    if user_by_mobile:
        return Response(status=status.HTTP_409_CONFLICT)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def validate_email(request, format=None):
    data = json.loads(request.body)
    if 'email' not in list(data.keys()):
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_by_email = User.objects.filter(email=data.get('email')).first()
    if user_by_email:
        return Response(status=status.HTTP_409_CONFLICT)
    return Response(status=status.HTTP_200_OK)
