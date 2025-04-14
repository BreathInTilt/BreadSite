from django.conf import settings
from django.conf.urls.static import static



from django.urls import path
from . import views

urlpatterns = [
    path('', views.bread_list, name='bread_list'),
    path('bread/<int:bread_id>/', views.bread_detail, name='bread_detail'),
    path('add_to_cart/<int:bread_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('order_success/', views.order_success, name='order_success'),
    path('about_us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
