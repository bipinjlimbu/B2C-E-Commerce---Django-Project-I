from django.shortcuts import render
from ..models import Product, Brand

def home_view(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
    brands = Brand.objects.all().order_by('name')
    return render(request, 'main/home_page.html', {'products': products, 'brands': brands})