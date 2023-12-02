
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    # path('detail/', views.product_detail, name='product_detail'),
    path('products/', views.product_list, name='product_list'),
    # path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_product/', views.add_product, name='add_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-quantity/<int:cart_item_id>/', views.update_cart_quantity, name='update_cart_quantity'),


    path('checkout/', views.checkout_view, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),

    path('pay/', views.pay, name='pay'),
    path('token/', views.token, name='token'),
    path('stk/', views.stk, name='stk'),
    path('payment/', views.payment_page, name='payment_page'),
    # path('payment-success/', views.payment_success, name='payment_success'),  # Create this view if needed


    # path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    # Other URL patterns...
    # Add URLs for filtered product list and other functionalities

    # filtered product list
    path('products/', views.filtered_product_list, name='filtered_product_list'),
    path('filter/', views.filtered_product_list, name='filtered_product_list'),

    path('product/<int:product_id>/', views.update_product_status, name='update_product'),
    path('filtered-products/', views.filtered_product_list, name='filtered_product_list'),
    path('filtered-products_2/', views.filtered_product_list_2, name='filtered_product_list_2'),

    path('services/', views.services, name='services'),
    path('shop/', views.shop, name='shop'),
    path('inner/', views.inner, name='inner'),

    path('login/', views.user_login, name='user_login'),
    path('register/', views.registration, name='registration'),


    path('contact/', views.contact, name='contact'),
    path('ky/', views.ky, name='ky'),
    path('ion/', views.ion, name='ion'),
    path('neew/', views.neew, name='neew'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('reach/', views.contact_view, name='contact'),
    path('success_page', views.success_page, name='success_page'),
    path('mpesa_success', views.mpesa_success, name='mpesa_success'),
    path('logout/', views.logout_view, name='logout'),
    # path('receipt/<str:transaction_id>/', generate_receipt, name='generate_receipt'),
    # Other URLs...
]
