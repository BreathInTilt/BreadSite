from django import forms
from .models import Order, Review

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'phone', 'address']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user_name', 'rating', 'comment']
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-input rounded-xl border-[#e5e0dc] text-sm px-2 py-1', 'placeholder': 'Ваше имя'}),
            'rating': forms.NumberInput(attrs={'class': 'form-input rounded-xl border-[#e5e0dc] text-sm px-2 py-1', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-textarea rounded-xl border-[#e5e0dc] text-sm px-2 py-1', 'rows': 4, 'placeholder': 'Ваш отзыв'}),
        }