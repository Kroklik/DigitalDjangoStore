from .models import Product, OrderProduct, Order, Customer

# В данном классе будит метод для получния инфо о товарах и метод добаления и удаления
class CartForAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None):
        self.user = request.user

        # Если в product_id и action что то попало то метод запуститься
        if product_id and action:
            self.add_or_delete(product_id, action)


    # Метод для получения инфо о корзине
    def get_cart_info(self):
        customer, created = Customer.objects.get_or_create(user=self.user)  # Получ или создадим покупателя

        order, created = Order.objects.get_or_create(customer=customer)
        print( 'Пользователь', order)
        order_products = order.orderproduct_set.all()

        cart_total_quantity = order.get_cart_total_quantity
        cart_total_price = order.get_cart_total_price

        return {
            'cart_total_quantity': cart_total_quantity,
            'cart_total_price': cart_total_price,
            'order': order,
            'products': order_products
        }

    # Метод дял добавления товара в корзину или удаления
    def add_or_delete(self, product_id, action):
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=product_id)
        order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)

        if action == 'add' and product.quantity > 0:
            order_product.quantity += 1  # В корзину прибавилось +1
            product.quantity -= 1 # У продукта на складе его кол-вщ убавилось -1
        else:
            order_product.quantity -= 1  # В корзину убавилось -1
            product.quantity += 1  # У продукта на складе его кол-во прибавилось +1

        product.save()
        order_product.save()

        if order_product.quantity <= 0:
            order_product.delete()



    # Метод который будит очищать корзину после заказа
    def clear(self):
        order = self.get_cart_info()['order']
        order_products = order.orderproduct_set.all()
        for product in order_products:
            product.delete()
        order.save()





# Функция которая будит возвращать инфо о корзине при помощи метода класса
def get_cart_data(request):
    cart = CartForAuthenticatedUser(request)
    cart_info = cart.get_cart_info()
    return cart_info


