import json
import base64

from django.contrib.sites import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart
from myapp.forms import ProductForm, ContactForm
# from myapp.formContact import ContactForm
from myapp.models import Member

from django.http import HttpResponse
from myapp.credentials import MpesaC2bCredential, MpesaAccessToken, LipanaMpesaPpassword
from requests.auth import HTTPBasicAuth

import requests
from .models import UserProfile

from django.template.loader import render_to_string
# from weasyprint import HTML  # WeasyPrint is used to generate PDFs from HTML (install it using pip)

from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth import logout
from django.contrib.auth import authenticate, login as auth_login  # Rename the login function alias




def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


# def product_detail(request, pk):
#     product = Product.objects.get(pk=pk)
#     return render(request, 'product_detail.html', {'product': product})

@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to the product list page after successful addition
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


# cart
@login_required(login_url='user_login')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        quantity = int(request.POST.get('quantity', 1))  # Default quantity is 1
        if quantity < 1:
            quantity = 1  # Ensure a minimum quantity of 1

        # Check if the product is already in the cart for the user
        cart_product = Cart.objects.filter(user=request.user, product=product).first()

        if cart_product:
            cart_product.quantity += quantity  # Increment quantity if the product is already in the cart
            cart_product.save()
        else:
            Cart.objects.create(user=request.user, product=product, quantity=quantity)

        return redirect('cart')  # Redirect to the cart page after adding the product

    # Handle GET requests or invalid cases here (if any)
    return redirect('product_list')  # Redirect to a suitable page if not a POST request


# @login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'cart.html', context)


# Other views for updating quantities, removing items from the cart, etc. would be needed

# removing from cart, and updating cart
# @login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    if cart_item.user == request.user:
        cart_item.delete()
    return redirect('cart')


# @login_required
def update_cart_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    if cart_item.user == request.user and request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
    return redirect('cart')


# checkout and payment
# @login_required
def checkout_view(request):
    # Retrieve cart items and calculate total
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    context = {
        'total': total
        # Include other necessary data for the checkout page
    }
    return render(request, 'checkout.html', context)


# def process_payment(request):
#     # Process payment logic here
#     # Access payment details from the submitted form (e.g., card number)
#     # Perform payment processing using a payment gateway or service
#
#     # After successful payment processing, update order status, create an order, etc.
#     # Redirect to a success or confirmation page
#     return redirect('payment_success')

# @login_required
def process_payment(request):
    if request.method == 'POST':
        # Retrieve the payment amount from the submitted form data
        amount = request.POST.get('amount')

        # Process the payment (This is a placeholder - implement your payment processing logic here)
        # For example, you might integrate with a payment gateway or service
        # Replace this with your actual payment processing logic
        payment_status = pay(amount)  # process_payment_function

        # If payment was successful
        if payment_status == 'success':
            # Perform actions after successful payment (e.g., update order status, send confirmation email, etc.)
            # Redirect to a success page or display a success message
            return HttpResponse('Payment Successful! Thank you for your purchase.')

        # If payment failed
        else:
            # Handle the failed payment scenario, such as showing an error message or redirecting to a failure page
            return HttpResponse('Payment Failed. Please try again or contact support.')

    # Handle cases other than POST requests (e.g., GET requests)
    return HttpResponse('Method not allowed')


# mpesa integration

def pay(request):
    return render(request, 'pay.html')


def token(request):
    consumer_key = '1SGNa4Lfy4YqQiL832A2OEGNYNBuNPQf'
    consumer_secret = 'R4BELOwVCGe2W2O1'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token": validated_mpesa_access_token})


def stk(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Apen Softwares",
            "TransactionDesc": "Web Development Charges"
        }
        response = requests.post(api_url, json=request, headers=headers)
        # return HttpResponse("Success")
        return redirect('mpesa_success')


def payment_page(request):
    # Fetch products in the user's cart
    cart_items = Cart.objects.filter(user=request.user)

    # Calculate the total amount by summing up subtotals of all cart items
    total_amount = sum(cart_item.subtotal() for cart_item in cart_items)

    return render(request, 'payment_page.html', {'total': total_amount})


# CRUD

# View to edit product details


# View to display product details


# working product details before changes

# def product_detail(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#
#     # Determine if the request came from the filtered product list
#     from_filtered_list = request.GET.get('from_filtered_list', False)
#
#     context = {
#         'product': product,
#         'from_filtered_list': from_filtered_list,
#     }
#
#     return render(request, 'product_detail.html', {'product': product})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Check if the 'from_filtered_list' parameter is present in the request's GET parameters
    from_filtered_list = request.GET.get('from_filtered_list', False)

    # Render the product detail template and pass the 'product' and 'from_filtered_list' context
    return render(request, 'product_detail.html', {'product': product, 'from_filtered_list': from_filtered_list})


@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product_id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})


