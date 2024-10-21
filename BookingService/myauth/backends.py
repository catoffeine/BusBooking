from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailPhoneUsernameAuthenticationBackend:
    @staticmethod
    def authenticate(request, username=None, password=None, form=None, check=False):
        if check:
            try:
                user = User.objects.get(
                    Q(phone=username) | Q(email=username)
                )
                print('FOUND', user)
                return user
            except User.DoesNotExist:
                print('NOT FOUND')
                return None
        if form is not None:
            email = form.data.get('email')
            phone = form.data.get('phone')
            password = form.data['password']
            try:
                if phone is None:
                    q = Q(email=email)
                if email is None:
                    q = Q(phone=phone)
                user = User.objects.get(
                    q
                )
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(
                    Q(phone=username) | Q(email=username)
                )
                print('FOUND', user)
            except User.DoesNotExist:
                print('NOT FOUND')
                return None
        if user and check_password(password, user.password):
            return user
        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def check_user_existance(username):
        try:
            user = User.objects.get(
                Q(phone=username) | Q(email=username)
            )
            print('FOUND', user)
        except User.DoesNotExist:
            print('NOT FOUND')
            return None
