from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path(r'logout', views.logout_page, name='logout'),
    path(r'about', views.about_page, name='about'),
    path(r'code', views.enter_code_page, name='code'),
    path(r'auth/<role>/<action>', views.auth_page, name='auth'),
    path(r'auth-partners', views.auth_partners_page, name='auth-partners'),
    path(r'set-new-password', views.set_new_password, name='set-new-password'),
    path(r'set-new-email', views.set_new_email, name='set-new-email'),
    path(r'profile', views.profile_page, name='profile'),
    path(r'upload-docs', views.load_documents_page, name='upload-docs'),
    path(r'return-policy', views.return_policy_page, name='return-policy'),
    path(r'oferta', views.oferta_page, name='oferta'),
    path(r'rules', views.rules_page, name='rules'),
]
