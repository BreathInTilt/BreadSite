from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from .bot import send_telegram_notification
from .models import Bread, Order, UserProfile
from .forms import OrderForm, ReviewForm
import telegram
import asyncio
from decimal import Decimal
from django import forms
from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_orders')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    return render(request, 'orders/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

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
    bread = get_object_or_404(Bread, id=bread_id)
    reviews = bread.reviews.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')  # Перенаправляем на страницу логина
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.bread = bread
            review.save()
            return redirect('bread_detail', bread_id=bread.id)
    else:
        form = ReviewForm()

    return render(request, 'bread_ordering/bread_detail.html', {
        'bread': bread,
        'reviews': reviews,
        'form': form,
    })



def user_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    # Создаём список заказов с вычисленной стоимостью
    orders_with_total = []
    total_orders = orders.count()
    total_spent = 0
    for order in orders:
        order_total = order.bread.price * order.quantity  # Вычисляем стоимость заказа
        orders_with_total.append({
            'order': order,
            'total_price': order_total,
        })
        total_spent += order_total

    return render(request, 'orders/user_orders.html', {
        'orders': orders_with_total,
        'user': request.user,
        'total_orders': total_orders,
        'total_spent': total_spent,
    })

def confirm_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if not all([customer_name, phone, address]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('view_cart')

        for bread_id, item in cart.items():
            bread = Bread.objects.get(id=bread_id)
            order = Order.objects.create(
                bread=bread,
                quantity=item['quantity'],
                customer_name=customer_name,
                phone=phone,
                address=address,
                user=request.user if request.user.is_authenticated else None  # Сохраняем пользователя, если он авторизован
            )

        # Очищаем корзину
        request.session['cart'] = {}
        messages.success(request, "Order placed successfully!")
        return redirect('order_success')

    return redirect('view_cart')




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
    cart_items = []

    # Вычисляем элементы корзины и их стоимость
    total = 0
    for bread_id, item in cart.items():
        item['total_price'] = item['price'] * item['quantity']  # Добавляем поле с общей стоимостью элемента
        cart_items.append(item)
        total += item['total_price']

    return render(request, 'orders/view_cart.html', {
        'cart': cart_items,
        'total': total,
    })


def order_success(request):
    return render(request, 'orders/order_success.html', {})

def about_us(request):

    return render(request, 'orders/about_us.html')

def contact(request):

    return render(request, 'orders/contact.html')

