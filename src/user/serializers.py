from rest_framework import serializers
from .models import User, UserAddress


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['groups', 'user_permissions']
        read_only_fields = ['created', 'modified']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            }
        }

    def create(self, validated_data):
        """Create and return a new user"""

        user = User.objects.create_user(
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            initial=validated_data['initial'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            password=validated_data['password'],
            is_superuser=validated_data['is_superuser'],
            is_staff=validated_data['is_staff'],
            is_active=validated_data['is_active'],
        )
        return user

    def update(self, user, validated_data):
        user.email = validated_data.get('email', user.email)
        user.mobile = validated_data.get('mobile', user.mobile)
        user.initial = validated_data.get('initial', user.initial)
        user.firstname = validated_data.get('firstname', user.firstname)
        user.lastname = validated_data.get('lastname', user.lastname)
        user.is_superuser = validated_data.get(
            'is_superuser', user.is_superuser)
        user.is_staff = validated_data.get('is_staff', user.is_staff)
        user.is_active = validated_data.get('is_active', user.is_active)

        user.save()

        return user


class ProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['is_superuser', 'is_staff', 'is_active', 'groups',
                   'user_permissions', 'last_login', 'created', 'modified']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            }
        }

    def create(self, validated_data):
        """Create and return a new user"""

        user = User.objects.create_user(
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            initial=validated_data['initial'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            password=validated_data['password']
        )
        return user


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ["id", "name", "contact_name", "contact_mobile", "line1", "line2", "line3",
                  "landmark", "district", "state", "pincode", "type", "created", "modified"]
        extra_kwargs = {
            'id': {'read_only': True},
            'created': {'read_only': True},
            'modified': {'read_only': True}
        }

    def save(self, *args, **kwargs):
        print(kwargs.get('user'))
        return super(UserAddressSerializer, self).save(*args, **kwargs)
