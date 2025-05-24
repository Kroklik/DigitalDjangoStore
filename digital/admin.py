from django.contrib import admin
from .models import *
from .forms import CategoryForm
from django.utils.safestring import mark_safe

# Register your models here.

class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1

class ParameterInline(admin.TabularInline):
    fk_name = 'product'
    model = ProductDescription
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'get_image')
    form = CategoryForm
    prepopulated_fields = {'slug': ['title']}

    # МЕТОД ДЛЯ ПОЛУЧЕНИЯ КАРТИНКИ КАТЕГОРИИ
    def get_image(self, obj):
        if obj.image:
            try:
                return mark_safe(f'<img src="{obj.image.url}" width="75" >')
            except:
                return '-'
        else:
            return '-'

    get_image.short_description = 'Картинка'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category')
    list_display_links = ('pk', 'title')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'quantity', 'price', 'created_at', 'brand', 'get_image')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ['title']}
    inlines = [GalleryInline, ParameterInline]
    list_editable = ['quantity', 'price']


    def get_image(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75" >')
            except:
                return '-'
        else:
            return '-'


# admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(ProductDescription)
admin.site.register(Gallery)
admin.site.register(FavoriteProduct)
# admin.site.register(Brand)


admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ShippingAddress)
admin.site.register(City)