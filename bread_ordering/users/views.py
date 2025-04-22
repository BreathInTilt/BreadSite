from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django_telegram_login.authentication import verify_telegram_authentication

def login_view(request):
    return render(request, 'users/login.html', {
        'TELEGRAM_BOT_NAME': settings.TELEGRAM_BOT_NAME,
        'TELEGRAM_LOGIN_REDIRECT_URL': settings.TELEGRAM_LOGIN_REDIRECT_URL,
    })

def telegram_callback(request):
    # Проверяем, присутствует ли параметр 'hash' в запросе
    if not request.GET.get('hash'):
        return HttpResponse("Handle the missing Telegram data in the response.", status=400)

    telegram_data = request.GET.dict()

    try:
        # Проверяем подлинность данных Telegram
        result = verify_telegram_authentication(bot_token=settings.TELEGRAM_BOT_TOKEN, request_data=request.GET)
    except ValueError as e:
        # В версии 0.2.3 все ошибки проверки выбрасываются как ValueError
        # Мы можем частично различать ошибки по тексту сообщения
        error_message = str(e).lower()
        if "data is outdated" in error_message:
            return HttpResponse("Authentication was received more than a day ago.", status=403)
        return HttpResponse(f"Authorization failed: {str(e)}", status=403)

    if not result:
        return HttpResponse("Authorization failed: Invalid data", status=403)

    # Извлекаем данные пользователя
    telegram_id = telegram_data.get('id')
    first_name = telegram_data.get('first_name', '')
    last_name = telegram_data.get('last_name', '')
    username = telegram_data.get('username', f'tg_{telegram_id}')

    # Находим или создаём пользователя
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': first_name, 'last_name': last_name}
    )

    # Авторизуем пользователя
    login(request, user)
    return HttpResponse(f"Welcome, {first_name}! You are now logged in.")