from django.contrib import admin
from django.db import models

from .models import Category, Product, Cart, Member, ContactMessage, Payment
from django.contrib.auth.models import User  # Import User model if not already imported
from django.db.models import Sum  # Import Sum function from django.db.models



class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'category', 'image']
    # Add other configurations as needed



class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'timestamp')
    list_display_links = ('name', 'subject')  # Make these fields clickable
    list_filter = ('timestamp',)  # Add a filter for the timestamp field

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'get_total_amount_paid')  # Include the new method in list_display
    list_display_links = ('user', 'product')
    list_filter = ('user', 'product')

    def get_total_amount_paid(self, obj):
        total_amount_paid = Payment.objects.filter(user=obj.user).aggregate(total=models.Sum('amount'))
        return total_amount_paid['total'] if total_amount_paid['total'] else 0

    get_total_amount_paid.short_description = 'Total Amount Paid'  # Set the column header name

class PaymentAdmin(admin.ModelAdmin):
        list_display = ('user', 'cart', 'amount', 'phone')
        list_filter = ('user',)  # Add filters as needed


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Member)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(Payment, PaymentAdmin)

