from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from .models import Category, Product, ProductImage, ProductVariant
from ecommerce_project.admin_site import custom_admin_site


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['preview']
    classes = ['collapse']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    preview.short_description = 'Preview'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    classes = ['collapse']


@admin.register(Category, site=custom_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'is_active', 'created_at', 'admin_actions']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_count(self, obj):
        count = obj.products.count()
        url = reverse('custom_admin:products_product_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    product_count.short_description = 'Products'

    def admin_actions(self, obj):
        edit_url = reverse('custom_admin:products_category_change', args=[obj.id])
        return format_html('<a href="{}" class="button">Edit</a>', edit_url)
    admin_actions.short_description = 'Actions'


@admin.register(Product, site=custom_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'preview_image', 'name', 'category', 'price', 'stock_status',
        'is_active', 'is_featured', 'created_at', 'admin_actions'
    ]
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'preview_image_large']
    inlines = [ProductImageInline, ProductVariantInline]
    list_per_page = 20

    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'has_variants')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Preview', {
            'fields': ('preview_image_large',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def preview_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 4px;" />',
                first_image.image.url
            )
        return "📷"
    preview_image.short_description = 'Image'

    def preview_image_large(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover; border-radius: 8px;" />',
                first_image.image.url
            )
        return "No image"
    preview_image_large.short_description = 'Product Image'

    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span class="badge badge-danger">Out of Stock</span>')
        elif obj.stock_quantity <= obj.low_stock_threshold:
            return format_html('<span class="badge badge-warning">Low Stock</span>')
        return format_html('<span class="badge badge-success">In Stock</span>')
    stock_status.short_description = 'Stock'

    def admin_actions(self, obj):
        edit_url = reverse('custom_admin:products_product_change', args=[obj.id])
        view_url = reverse('products:product_detail', args=[obj.slug])
        return format_html(
            '<a href="{}" class="button">Edit</a> '
            '<a href="{}" target="_blank" class="button">View</a>',
            edit_url, view_url
        )
    admin_actions.short_description = 'Actions'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
