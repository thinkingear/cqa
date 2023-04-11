from django.conf import settings

from account.forms import RegistrationForm, LoginForm
from django.shortcuts import redirect, render
from account.models import User
from django.contrib.auth import login, logout
from .backends import EmailBackend


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        # register: POST
        if form.is_valid():
            # register: form is valid
            user = form.save(commit=False)
            user.email = user.email.strip()
            user.password = user.password.strip()
            user.username = user.username.strip()

            user.save()
            login(request, user, backend=settings.EMAIL_BACKEND_PATH)
            return redirect('core:home')
        else:
            # register: form is not valid
            # print(form.errors)
            return render(request, 'account/register.html', {'form': form})
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            User.objects.get(email=email)
            user = EmailBackend.authenticate(request, email=email, password=password)

            if user is not None:
                print('login: authentication success')
                login(request, user, backend=settings.EMAIL_BACKEND_PATH)
                return redirect('core:home')
            else:
                print('login: authentication failed')
                form = LoginForm(request.POST)
                form.add_error('password', 'Email and/or Password incorrect')
        except User.DoesNotExist:
            print('login: user does not exist')
            form = LoginForm(request.POST)
            form.add_error('email', 'Email does not exist')

    else:
        form = LoginForm()

    print(form.errors)
    context = {'form': form}
    return render(request, 'account/login.html', context)


def logout_page(request):
    if not request.user.is_authenticated:
        return redirect('core:home')

    logout(request)
    return redirect('core:home')
