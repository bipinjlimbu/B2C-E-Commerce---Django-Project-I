from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from ..models import Brand, Product, Wishlist

def products_view(request):
    context = {}
    
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', 'all')
    brand_id = request.GET.get('brand', 'all')
    condition = request.GET.get('condition', 'all')
    price_range = request.GET.get('price_range', 'all')
    sort_by = request.GET.get('sort', 'latest')
    
    products = Product.objects.all().order_by('-created_at')
    
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(brand__name__icontains=search_query) | Q(category__icontains=search_query), is_active=True).order_by('-created_at')
        
    if category and category != 'all':
        products = products.filter(category=category, is_active=True).order_by('-created_at')
        
    if brand_id and brand_id != 'all':
        brand_instance = Brand.objects.get(id=brand_id)
        products = products.filter(brand=brand_instance, is_active=True).order_by('-created_at')
        
    if condition and condition != 'all':
        products = products.filter(condition=condition, is_active=True).order_by('-created_at')
        
    if price_range and price_range != 'all':
        if price_range == '0-999':
            products = products.filter(price__gte=0, price__lte=999, is_active=True).order_by('-created_at')
        elif price_range == '1000-4999':
            products = products.filter(price__gte=1000, price__lte=4999, is_active=True).order_by('-created_at')
        elif price_range == '5000-9999':
            products = products.filter(price__gte=5000, price__lte=9999, is_active=True).order_by('-created_at')
        elif price_range == '10000-49999':
            products = products.filter(price__gte=10000, price__lte=49999, is_active=True).order_by('-created_at')
        elif price_range == '50000+':
            products = products.filter(price__gte=50000, is_active=True).order_by('-created_at')
        
    if sort_by == 'price_asc':
        products = products.filter(is_active=True).order_by('price')
    elif sort_by == 'price_desc':
        products = products.filter(is_active=True).order_by('-price')
    elif sort_by == 'stock_asc':
        products = products.filter(is_active=True).order_by('stock')
    elif sort_by == 'stock_desc':
        products = products.filter(is_active=True).order_by('-stock')
        
    context['products'] = products
    context['brands'] = Brand.objects.all()
    return render(request, 'main/products_page.html', context)

@login_required
def add_product_view(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add a product.")
        return redirect('/dashboard/admin/?section=product-management')
    
    brands = Brand.objects.all()
    
    errors = {}
    if request.method == "POST":
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category = request.POST.get('category')
        condition = request.POST.get('condition')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        is_active = request.POST.get('is_active') == 'true'
        brand_id = request.POST.get('brand')
        product_image = request.FILES.get('product_image')

        if not name:
            errors['name'] = "Product name is required."
            
        if not sku:
            errors['sku'] = "SKU is required."
        elif Product.objects.filter(sku=sku).exists():
            errors['sku'] = "SKU must be unique. This SKU already exists."
            
        if not category:
            errors['category'] = "Category is required."
            
        if not condition:
            errors['condition'] = "Condition is required."
            
        if not description:
            errors['description'] = "Description is required."
            
        if not price:
            errors['price'] = "Price is required."
            
        if not stock:
            errors['stock'] = "Stock quantity is required."
            
        if not brand_id:
            errors['brand'] = "Brand selection is required."
            
        if not product_image:
            errors['product_image'] = "Product image is required."

        if errors:
            return render(request, 'main/add_products_page.html', {'brands': brands,'data': request.POST, 'errors': errors})
        
        brand = Brand.objects.get(id=brand_id)
        product = Product(
            name=name,
            sku=sku,
            category=category,
            condition=condition,
            description=description,
            price=price,
            stock=stock,
            brand=brand,
            product_image=product_image,
            is_active=is_active
        )
        product.save()
        messages.success(request, f"Product '{name}' has been added successfully.")
        return redirect('/dashboard/admin/?section=product-management')
        
    return render(request, 'main/add_products_page.html',{'brands':brands})

@login_required
def edit_product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit a product.")
        return redirect('/dashboard/admin/?section=product-management')
    
    if not product:
        messages.error(request, "Product not found.")
        return redirect('/dashboard/admin/?section=product-management')
    
    brands = Brand.objects.all()
    
    errors = {}
    if request.method == "POST":
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category = request.POST.get('category')
        condition = request.POST.get('condition')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        brand_id = request.POST.get('brand')
        product_image = request.FILES.get('product_image')

        if not name:
            errors['name'] = "Product name is required."
            
        if not sku:
            errors['sku'] = "SKU is required."
        elif Product.objects.filter(sku=sku).exclude(id=product_id).exists():
            errors['sku'] = "SKU must be unique. This SKU already exists."
            
        if not category:
            errors['category'] = "Category is required."
            
        if not condition:
            errors['condition'] = "Condition is required."
            
        if not description:
            errors['description'] = "Description is required."
            
        if not price:
            errors['price'] = "Price is required."
            
        if not stock:
            errors['stock'] = "Stock quantity is required."
            
        if not brand_id:
            errors['brand'] = "Brand selection is required."

        if errors:
            return render(request, 'main/edit_products_page.html', {'product': product, 'brands': brands, 'data': request.POST, 'errors': errors})
        
        brand = Brand.objects.get(id=brand_id)
        
        product.name = name
        product.sku = sku
        product.category = category
        product.condition = condition
        product.description = description
        product.price = price
        product.stock = stock
        product.brand = brand
        
        if product_image:
            product.product_image.delete(save=False)
            product.product_image = product_image
        
        product.save()
        
        messages.success(request, f"Product '{name}' has been updated successfully.")
        return redirect('/dashboard/admin/?section=product-management')
    
    return render(request, 'main/edit_products_page.html', {'product': product, 'brands': brands})

@login_required
def is_active_toggle_view(request, product_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to change product status.")
        return redirect('/dashboard/admin/?section=product-management')
    
    try:
        product = Product.objects.get(id=product_id)
        product.is_active = not product.is_active
        product.save()
        status = "activated" if product.is_active else "deactivated"
        messages.success(request, f"Product '{product.name}' has been {status}.")
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
    return redirect('/dashboard/admin/?section=product-management')

@login_required
def delete_product_view(request, product_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete a product.")
        return redirect('/dashboard/admin/?section=product-management')
    
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, f"Product '{product.name}' has been deleted successfully.")
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
    return redirect('/dashboard/admin/?section=product-management')

def single_product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    
    if not product.is_active:
        messages.error(request, "This product is currently inactive.")
        return redirect('home')
    
    if Wishlist.objects.filter(customer=request.user, product=product).exists():
        product.in_wishlist = True
    else:
        product.in_wishlist = False
        
    return render(request, 'main/single_product_page.html', {'product': product, 'reviews': reviews})