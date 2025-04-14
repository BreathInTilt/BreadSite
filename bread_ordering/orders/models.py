from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Bread(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.TextField(blank=True)  # Новое поле для ингредиентов
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='breads/', blank=True, null=True)  # Поле для изображения

    def __str__(self):
        return self.name


class Review(models.Model):
    bread = models.ForeignKey(Bread, on_delete=models.CASCADE, related_name='reviews')
    user_name = models.CharField(max_length=100)  # Имя пользователя
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]  # Рейтинг от 1 до 5
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.bread.name} ({self.rating})"

class Order(models.Model):
    bread = models.ForeignKey(Bread, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"
