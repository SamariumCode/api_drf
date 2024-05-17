from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from . import models


class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_15 = '3<=15'
    MORE_THAN_16 = '>17'

    title = 'Critical Inventory Status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'Low'),
            (InventoryFilter.BETWEEN_3_15, 'Medium'),
            (InventoryFilter.MORE_THAN_16, 'High'),
        ]

    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)

        if self.value() == InventoryFilter.BETWEEN_3_15:
            return queryset.filter(inventory__range=(3, 15))

        if self.value() == InventoryFilter.MORE_THAN_16:
            return queryset.filter(inventory__gte=17)


class ProductAdminInline(admin.TabularInline):
    model = models.Comment
    fields = ['name', 'body']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory',
                    'unit_price', 'total', 'inventory_status', 'product_category', 'num_of_comments']
    list_per_page = 2
    list_editable = ['unit_price', ]
    ordering = ['-id', ]
    list_select_related = ['category', ]
    list_filter = ['datetime_created', 'category', InventoryFilter]
    actions = ['clear_inventory', ]
    prepopulated_fields = {
        'slug': ['name', ]
    }
    search_fields = ['name', ]
    autocomplete_fields = ['category']
    inlines = [ProductAdminInline]

    # fields = ['name', 'slug']
    # exclude = ['discounts',]
    # readonly_fields = ['category',]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('comments').annotate(num_of_comments=Count('comments'))

    @admin.display(ordering='num_of_comments', description='# Comments')
    def num_of_comments(self, product: models.Product):
        # return product.num_of_comments

        # http://127.0.0.1:8000/admin/store/comment/?product__id=2
        url = (
                reverse('admin:store_comment_changelist')
                + '?'
                + urlencode(
            {
                'product__id': product.id
            }
        )
        )

        return format_html('<a href="{}">{}</a>', url, product.num_of_comments)

    def total(self, product):
        return product.inventory * product.unit_price

    def inventory_status(self, product: models.Product):
        if product.inventory < 10:
            return 'Low'
        if product.inventory > 20:
            return 'High'

        return 'Medium'

    # ordering category_name
    @admin.display(ordering='category__title')
    def product_category(self, product: models.Product):
        return product.category.title

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} of product inventories cleared to zero.',
            messages.WARNING,
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    list_per_page = 5
    ordering = ['first_name', 'last_name', ]
    search_fields = ['first_name__istartswith', 'last_name__istartswith', ]
    actions = ['uppercase', 'lowercase']

    @admin.action(description='Make Selected Upper first name')
    def uppercase(self, request, queryset):
        for obj in queryset:
            obj.first_name = obj.first_name.upper()
            obj.save()

    @admin.action(description='Make Selected Lower first name')
    def lowercase(self, request, queryset):
        for obj in queryset:
            obj.first_name = obj.first_name.lower()
            obj.save()


class OrderItemInline(admin.TabularInline):  # StackedInline
    model = models.OrderItem
    fields = ['product', 'quantity', 'unit_price']
    extra = 1
    min_num = 1
    # max_num = 10


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status',
                    'datetime_created', 'num_of_items']
    ordering = ['datetime_created', ]
    list_editable = ['status', ]
    list_per_page = 4
    list_select_related = ['customer', ]
    search_fields = ['customer__last_name', ]
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items').annotate(items_count=Count('items'))

    @admin.display(ordering='items_count', description='# items')
    def num_of_items(self, order: models.Order):
        return order.items_count


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    autocomplete_fields = ['product', ]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status', 'product_name', 'body', 'name']
    list_editable = ['status']
    list_per_page = 3
    list_select_related = ['product', ]
    list_display_links = ['product', ]
    actions = ['make_wa']
    autocomplete_fields = ['product', ]

    def product_name(self, comment: models.Comment):
        return comment.product.slug

    @admin.action(description='Mark Selected Status Waiting')
    def make_wa(self, request, queryset):
        queryset.update(status='w')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', ]


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass
