from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from .bot import send_telegram_notification
from .models import Bread, Order
from .forms import OrderForm, ReviewForm
import telegram
import asyncio
from decimal import Decimal

#'1195159042:AAGQgmkFczEb_nPpYRiPHdpdIDbk2SVhaF4'
#'712395220'


def bread_list(request):
    breads = Bread.objects.all()
    return render(request, 'orders/bread_list.html', {'breads': breads})

"""
def create_order(request, bread_id):
    bread = get_object_or_404(Bread, pk=bread_id)
    if request.method == 'POST':
        print("POST123")
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity_requested = form.cleaned_data['quantity']
            print("Form Valid")
            # Проверка доступности товара
            if bread.stock >= quantity_requested:
                # Уменьшение количества на складе
                bread.stock -= quantity_requested
                bread.save()

                # Сохранение заказа
                order = form.save()

                # Вызов асинхронной функции для отправки уведомления
                asyncio.run(send_telegram_notification(order))

                return redirect('order_success')
            else:
                # Отправляем сообщение об ошибке, если товара недостаточно
                messages.error(request, f"Недостаточно товара на складе. В наличии только {bread.stock} шт.")
        else:
            messages.error(request, "Ошибка в данных формы. Пожалуйста, проверьте введенные данные.")
    else:
        form = OrderForm(initial={'bread': bread})

    return render(request, 'orders/create_order.html', {'form': form, 'bread': bread})
"""


def bread_detail(request, bread_id):
    bread = get_object_or_404(Bread, pk=bread_id)

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.bread = bread
            review.save()
            messages.success(request, "Ваш отзыв успешно добавлен!")
            return redirect('bread_detail', bread_id=bread_id)
    else:
        review_form = ReviewForm()

    reviews = bread.reviews.all()  # Получаем все отзывы для данного хлеба
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']  # Средний рейтинг
    if average_rating is not None:
        average_rating = round(average_rating, 1)  # Округляем до 1 знака после запятой
    else:
        average_rating = 0  # Если отзывов нет, средний рейтинг = 0

    return render(request, 'orders/bread_detail.html', {
        'bread': bread,
        'reviews': reviews,
        'review_form': review_form,
        'average_rating': average_rating
    })


def confirm_order(request):
    cart = request.session.get('cart', {})

    # Проверяем, пуста ли корзина
    if not cart:
        messages.error(request, "Корзина пуста.")
        return redirect('view_cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            orders = []
            # Перебираем все товары в корзине и создаем заказы
            for bread_id, item in cart.items():
                bread = get_object_or_404(Bread, pk=bread_id)
                quantity = item['quantity']

                # Проверка наличия достаточного количества на складе
                if bread.stock >= quantity:
                    bread.stock -= quantity
                    bread.save()

                    # Создание записи заказа
                    order = Order.objects.create(
                        bread=bread,
                        customer_name=form.cleaned_data['customer_name'],
                        phone=form.cleaned_data['phone'],
                        address=form.cleaned_data['address'],
                        quantity=quantity
                    )
                    orders.append(order)


                else:
                    # Если недостаточно товара, отправляем сообщение об ошибке и перенаправляем назад в корзину
                    messages.error(request, f"Недостаточно товара для {item['name']}.")
                    return redirect('view_cart')

            # Очистка корзины после успешного оформления
            asyncio.run(send_telegram_notification(orders))
            request.session['cart'] = {}
            messages.success(request, "Ваш заказ был успешно оформлен.")
            return redirect('order_success')
        else:
            messages.error(request, "Пожалуйста, заполните все поля корректно.")
    else:
        # Создаем начальные данные для формы, если это GET запрос
        form = OrderForm()

    return render(request, 'orders/create_order.html', {'form': form, 'cart': cart})




def add_to_cart(request, bread_id):
    bread = get_object_or_404(Bread, pk=bread_id)
    quantity = int(request.POST.get('quantity', 1))

    # Проверка наличия достаточного количества на складе
    if bread.stock < quantity:
        messages.error(request, f"Недостаточно товара на складе. В наличии только {bread.stock} шт.")
        return redirect('bread_list')

    # Получение текущей корзины из сессии
    cart = request.session.get('cart', {})

    if str(bread_id) in cart:
        # Если хлеб уже в корзине, проверяем, не превышает ли новое количество доступный запас
        new_quantity = cart[str(bread_id)]['quantity'] + quantity
        if bread.stock < new_quantity:
            messages.error(request, f"Недостаточно товара на складе. В наличии только {bread.stock} шт.")
            return redirect('bread_list')
        cart[str(bread_id)]['quantity'] = new_quantity
    else:
        # Добавляем хлеб в корзину
        cart[str(bread_id)] = {
            'name': bread.name,
            'price': float(bread.price),  # Преобразуем Decimal в float
            'quantity': quantity
        }

    # Сохраняем корзину в сессии
    request.session['cart'] = cart
    messages.success(request, f'{bread.name} добавлен в корзину.')

    return redirect('bread_list')

def view_cart(request):
    cart = request.session.get('cart', {})

    # Проверяем, пуста ли корзина
    if not cart:
        messages.error(request, "Корзина пуста.")
        return redirect('bread_list')

    return render(request, 'orders/view_cart.html', {'cart': cart})


def order_success(request):

    return render(request, 'orders/order_success.html')

def about_us(request):

    return render(request, 'orders/about_us.html')

def contact(request):

    return render(request, 'orders/contact.html')

