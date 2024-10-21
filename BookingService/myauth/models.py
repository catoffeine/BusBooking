import json
import os

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe


class MyAccountManager(BaseUserManager):
    def create_user(self, phone, password, role):
        if not phone:
            raise ValueError('Users must have an email address')

        user = self.model(
            phone=phone,
            password=password,
            role=role
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password):
        user = self.create_user(
            phone=phone,
            password=password,
            role='ADMIN'
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Meta:
        verbose_name = 'аккаунт'
        verbose_name_plural = 'аккаунты'

    id = models.AutoField(primary_key=True)
    # USER_ROLES = (
    #     ('driver', 'DRIVER'),
    #     ('client', 'CLIENT'),
    #     ('company', 'COMPANY'),
    #     ('admin', 'ADMIN')
    # )
    # role = models.CharField(max_length=10, choices=USER_ROLES, default='client')
    role = models.CharField(max_length=10, default='client')

    email = models.TextField(blank=True, null=True, unique=True)
    phone = models.TextField(blank=True, null=True, unique=True)

    USERNAME_FIELD = 'phone'
    objects = MyAccountManager()

    def __str__(self):
        try:
            cl = Client.objects.get(auth_profile=self)
            return str(cl)
        except Client.DoesNotExist:
            pass

        try:
            d = Driver.objects.get(auth_profile=self)
            return str(d)
        except Driver.DoesNotExist:
            pass

        try:
            comp = Company.objects.get(auth_profile=self)
            return str(comp)
        except Company.DoesNotExist:
            pass

        return f"{self.phone}"

    @staticmethod
    def has_perm(perm, obj=None, **kwargs):
        return True

    @staticmethod
    def has_module_perms(app_label, **kwargs):
        return True

    @property
    def is_staff(self):
        return self.role in ('ADMIN', 'admin')

    @admin.display(description='Роль')
    def html_role(self):
        r = self.role.lower().strip()
        color = {'admin': 'red', 'client': 'black', 'driver': 'orange', 'company': 'orange'}
        return mark_safe(f"<p style='color: {color[r]}; margin: 0; padding: 0'>{r}</p>")


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    royalty_percent = models.FloatField(blank=True, null=True, default=0)
    name = models.TextField(unique=True)
    documents_verified = models.BooleanField(default=False, blank=True, null=True)
    documents_comment = models.TextField(blank=True, null=True)
    registration_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    auth_profile = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.TextField(blank=True, null=True, unique=True)
    phone = models.TextField(blank=True, null=True, unique=True)

    @admin.display(description='Документы')
    def docs_status(self):
        d_name = f'user_files/{self.id}_company'
        url = f'/admin/filebrowser/browse/?&dir={self.id}_company'
        if self.documents_verified:
            return mark_safe("<p style='color:green; padding: 0; margin:0;'>Документы проверены</p>")
        else:
            if self.documents_comment not in ('', None):
                return mark_safe("<p style='color:orange; padding: 0; margin:0;'>Ошибка в документах</p>")
            elif (os.path.isdir(d_name) and len(os.listdir(d_name)) == 0) or not os.path.isdir(d_name):
                return mark_safe("<p style='color:red; padding: 0; margin:0;'>Компания не предоставила документы</p>")
            else:
                return mark_safe(f"<a href='{url}' target='_blank'>Документы на проверке</a>")

    @admin.display(description='Роялти')
    def royalty_percent_adm(self):
        return f'{self.royalty_percent}%'

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'


class Client(models.Model):
    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    id = models.AutoField(primary_key=True)
    surname = models.TextField()
    name = models.TextField(blank=True,
                            null=True)
    middlename = models.TextField(blank=True,
                                  null=True)
    passport_series = models.TextField(blank=True,
                                       null=True)
    passport_number = models.TextField(blank=True,
                                       null=True)
    registration_datetime = models.DateTimeField(auto_now_add=True, blank=True,
                                                 null=True)

    auth_profile = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    email = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fio()

    @admin.display(description='ФИО')
    def fio(self):
        return f'{self.surname} {self.name} {self.middlename}'

    @admin.display(description='Телефон')
    def ph(self):
        return str(self.auth_profile.phone)

    @admin.display(description='Почта')
    def em(self):
        return str(self.auth_profile.email)


class Driver(models.Model):
    id = models.AutoField(primary_key=True)
    surname = models.TextField()
    name = models.TextField(blank=True, null=True)
    middlename = models.TextField(blank=True, null=True)
    passport_series = models.TextField(blank=True, null=True)
    passport_number = models.TextField(blank=True, null=True)
    registration_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    documents_comment = models.TextField(blank=True, null=True)
    documents_verified = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)
    auth_profile = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fio()

    @admin.display(description='ФИО')
    def fio(self):
        return f'{self.surname} {self.name} {self.middlename}'

    @admin.display(description='Телефон')
    def ph(self):
        return str(self.auth_profile)

    class Meta:
        verbose_name = 'водитель'
        verbose_name_plural = 'водители'

    @admin.display(description='Документы')
    def docs_status(self):
        d_name = f'user_files/{self.id}_driver'
        url = f'/admin/filebrowser/browse/?&dir={self.id}_driver'
        if self.documents_verified:
            return mark_safe("<p style='color:green; padding: 0; margin:0;'>Документы проверены</p>")
        else:
            if self.documents_comment not in ('', None):
                return mark_safe("<p style='color:orange; padding: 0; margin:0;'>Ошибка в документах</p>")
            elif (os.path.isdir(d_name) and len(os.listdir(d_name)) == 0) or not os.path.isdir(d_name):
                return mark_safe("<p style='color:red; padding: 0; margin:0;'>Водитель не предоставил документы</p>")
            else:
                return mark_safe(f"<a href='{url}' target='_blank'>Документы на проверке</a>")

    @admin.display(description='Компания')
    def comp(self):
        if self.company is not None:
            return self.company.name
        return 'Самозанятый'


class Config(models.Model):
    class Meta:
        verbose_name = 'Конфигурационная переменная'
        verbose_name_plural = 'Конфигурационные переменные'

    variable_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=100, null=True, blank=True)
    value = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.variable_name


def GET_VAR(var_name, default=None):
    try:
        config = Config.objects.get(variable_name=var_name)
    except:
        return default
    return config.value


def load_default_config_vars():
    data = json.load(open('default_config_vars.json', mode='rb'))
    for var_name in data:
        try:
            confvar = Config.objects.get(variable_name=var_name)
        except:
            confvar = None
        if confvar is None:
            var = Config()
            var.variable_name = var_name
            var.value = data[var_name]['data']
            var.description = data[var_name]['desc']
            var.save()


def update_credentials_handler(sender, instance, **kwargs):
    """Handler to update creds in profiles"""
    if instance.auth_profile:
        if instance.email not in (None, '', ' '):
            instance.auth_profile.email = instance.email
        if instance.phone not in (None, '', ' '):
            instance.auth_profile.phone = instance.phone
        instance.auth_profile.save()


post_save.connect(update_credentials_handler, sender=Driver)
post_save.connect(update_credentials_handler, sender=Company)
post_save.connect(update_credentials_handler, sender=Client)
