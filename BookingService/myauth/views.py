import os
import random
import uuid
import requests
from os.path import isfile, join

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import MetaUserRegistrationForm, PhoneInput, PhoneAndPasswordInput, CodeInput, ChangePasswordForm, \
    ClientChangeForm, DriverChangeForm, CompanyChangeForm, UploadFileForm, EmailInput
from .models import User, Client, Driver, Company, GET_VAR
from booking.models import Bus, Trip, Route

from email_worker import send_email

from booking.forms import TicketSearchForm
from myauth.models import load_default_config_vars

WAITING_CODE = {}


def get_user_form(request):
    form_class, model = {'client': (ClientChangeForm, Client),
                         'driver': (DriverChangeForm, Driver),
                         'company': (CompanyChangeForm, Company)}.get(request.user.role, (None, None))
    return form_class


def anonymous_required(func):
    """Decoreator for redirecting already logged in users"""

    def as_view(request, *args, **kwargs):
        redirect_to = '/'
        if request.user.is_authenticated:
            return redirect(redirect_to)
        response = func(request, *args, **kwargs)
        return response

    return as_view


def check_everything(view_func):
    """ Decorator for checking everything for logged in users """

    def check_req(req):
        return all(el not in req.get_full_path() for el in [
            'set-new-password',
            'set-new-email'

        ])

    def wrapper(request, *args, **kwargs):

        # If user is logged in
        if request.user.is_authenticated:
            # If user hasn't setted strong password or somehow his password was empty
            if request.user.password in (None, '') and check_req(request):
                return redirect('set-new-password')
            if request.user.email in (None, '') and check_req(request):
                return redirect('set-new-email')
            ...

            return view_func(request, *args, **kwargs)
        elif request.path == "/":
            return view_func(request, *args, **kwargs)
        else:
            return redirect('index')

    return wrapper


def send_code(phone):
    """ Function to send auth code via sms """
    global WAITING_CODE
    new_code = random.randint(1000, 9999)
    WAITING_CODE[phone] = str(new_code)
    sms_text = f'Код авторизации: {new_code}'
    print(phone, sms_text)
    # resp = requests.get(
    #     f"https://ssl.cdfbs00.ru/?method=push_msg&email=dpolunchukov@gmail.com&password=88GcUfbe9u&text={sms_text}&phone={phone}&sender_name=RussiaLike")
    return new_code


def about_page(request):
    if request.method == 'POST':
        form = TicketSearchForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            from_f = form.cleaned_data['from_f']
            to_f = form.cleaned_data['to_f']
            # trips = find_suitable_trips(date, from_f, to_f)
            trips = Trip.objects.all()

            return render(request, 'view-trips.html', {'trips': trips,
                                                       'from_f': from_f.capitalize(),
                                                       'to_f': to_f.capitalize(),
                                                       'date': date})
    else:
        form = TicketSearchForm()
    return render(request, 'about.html', {'form': form})


@check_everything
def index_page(request):
    """ Welcome landing page """
    load_default_config_vars()  # First time after init
    try:
        if request.user.role.lower() == 'admin':
            return redirect('/admin')
    except:
        pass
    return render(request, 'index.html')


@anonymous_required
def enter_code_page(request):
    """ Entering code page for registration """
    phone = request.COOKIES.get('registration_phone')
    role = request.COOKIES.get('registration_role')

    # Check if user hasn't manually changed cookie value to log in on different phone
    if authenticate(username=phone, check=True) is not None \
            or role not in ('driver', 'client'):
        return redirect('index')

    form = CodeInput()
    if request.method == 'POST':
        form = CodeInput(request.POST)
        code = form.data['code']
        if str(code) == str(WAITING_CODE.get(phone)):
            new_user = User()
            new_user.role = role
            new_user.phone = phone
            new_user.save()
            if role == 'client':
                client_profile = Client()
                client_profile.auth_profile = new_user
                client_profile.email = new_user.email
                client_profile.save()
            elif role == 'driver':
                driver_profile = Driver()
                driver_profile.auth_profile = new_user
                driver_profile.email = new_user.email
                driver_profile.save()
            login(request, new_user)
            return redirect('index')
        else:
            form.add_error('code', 'Неправильный код')
    return render(request, 'register_person_code.html', {'phone': phone, 'form': form, 'code': str(WAITING_CODE.get(phone))})


