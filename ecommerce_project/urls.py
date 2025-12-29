from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin_site import custom_admin_site
from django.views.generic import TemplateView
from django.http import HttpResponse
def fake_source(request):
    return HttpResponse("<h2>Tophutbd is protected.</h2>")

urlpatterns = [
    path('', include('products.urls')),
    path("fake-source/", fake_source),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('users/', include('users.urls')),
    path('admin/', custom_admin_site.urls, name='custom_admin'),

    # Policy pages
    path('privacy-policy/', TemplateView.as_view(template_name='policies/privacy_policy.html'), 
         name='privacy_policy'),
    path('refund-policy/', TemplateView.as_view(template_name='policies/refund_policy.html'), 
         name='refund_policy'),
    path('terms-conditions/', TemplateView.as_view(template_name='policies/terms_conditions.html'), 
         name='terms_conditions'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Override the default admin site
admin.site = custom_admin_site
admin.autodiscover()