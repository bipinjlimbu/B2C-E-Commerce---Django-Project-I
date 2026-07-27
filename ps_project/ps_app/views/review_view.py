from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Review, Product

@login_required
def add_review_view(request, product_id):
    if request.user.is_staff:
        messages.error(request, 'Staff members cannot add reviews.')
        return redirect('/dashboard/admin/?section=product-reviews')
    
    product = Product.objects.filter(id=product_id).first()
    
    errors = {}
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating:
            errors['rating'] = 'Rating is required.'
        if not comment:
            errors['comment'] = 'Comment is required.'
            
        if errors:
            return render(request, 'main/add_review_page.html', {'product': product, 'errors': errors, 'data': request.POST})
        
        review = Review(customer=request.user, product=product, rating=rating, comment=comment)
        review.save()
        messages.success(request, 'Review added successfully.')
        return redirect(f'/products/{product_id}/')
    
    return render(request, 'main/add_review_page.html', {'product': product})

@login_required
def edit_review_view(request, review_id):
    review = Review.objects.filter(id=review_id, customer=request.user).first()
    
    if not review:
        messages.error(request, 'Review not found or you do not have permission to edit it.')
        return redirect('/dashboard/?section=my-reviews')
    
    if not request.user == review.customer:
        messages.error(request, 'You do not have permission to edit this review.')
        return redirect('/dashboard/?section=my-reviews')
    
    if not review.product:
        messages.error(request, 'The product associated with this review does not exist.')
        return redirect('/dashboard/?section=my-reviews')
    
    if request.user.is_staff:
        messages.error(request, 'Staff members cannot edit reviews.')
        return redirect('/dashboard/admin/?section=product-reviews')
    
    errors = {}
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating:
            errors['rating'] = 'Rating is required.'
        if not comment:
            errors['comment'] = 'Comment is required.'
            
        if errors:
            return render(request, 'main/edit_review_page.html', {'review': review, 'errors': errors, 'data': request.POST})
        
        review.rating = rating
        review.comment = comment
        review.save()
        messages.success(request, 'Review updated successfully.')
        return redirect('/dashboard/?section=my-reviews')
    
    return render(request, 'main/edit_review_page.html', {'review': review})

@login_required
def delete_review_view(request, review_id):
    review = Review.objects.filter(id=review_id).first()
    
    if not review:
        messages.error(request, 'Review not found.')
        return redirect('/dashboard/?section=my-reviews')
    
    if not request.user == review.customer and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this review.')
        return redirect('/dashboard/?section=my-reviews')
    
    if not review.product:
        messages.error(request, 'The product associated with this review does not exist.')
        return redirect('/dashboard/?section=my-reviews')
    
    if review:
        review.delete()
        messages.success(request, 'Review deleted successfully.')
    else:
        messages.error(request, 'Review not found or you do not have permission to delete it.')
    
    if request.user.is_staff:
        return redirect('/dashboard/admin/?section=product-reviews')
    else:
        return redirect('/dashboard/?section=my-reviews')