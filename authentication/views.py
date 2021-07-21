# -*- encoding: utf-8 -*-
import json
from urllib.parse import unquote 

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from firebase_admin import auth
import firebase_admin
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import LoginForm, SignUpForm
 
def firebase_logout(request):
    logout(request)
    return redirect(settings.REPUSTATE_WEBSITE)

def logout_view(request):
    logout(request)
    if settings.REPUSTATE_LOGIN:
        return redirect(settings.REPUSTATE_WEBSITE + "/firebase-logout/")
    return redirect("/")
        

def login_view(request):
    if request.user.is_authenticated:
        return redirect("/project/")
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
            
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('project')
        else:
            msg = 'Invalid credentials'
    context = {
        "form": form, "msg": msg,
        'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
        'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
        'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
        'FIREBASE_STORAGE_BUKCET': settings.FIREBASE_STORAGE_BUKCET,
        'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
        'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
    }
    return render(request, "accounts/login.html", context)


def register_user(request):

    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

def guest_login(request):
    """
    Automatically sign a user in under the guest@repustate.com account and
    potentially redirect them to a sample project.
    """
    logout(request)
    user = authenticate(username='guest@repustate.com', password='')
    login(request, user)

    if request.GET.get('project'):
        return redirect(reverse("project", kwargs={'project_id':request.GET['project']}))

    return redirect(reverse("project"))

@csrf_exempt
def firebase_login(request):
    
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    token = body["token"]
    decoded_token = auth.verify_id_token(token)
    email = decoded_token["email"]
    user, created = User.objects.get_or_create(username=email)
    if created:
        user.set_password(User.objects.make_random_password())
        user.save()
    
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    if settings.REPUSTATE_LOGIN:
        return JsonResponse({'url':settings.REPUSTATE_WEBSITE + "/firebase-login-api/?token=" + token})

    return JsonResponse({'url': reverse('project')})

@csrf_exempt
def firebase_login_api(request):
    """
    endpoint used by repustate to login in both websites
    """
    token = request.GET.get("token","")
    redirect_path = unquote(request.GET.get("redirect", "/"))
    decoded_token = auth.verify_id_token(token)
    email = decoded_token["email"]
    user, created = User.objects.get_or_create(username=email)
    if created:
        user.set_password(User.objects.make_random_password())
        user.save()
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    return redirect(settings.REPUSTATE_WEBSITE + redirect_path)

