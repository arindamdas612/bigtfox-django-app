def get_user_update_dict(request_dict, user_to_update):
    update_fields = ['email', 'mobile', 'initial', 'firstname',
                     'lastname', 'password', 'is_superuser', 'is_staff', 'is_active']
