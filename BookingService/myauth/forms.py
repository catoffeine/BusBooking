from django.core.exceptions import ValidationError

from .models import Company, User, Client, Driver
from django.forms import ModelForm, TextInput, CharField, PasswordInput, Form, FileField, FileInput, Textarea
from django.contrib.auth.forms import PasswordChangeForm

from booking.models import Bus


def txtw(placeholder):
    return TextInput(attrs={
        'class': 'form-control',
        'placeholder': placeholder})


def txta(placeholder):
    return Textarea(attrs={
        'class': 'form-control',
        'placeholder': placeholder})


class PhoneInput(Form):
    phone = CharField(label="Телефон", max_length=15, widget=TextInput(attrs={
        'class': 'form-control phone_input',
        'placeholder': '+71234567890',   
    }))


class PhoneAndPasswordInput(Form):
    phone = CharField(label="Телефон", max_length=15, widget=TextInput(attrs={
        'class': 'form-control phone_input',
        'placeholder': '+71234567890',
    }))
    password = CharField(label="Пароль", max_length=100, widget=txtw('Пароль'))


class CodeInput(Form):
    code = CharField(label="Код", max_length=4, widget=TextInput(attrs={
        'class': 'form-control',
        'placeholder': '****',
        'type': 'number'
    }))


class EmailInput(Form):
    email = CharField(label="Почта", max_length=100, widget=txtw('Почта'))


class MetaUserRegistrationForm(ModelForm):
    """A form for meta-user account registration and authorisation"""

    class Meta:
        model = User
        fields = ["email", "password"]
        widgets = {
            "email": txtw('Почта'),
            "password": txtw('Пароль')
        }

    def save(self, commit=True, role='client'):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.role = role
        user.set_password(self.data["password"])
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super(MetaUserRegistrationForm, self).clean()
        password = cleaned_data.get('password')

        # check for min length
        min_length = 8
        if len(password) < min_length:
            msg = 'Пароль должен содержать минимум %s символов' % (str(min_length))
            self.add_error('password', msg)

        # check for digit
        if sum(c.isdigit() for c in password) < 1:
            msg = 'В пароле должна быть как минимум 1 цифра'
            self.add_error('password', msg)

        # check for uppercase letter
        if not any(c.isupper() for c in password):
            msg = 'В пароле должна быть хотя-бы одна заглавная буква'
            self.add_error('password', msg)

        # check for lowercase letter
        if not any(c.islower() for c in password):
            msg = 'В пароле должна быть хотя-бы одна строчная буква'
            self.add_error('password', msg)
        return cleaned_data


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].widget = txtw('Пароль')


class ClientChangeForm(ModelForm):
    class Meta:
        model = Client
        fields = ['name',
                  'surname',
                  'middlename',
                  'passport_series',
                  'passport_number',
                  'email',
                  'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget = txtw(field_name)


class DriverChangeForm(ModelForm):
    class Meta:
        model = Driver
        fields = ['surname', 'name', 'middlename', 'passport_series', 'passport_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget = txtw(field_name)


class CompanyChangeForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget = txtw(field_name)


class UploadFileForm(Form):
    file = FileField(widget=FileInput(attrs={'class': 'form-control'}))
