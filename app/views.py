from django.shortcuts import render,redirect, HttpResponse
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404






# def search(request):
#     query = request.GET.get('q')
#     print(f"Query: {query}")  # Print the query
#     results = Product.objects.filter(title__icontains=query)
#     print(f"Results: {results}")  # Print the results
#     return render(request, 'app/search_results.html', {'results': results})

def search(request):
    query = request.GET.get('q', '')
    search_results = Product.objects.filter(title__icontains=query)
    return render(request, 'app/search_results.html', {'search_results': search_results, 'query': query})

# class SearchView(View):
#     def get(self, request):
#         query = request.GET.get('q')
#         print(f"Query: {query}")  # Print the query
#         results = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
#         print(f"Results: {results}")  # Print the results
#         return render(request, 'app/search_results.html', {'results': results})


class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='PR')
        bottomwears = Product.objects.filter(category='MF')
        mobiles = Product.objects.filter(category='M')
        return render(request, 'app/home.html', {'topwears': topwears, 'bottomwears': bottomwears, 'mobiles':mobiles})


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'app/productdetail.html', {'product': product})

@login_required
def add_to_cart(request):
    user = request.user
    product = request.GET.get('prod_id')
    item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=user)).exists()
    if not item_already_in_cart1:
        product_title = Product.objects.get(id=product)
        Cart(user=user, product=product_title).save()
        messages.success(request, 'Product Added to Cart Successfully !!' )
    return redirect('/cart')

def show_cart(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
		user = request.user
		cart = Cart.objects.filter(user=user)
		amount = 0.0
		shipping_amount = 5.0
		totalamount=0.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		print(cart_product)
		if cart_product:
			for p in cart_product:
				tempamount = (p.quantity * p.product.discounted_price)
				amount += tempamount
			totalamount = amount+shipping_amount
			return render(request, 'app/addtocart.html', {'carts':cart, 'amount':amount, 'totalamount':totalamount, 'totalitem':totalitem})
		else:
			return render(request, 'app/emptycart.html', {'totalitem':totalitem})
	else:
		return render(request, 'app/emptycart.html', {'totalitem':totalitem})

def plus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity+=1
		c.save()
		amount = 0.0
		shipping_amount= 5.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			amount += tempamount
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

def minus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity-=1
		c.save()
		amount = 0.0
		shipping_amount= 5.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

def remove_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.delete()
		amount = 0.0
		shipping_amount= 5.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'amount':amount,
			'totalamount':amount+shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")


@login_required
def buy_now(request, product_id=None):
    if product_id:
        user = request.user
        item_already_in_cart = Cart.objects.filter(Q(product=product_id) & Q(user=user)).exists()
        if not item_already_in_cart:
            product = get_object_or_404(Product, id=product_id)
            Cart(user=user, product=product).save()
            messages.success(request, 'Product Added to Cart Successfully !!')
        return redirect('checkout')


def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-dark'})

def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed':op})

def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Apple' or data == 'Samsung':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    return render(request, 'app/mobile.html', {'mobiles': mobiles})

def topwear(request, data=None):
    if data == None:
        topwears = Product.objects.filter(category='PR')
    elif data == 'HRX' or data == 'Polo' or data == "Park":
        topwears = Product.objects.filter(category='PR').filter(brand=data)
    return render(request, 'app/topwear.html', {'topwears': topwears})

def bottomwear(request, data=None):
    if data == None:
        bottomwears = Product.objects.filter(category='MF')
    elif data == 'Beyoung' or data == "Lee":
        bottomwears = Product.objects.filter(category='MF').filter(brand=data)
    return render(request, 'app/bottomwear.html', {'bottomwears': bottomwears})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulations! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})


def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=request.user)
    amount = 0.0
    shipping_amount = 5.0
    totalamount=0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount = amount+shipping_amount

    # Get the product details from the session
    product_id = request.session.get('product_id')
    if product_id:
        product = Product.objects.get(id=product_id)
        return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items, 'totalcost':totalamount, 'product': product})

    return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items, 'totalcost':totalamount})

from django.core.exceptions import ObjectDoesNotExist

def payment_done(request):
    custid = request.GET.get('custid')
    print("Customer ID", custid)
    user = request.user
    cartid = Cart.objects.filter(user = user)
    try:
        customer = Customer.objects.get(id=custid)
    except ObjectDoesNotExist:
        messages.error(request, 'Customer does not exist')
        return redirect('home')  # replace 'home' with the name of your home page or error page
    print(customer)
    for cid in cartid:
        OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
        print("Order Saved")
        cid.delete()
        print("Cart Item Deleted")
    messages.success(request, 'Payment is done successfully')
    return redirect("orders")


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-dark'})
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Profile Updated Successfully')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})