@anonymous_required
def auth_page(request, role, action):
    """ Login and registration endpoints for all roles """

    header_text = {'company': 'для компаний', 'client': 'для клиентов', 'driver': 'для водителей'}.get(role)

    if role == 'company':
        # Registration endpoint
        form = MetaUserRegistrationForm()
        if action == 'registration':
            if request.method == 'POST':
                form = MetaUserRegistrationForm(request.POST)
                print(form.is_valid(), form.data)
                if form.is_valid():
                    comp_auth_acc = form.save(role=role)
                    new_company = Company()
                    new_company.auth_profile = comp_auth_acc
                    new_company.email = comp_auth_acc.email
                    new_company.save()
                    user = authenticate(request, form=form)
                    login(request, user)
                    return redirect('index')
            return render(request, 'auth_company.html', {'form': form, 'label': 'Регистрация',
                                                         'header_text': header_text, 'role': role})

        # Login endpoint
        elif action == 'login':
            if request.method == 'POST':
                form = MetaUserRegistrationForm(request.POST)
                user = authenticate(request, form=form)
                if user is not None:
                    login(request, user)
                    return redirect('index')
            return render(request, 'auth_company.html', {'form': MetaUserRegistrationForm(), 'label': 'Вход',
                                                         'header_text': header_text, 'role': role})
    elif role in ('client', 'driver', 'user'):

        # Login user by phone and password
        if action == 'login':
            if request.method == 'POST':
                form = PhoneAndPasswordInput(request.POST)
                user = authenticate(request, username=form.data['phone'], password=form.data['password'])
                if user:
                    login(request, user)
                    return redirect('index')
            return render(request, 'login_person.html',
                          {'role': role, 'header_text': header_text, 'form': PhoneAndPasswordInput()})

        # Register user with his phone number
        elif action == 'registration':
            form_to_response = PhoneAndPasswordInput()
            if request.method == 'POST':
                form = PhoneInput(request.POST)
                phone = form.data['phone']
                existing_user = authenticate(request, username=phone, check=True)

                # If not already registered
                if existing_user is None:
                    response = redirect('code')
                    response.set_cookie('registration_phone', phone, max_age=1000)
                    response.set_cookie('registration_role', role, max_age=1000)
                    send_code(phone)  # Sending code to user
                    return response
            return render(request, 'register_person_phone.html', {'role': role, 'form': form_to_response,
                                                                  'header_text': header_text})
    return redirect('index')


@anonymous_required
def auth_partners_page(request):
    return render(request, 'index_auth.html')


def logout_page(request):
    """ Logout page (WE DON'T NEED TO CHECK EVERYTHING BEFORE LOGOUT)"""
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')


@check_everything
def set_new_password(request):
    """ Page for updating password for already logged in user """
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        form.data.old_password = None
        form.is_valid()  # Add cleaned_data attr
        user = form.save()
        login(request, user)
        return redirect('index')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'set_new_password.html', {'form': form})


@check_everything
def set_new_email(request):
    """ Page for updating password for already logged in user """
    if request.method == 'POST':
        form = EmailInput(request.POST)
        email = request.POST.get('email')
        request.user.email = email
        user = request.user.save()
        login(request, user)
        return redirect('index')
    else:
        form = EmailInput(request.user)
    return render(request, 'set_new_email.html', {'form': form})


@check_everything
def profile_page(request):
    """ Profile page with """
    prefill_data = get_user_data(request)
    if request.method == 'POST':
        form = get_user_form(request)(request.POST, instance=prefill_data)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = get_user_form(request)(instance=prefill_data)
    return render(request, 'profile.html', {'form': form, 'label': 'Профиль'})


def handle_uploaded_file(f, path):
    with open(path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def get_user_data(request):
    form_class, model = {'client': (ClientChangeForm, Client),
                         'driver': (DriverChangeForm, Driver),
                         'company': (CompanyChangeForm, Company)}.get(request.user.role, (None, None))
    return model.objects.get(auth_profile=request.user)


@check_everything
def load_documents_page(request):
    obj = get_user_data(request)
    us = request.user
    if us.role == 'driver':
        docs = GET_VAR('driver-docs-list', '').split(',')
    elif us.role == 'company':
        docs = GET_VAR('company-docs-list', '').split(',')
    path_to_docs = f'user_files/{obj.id}_{request.user.role}'

    # Crete directory fith files if doesn't exist
    isExist = os.path.exists(path_to_docs)
    if not isExist:
        os.makedirs(path_to_docs)

    if request.method == "POST":
        fname = request.FILES['file'].name
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"], path_to_docs + '/' + fname)
            send_email(us, 'Document uploaded', f'You successfully uploaded {fname}')
            return redirect("upload-docs")
    else:
        form = UploadFileForm()

    onlyfiles = [f for f in os.listdir(path_to_docs) if isfile(join(path_to_docs, f))]
    docs_status = obj.documents_verified
    docs_comment = obj.documents_comment

    return render(request, 'load_documents.html',
                  {
                      'docs': docs,
                      'path_to_docs': path_to_docs,
                      'form': form,
                      'files': onlyfiles,
                      'docs_status': docs_status,
                      'docs_comment': docs_comment
                  })


def return_policy_page(request):
    return render(request, 'return-policy.html')


def oferta_page(request):
    return render(request, 'oferta.html')


def rules_page(request):
    return render(request, 'rules.html')
