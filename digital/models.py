from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название категории')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Картинка')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Категория', related_name='subcategories')

    def get_absolute_url(self):
        return reverse('category_page', kwargs={'slug': self.slug})

    # Метод для получения картинки категории
    def get_image_category(self):
        if self.image:
            return self.image.url
        else:
            return '-'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'



# Модель товара
class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название товара')
    price = models.FloatField(verbose_name='Цена')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    credit = models.CharField(max_length=250, null=True, blank=True, verbose_name='Рассрочка')
    discount = models.CharField(max_length=250, null=True, blank=True, verbose_name='Скидка')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',
                                 verbose_name='Категория')
    slug = models.SlugField(unique=True, null=True)
    memory = models.CharField(max_length=250,  verbose_name='Память')
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Бренд')
    color_cod = models.TextField(default='#000000', verbose_name='Код цвета', null=True, blank=True)
    color_name = models.TextField(default='Чёрный', verbose_name='Цвет', null=True, blank=True)
    model_product = models.CharField(max_length=255, null=True, blank=True, verbose_name='Модель товара')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    # Метод для получения картинки категории
    def get_image_product(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return '-'
        else:
            return '-'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


# Меодель Галереи картинок товаров
class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Картинка товара')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Картинка Товара'
        verbose_name_plural = 'Картинки Товаров'


# Модель описания товара
class ProductDescription(models.Model):
    parameter = models.CharField(max_length=150, verbose_name='Название параметра')
    parameter_info = models.CharField(max_length=400, verbose_name='Описание параметра')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='parameters')

    class Meta:
        verbose_name = 'Описание Товара'
        verbose_name_plural = 'Описание Товаров'




class Brand(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название Бренда')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='brand', verbose_name='Категория')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'



# Моделька Избранное
class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользоваель')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')

    def __str__(self):
        return f'Продукт {self.product.title}, {self.user.username}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'




#--------------------------------------------------------------------------------------------


# Модель покупателя

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=255, default='', verbose_name='Имя')
    last_name = models.CharField(max_length=255, default='', verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Почта покупателя', blank=True, null=True)

    def __str__(self):
        return f'Покупатель {self.first_name}'


    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


#-------------------------------------------------------------------
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнен ли заказа')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')

    def __str__(self):
        return f'Заказ №: {self.pk}'


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # ------------------------------  Здесь будут метода подсчёта заказа
    @property # Метод для полкчения суммы Заказа
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property  # Метод для полкчения кол-ва заказанных товаров
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity





# Модель заказынных товаров
class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Кол-во')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')


    def __str__(self):
        return f'{self.product.title} {self.order}'

    class Meta:
        verbose_name = 'Заказанны товар'
        verbose_name_plural = 'Заказанные товары'


    # Метод который вернёт сумму товара в его кол-ве
    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price



class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order,  on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    address = models.CharField(max_length=255, verbose_name='Адрес ул.дом.кв')
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name='Город')
    region = models.CharField(max_length=100, verbose_name='Регион/Область')
    phone = models.CharField(max_length=100, verbose_name='Номер телефона')
    comment = models.CharField(max_length=255, null=True, blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата доставки')

    def __str__(self):
        return f'{self.address} покупателя {self.customer.first_name}'

    class Meta:
        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставки'



class City(models.Model):
    city_name = models.CharField(max_length=100, verbose_name='Название города')

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
















