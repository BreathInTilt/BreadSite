from django.urls import path
from .views import login_view
from .views import login_view, telegram_callback

urlpatterns = [
    path('login/', login_view, name='login'),
    path('telegram/login/', login_view, name='telegram_login'),  # Добавьте этот маршрут
    path('telegram/callback/', telegram_callback, name='telegram_callback'),
]