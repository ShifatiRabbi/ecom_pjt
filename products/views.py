from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category

def home(request):
    # Get categories for navigation
    categories = Category.objects.filter(is_active=True)
    
    # Get products by category (you'll need to adjust these based on your category structure)
    home_gadgets_products = Product.objects.filter(
        category__name__icontains='home', 
        is_active=True
    )[:8] or Product.objects.filter(is_active=True)[:8]
    
    health_beauty_products = Product.objects.filter(
        category__name__icontains='health', 
        is_active=True
    )[:8] or Product.objects.filter(is_active=True)[:8]
    
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True
    )[:12] or Product.objects.filter(is_active=True)[:12]
    
    latest_products = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:12]
    
    context = {
        'categories': categories,
        'home_gadgets_products': home_gadgets_products,
        'health_beauty_products': health_beauty_products,
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'products/home.html', context)

def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_products.html', context)

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def product_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/search_results.html', context)