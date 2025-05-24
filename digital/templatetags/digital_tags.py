from digital.models import Category, Product, FavoriteProduct
from django import template

register = template.Library()


# Функция для получения категорий на любой странице
@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)


# Функция для получения цветов меодели
@register.simple_tag()
def get_colors(model):
    products = Product.objects.filter(model_product=model)
    list_colors = [i.color_cod for i in products]
    print('Список цветов', list_colors)
    return list_colors


@register.simple_tag()
def get_favorite_products(user):
    favorite_products = FavoriteProduct.objects.filter(user=user)
    products = [i.product for i in favorite_products]
    return products

@register.simple_tag()
def get_normal_price(price):
    return f'{int(price):_}'.replace('_', ' ')







