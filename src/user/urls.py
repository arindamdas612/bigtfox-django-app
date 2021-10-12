from django.urls import path

from .views import (
    UserLoginAPIView,
    Users,
    UserProfile,
    UserAddresses,
    regiester_user,
    logout,
    validate_email,
    validate_mobile,
)

urlpatterns = [
    path('login/', UserLoginAPIView.as_view()),
    path('logout/', logout),
    path('users/', Users.as_view()),
    path('users/register/', regiester_user),
    path('user/profile/', UserProfile.as_view()),
    path('users/validate-email/', validate_email),
    path('users/validate-mobile/', validate_mobile),
    path('user/address/', UserAddresses.as_view()),
]