@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def update_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        # active_status = request.POST.get('active_status')
        # Toggle the product's active status based on the form input
        if 'active_status' in request.POST:
            if request.POST['active_status'] == 'active':
                product.is_active = True
            else:
                product.is_active = False
            product.save()
            return redirect('product_detail', product_id=product_id)
    return render(request, 'update_product.html', {'product': product})


# def update_product_status(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     if request.method == 'POST':
#         active_status = request.POST.get('active_status')
#         if active_status == 'active':
#             product.is_active = True
#         else:
#             product.is_active = False
#         product.save()
#         return redirect('product_detail', product_id=product.id)
#     return render(request, 'update_product.html', {'product': product})


@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')  # Redirect to a suitable page after deletion
    return render(request, 'delete_product.html', {'product': product})


# filtered product list
def filtered_product_list(request):
    filtered_products = Product.objects.filter(is_active=True)
    return render(request, 'filtered_product_list.html', {'products': filtered_products})


# def filtered_product_list(request):
#     categories = ['women', 'men', 'shoes', 'watches']  # Sample categories
#     selected_category = request.GET.get('category')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#
#     products = Product.objects.all()
#
#     if selected_category in categories:
#         products = products.filter(category=selected_category)
#
#     if min_price:
#         products = products.filter(price__gte=min_price)
#
#     if max_price:
#         products = products.filter(price__lte=max_price)
#
#     context = {
#         'products': products,
#         'categories': categories,
#         'selected_category': selected_category,
#         'min_price': min_price,
#         'max_price': max_price,
#     }
#     return render(request, 'filtered_product_list.html', context)

# def filtered_product_list(request):
#     categories = ['women', 'men', 'shoes', 'watches']  # Sample categories
#     selected_category = request.GET.get('category')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#
#     products = Product.objects.all()
#
#     if selected_category in categories:
#         products = products.filter(category=selected_category)
#
#     if min_price:
#         products = products.filter(price__gte=min_price)
#
#     if max_price:
#         products = products.filter(price__lte=max_price)
#
#     # Assuming 'status' is the field representing active/inactive status
#     products = products.filter(status='active')  # Filter for 'active' status
#
#     context = {
#         'products': products,
#         'categories': categories,
#         'selected_category': selected_category,
#         'min_price': min_price,
#         'max_price': max_price,
#     }
#     return render(request, 'filtered_product_list.html', context)


# def filtered_product_list(request):
#     categories = ['women', 'men', 'shoes', 'watches']  # Sample categories
#     selected_category = request.GET.get('category')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#
#     products = Product.objects.filter(status='active')  # Filter for 'active' status
#
#     if selected_category in categories:
#         products = products.filter(category=selected_category)
#
#     if min_price:
#         products = products.filter(price__gte=min_price)
#
#     if max_price:
#         products = products.filter(price__lte=max_price)
#
#     context = {
#         'products': products,
#         'categories': categories,
#         'selected_category': selected_category,
#         'min_price': min_price,
#         'max_price': max_price,
#     }
#     return render(request, 'filtered_product_list.html', context)


#
# def filtered_product_list(request):
#     products = Product.objects.all()
#
#     # Handling filters
#     category = request.GET.get('category')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#
#     if category:
#         products = products.filter(category=category)
#
#     if min_price and max_price:
#         products = products.filter(price__range=(min_price, max_price))
#
#     return render(request, 'filtered_product_list.html', {'products': products})


def filtered_product_list(request):
    categories = ['women', 'men', 'shoes', 'watches']  # Sample categories

    # Get filter values from the request's GET parameters
    selected_category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Query all products (initial queryset)
    products = Product.objects.filter(status='active')

    # Apply category filter if selected
    if selected_category in categories:
        products = products.filter(category=selected_category)

    # Apply price range filters if provided
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'filtered_product_list.html', context)


