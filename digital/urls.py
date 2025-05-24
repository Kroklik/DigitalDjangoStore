from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductList.as_view(), name='index'),
    path('category_page/<slug:slug>/', CategoryView.as_view(), name='category_page'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register_view, name='register'),
    path('product_detail/<slug:slug>/', ProductDetail.as_view(), name='product_detail'),
    path('product_color/<str:model_product>/<str:color>/', product_by_color, name='product_color'),
    path('add_favorite/<slug:slug>/', save_favorite_product, name='add_favorite'),
    path('my_favorite/', FavoriteProductsView.as_view(), name='my_favorite'),
    path('to_cart/<int:pk>/<str:action>/', to_cart_view, name='to_cart'),
    path('my_cart/', my_cart_view, name='my_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/', create_checkout_session, name='payment'),
    path('success_payment/', success_payment, name='success'),
    path('clear_cart/', clear_cart, name='clear_cart')
]