from random import randint

from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from .forms import LoginForm, RegisterForm, CustomerForm, ShippingForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, get_cart_data
import stripe
from shop import settings


# Create your views here.

class ProductList(ListView):
    model = Product
    context_object_name = 'categories'

    extra_context = {
        'title': 'DigitalStore'
    }

    template_name = 'digital/index.html'

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'digital/category_page.html'
    paginate_by = 1

    def get_queryset(self):
        brand_field = self.request.GET.get('brand')
        color_field = self.request.GET.get('color')
        price_field = self.request.GET.get('price')
        discount_field = self.request.GET.get('discount')

        category = Category.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category=category)

        if brand_field:
            products = products.filter(brand__title=brand_field)

        if color_field:
            products = products.filter(color_name=color_field)

        if price_field:
            products = products.filter(price=price_field)

        if discount_field:
            products = products.filter(discount=discount_field)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category=category)
        brands = list(set([i.brand for i in products]))
        colors = list(set([i.color_name for i in products]))
        prices = list(set([int(i.price) for i in products]))
        discounts = list(set([i.discount for i in products]))

        context['brands'] = brands
        context['colors'] = colors
        context['prices'] = prices
        context['discounts'] = discounts
        context['category'] = category
        context['title'] = f'Категория: {category.title}'

        return context


# Функция для входа в Аккаунт
def user_login(request):
    if request.user.is_authenticated:
        page = request.META.get('HTTP_REFERER', 'index')
        return redirect(page)
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    messages.success(request, 'Вы вошли в аккаунт')
                    return redirect('index')
                else:
                    messages.error(request, 'Не верный логин или пароль')
                    return redirect('login')
            else:
                messages.error(request, 'Не верный логин или пароль')
                return redirect('login')
        else:
            form = LoginForm()

        context = {
            'form': form,
            'title': 'Вход в Аккаунт'
        }

        return render(request, 'digital/login.html', context)


# Функция для выхода из Аккаунта
def user_logout(request):
    logout(request)
    messages.warning(request, 'Уже уходите 😢')
    return redirect('index')


# Функция регистрации
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'Регистрация прошла успешно. Авторизуйтесь')
                return redirect('login')
            else:
                for field in form.errors:
                    messages.error(request, form.errors[field].as_text())
                return redirect('register')

        else:
            form = RegisterForm()

        context = {
            'title': 'Регистрация пользователя',
            'form': form
        }

        return render(request, 'digital/register.html', context)


# Вьюшка для детали товара
class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Товар {product.title}'

        products = Product.objects.filter(category=product.category)  # Получ список продуктов категории
        data = []
        for i in range(len(products)):
            random_index = randint(0, len(products) - 1)
            p = products[random_index]
            if p not in data and product != p:
                data.append(p)
            context['products'] = data

        return context


def product_by_color(request, model_product, color):
    product = Product.objects.get(model_product=model_product, color_cod=color)

    products = Product.objects.filter(category=product.category)  # Получ список продуктов категории
    data = []
    for i in range(len(products)):
        random_index = randint(0, len(products) - 1)
        p = products[random_index]
        if p not in data and product != p:
            data.append(p)

    context = {
        'title': f'Товар {product.title}',
        'product': product,
        'products': data
    }

    return render(request, 'digital/product_detail.html', context)



# Вьюшка для довления товара в Избранное
def save_favorite_product(request, slug):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProduct.objects.filter(user=user)
        if user:
            if product not in [i.product for i in favorite_products]:
                messages.success(request, f'Товар {product.title} в избранном')
                FavoriteProduct.objects.create(user=user, product=product)
            else:
                fav_product = FavoriteProduct.objects.get(user=user, product=product)
                messages.warning(request, f'Товар {product.title} удалён из избранного')
                fav_product.delete()

        page = request.META.get('HTTP_REFERER', 'index')
        return redirect(page)

    else:
        messages.warning(request, 'Авторизуйтесь, для добавления товара в Избранное')
        return redirect('login')




class FavoriteProductsView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'digital/favorite.html'
    login_url = 'login'

    # Данным метод отправляет продукты конкретного пользователя на страницу
    def get_queryset(self):
        user = self.request.user
        favorite_products = FavoriteProduct.objects.filter(user=user)
        products = [i.product for i in favorite_products]
        return products


# Вьюшка для добавления товара в Корзину
def to_cart_view(request, pk, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, pk, action)
        page = request.META.get('HTTP_REFERER', 'index')
        messages.success(request, 'Товар добавлен в корзину')
        return redirect(page)
    else:
        messages.warning(request, 'Авторизуйтесь')
        return redirect(login)


# Вьюшка для страницы корзины
def my_cart_view(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Моя корзина',
            'order': cart_info['order'],
            'products': cart_info['products']
        }

        return render(request, 'digital/my_cart.html', context)

    else:
        return redirect('login')



def checkout(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Оформить заказ',
            'order': cart_info['order'],
            'items': cart_info['products'],

            'customer_form': CustomerForm(),
            'shipping_form': ShippingForm()
        }

        return render(request, 'digital/checkout.html', context)

    else:
        return redirect('login')



def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        customer_form = CustomerForm(data=request.POST)
        if customer_form.is_valid():
            customer = Customer.objects.get(user=request.user)
            customer.first_name = customer_form.cleaned_data['first_name']
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.email = customer_form.cleaned_data['email']
            customer.save()

        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()

        else:
            for field in shipping_form.errors:
                messages.warning(request, shipping_form.errors[field].as_text())


        total_price = cart_info['cart_total_price']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data':{
                    'currency': 'usd',
                    'product_data': {
                        'name': 'DigitalStore товары'
                    },
                    'unit_amount': int(total_price)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)


def success_payment(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        # Реализовать логику сохранения заказа после оплаты

        user_cart.clear()
        messages.success(request, 'Оплата прошла успешно. Мы вас кинули спаибо покупайте ещё.')
        return render(request, 'digital/success.html')

    else:
        return redirect('index')



def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()

    return redirect('my_cart')