@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def update_product_status(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        active_status = request.POST.get('active_status')
        if active_status == 'active':
            product.is_active = True
        else:
            product.is_active = False
        product.save()
        return redirect('product_detail', product_id=product.id)
    return render(request, 'update_product.html', {'product': product})


def filtered_product_list(request):
    filtered_products = Product.objects.filter(is_active=True)
    return render(request, 'filtered_product_list.html', {'products': filtered_products})


def filtered_product_list_2(request):
    # Example: Fetching the first 8 products based on a filter condition (change this logic as per your requirements)
    filtered_products_2 = Product.objects.filter(is_active=True)[:8]

    context = {
        'filtered_products_2': filtered_products_2
    }
    return render(request, 'index.html', context)
    # return render(request, 'filtered_product_list.html', {'products': filtered_products_2})


def index(request):
    # Assuming Product is your model with 'name' and 'image' fields
    products = Product.objects.all()  # Retrieve all products from the database
    rows_of_products = [products[i:i + 4] for i in range(0, 8, 4)]  # Slice products for the first 2 rows
    return render(request, 'index.html', {'rows_of_products': rows_of_products})


# contact form submission
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the form data to the database
            return redirect('success_page')  # Redirect to a success page
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def success_page(request):
    return render(request, 'success_page.html')


def mpesa_success(request):
    return render(request, 'mpesa_success.html')


def services(request):
    return render(request, 'services.html')


def shop(request):
    return render(request, 'shop.html')


def contact(request):
    return render(request, 'contact.html')


def inner(request):
    return render(request, 'inner.html')


def ky(request):
    return render(request, 'ky.html')


def ion(request):
    return render(request, 'ion.html')


def neew(request):
    return render(request, 'neew.html')


def registration(request):
    if request.method == 'POST':
        member = Member(firstname=request.POST['firstname'], lastname=request.POST['lastname'],
                        email=request.POST['email'],
                        username=request.POST['username'], password=request.POST['password'])
        member.save()
        return redirect('/')
    else:
        return render(request, 'registration.html')


# def login(request):
#     return render(request, 'login.html')


# def index(request):
# if request.method == 'POST':
#     if Member.objects.filter(username=request.POST['username'],
#                              password=request.POST['password']).exists():
#         member = Member.objects.get(username=request.POST['username'],
#                                     password=request.POST['password'])
#         return render(request, 'index.html', {'member': member})
#     else:
#         return render(request, 'login.html')
# else:
#     return render(request, 'index.html')


#
# def generate_receipt(request, transaction_id):
#     # Fetch transaction details from your database using the transaction_id
#     # Replace these placeholders with actual data retrieved from your database
#     transaction_details = {
#         'transaction_id': transaction_id,
#         'amount': 50.00,
#         'date': '2023-12-01',
#         # Other relevant details
#     }
#
#     # Render receipt HTML using a template and transaction details
#     receipt_html = render_to_string('receipt_template.html', {'transaction': transaction_details})
#
#     # Generate PDF from HTML content
#     pdf_file = HTML(string=receipt_html).write_pdf()
#
#     # Prepare HTTP response to force download the generated PDF
#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="receipt_{transaction_id}.pdf"'
#     return response
#


def logout_view(request):
    logout(request)
    # Redirect to a specific page after logout (optional)
    return redirect('index')  # Redirect to the index page after logout


# def login(request):
#     # Your login logic here, such as checking credentials
#     # For demonstration purposes, assuming a successful login with user type determination
#
#     # Simulate login success and determine user type (replace this with actual login logic)
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         # Your authentication logic here (example: check credentials against database)
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             # If authentication successful, determine user type and set in session
#             # user_type = determine_user_type(user) # Replace with your logic to determine user type
#             if user.is_superuser:
#                 return 'admin'
#             elif user.is_staff:
#                 return 'staff'
#             else:
#                 return 'normal_user'
#
#
#             request.session['user_type'] = user_type
#             return redirect('dashboard')
#         else:
#             # If authentication failed, show an error message or handle accordingly
#             return render(request, 'login.html', {'error_message': 'Invalid credentials'})

        # if authenticated:
        #     user_type = get_user_type(username)  # Replace with your logic
        #     request.session['user_type'] = user_type
        #     return redirect('dashboard')

        # For demo purposes, assuming the login is successful
    #     if username == 'admin':
    #         request.session['user_type'] = 'admin'
    #     elif username == 'staff':
    #         request.session['user_type'] = 'staff'
    #     else:
    #         request.session['user_type'] = 'normal_user'
    #     return redirect('dashboard')
    #
    # return render(request, 'login.html')


def dashboard(request):
    user_type = request.session.get('user_type')

    if user_type == 'admin':
        context = {'content': 'Admin dashboard content'}
    elif user_type == 'staff':
        context = {'content': 'Staff dashboard content'}
    else:
        context = {'content': 'Normal user dashboard content'}

    return render(request, 'dashboard.html', context)


def determine_user_type(user):
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.user_type
    except UserProfile.DoesNotExist:
        return 'normal_user'  # If profile doesn't exist, consider as a normal user

# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             user_type = determine_user_type(user)
#             request.session['user_type'] = user_type
#             return redirect('dashboard')
#         else:
#             return render(request, 'login.html', {'error_message': 'Invalid credentials'})
#
#     return render(request, 'login.html')



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Logs in the user

            # Retrieve user profile to determine user type
            try:
                user_profile = UserProfile.objects.get(user=user)
                user_type = user_profile.user_type
            except UserProfile.DoesNotExist:
                user_type = 'normal_user'  # Default to normal_user if profile doesn't exist

            # Set the user type in session
            request.session['user_type'] = user_type

            return redirect('/')  # Redirect to dashboard after successful login
        else:
            error_message = 'Invalid credentials'
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')