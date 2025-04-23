from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import NotTelegramDataError, TelegramDataIsOutdatedError

def login_view(request):
    return render(request, 'users/login.html', {
        'TELEGRAM_BOT_NAME': settings.TELEGRAM_BOT_NAME,
        'TELEGRAM_LOGIN_REDIRECT_URL': settings.TELEGRAM_LOGIN_REDIRECT_URL,
    })

def telegram_callback(request):
    if not request.GET.get('hash'):
        return HttpResponse("Handle the missing Telegram data in the response.", status=400)

    try:
        telegram_data = verify_telegram_authentication(
            bot_token=settings.TELEGRAM_BOT_TOKEN,
            request_data=request.GET
        )
    except TelegramDataIsOutdatedError:
        return HttpResponse("Authentication was received more than a day ago.", status=403)
    except NotTelegramDataError:
        return HttpResponse("The data is not related to Telegram!", status=403)

    telegram_id = telegram_data.get('id')
    first_name = telegram_data.get('first_name', '')
    last_name = telegram_data.get('last_name', '')
    username = telegram_data.get('username', f'tg_{telegram_id}')

    user, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': first_name, 'last_name': last_name}
    )

    # Указываем бэкенд аутентификации
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # Проверяем, заполнены ли имя и фамилия
    if not user.first_name or not user.last_name:
        return redirect('profile_edit')

    return HttpResponse(f"Welcome, {first_name}! You are now logged in.")