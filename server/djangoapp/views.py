from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarMake, CarModel
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request

# Get an instance of a logger

logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context ={}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('psw')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            print(f'{request.user.username} logged in')
            if request.META.get('HTTP_REFERER'):
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    print(f'{request.user.username} logged out')
    logout(request)
    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('psw')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/alexoff_djangoserver-space/capstone/dealerships.json"
        # Get dealers from the URL
        _state = request.GET.get('state')
        if _state:
            dealerships = get_dealers_from_cf(url, state=_state)
        else:
            dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name

        context['dealers'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


def get_reviews(request):
    context = {}
    print(request)
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/alexoff_djangoserver-space/capstone/review.json"
        # Get dealers from the URL
        _dealer_id = request.GET.get('dealerId')
        if _dealer_id:
            reviews = get_dealer_reviews_from_cf(url, dealer_id=_dealer_id)
        else:
            reviews = get_dealer_reviews_from_cf(url)
        # Concat all dealer's short name
        names = ' '.join([review.review for review in reviews])
        # Return a list of dealer short name
        return HttpResponse(names)
# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):


def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/alexoff_djangoserver-space/capstone/review.json"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        print(reviews)
        # Concat all dealer's short name
        names = ' '.join([review.review for review in reviews])
        context['reviews'] = reviews
        context['id'] = dealer_id
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)


def add_review(request, dealer_id):
    if request.method == 'GET':
        context = {}

        dealers = get_dealers_from_cf('https://eu-de.functions.appdomain.cloud/api/v1/web/alexoff_djangoserver-space'
                                      '/capstone/dealerships.json')
        for dealer in dealers:
            if dealer.id == dealer_id:
                context['dealer'] = dealer
                break
        context['dealer_id'] = dealer_id
        context['cars'] = CarModel.objects.filter(dealer_id=dealer_id)
        print(context['cars'][0].car_make)
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == 'POST' and User.is_authenticated:
        print(request.POST)
        if request.POST.get('car'):
            car_obj = CarModel.objects.get(id=request.POST.get('car')[0])
            print(car_obj)
        else:
            car_obj = None
        review = {
            "id": 12,
            "name": f'{User.first_name} {User.last_name}',
            "dealership": dealer_id,
            "review": request.POST.get('content'),
            "purchase": True if request.POST.get('purchasecheck') else False,
            "purchase_date": request.POST.get('purchasedate')[0] if request.POST.get('purchasedate') else '',
            "car_make": car_obj.car_make.name if car_obj else '',
            "car_model": car_obj.name if car_obj else '',
            "car_year": car_obj.year.year if car_obj else ''
        }
        payload = {"review": review}
        resp = post_request('https://eu-de.functions.appdomain.cloud/api/v1/web/alexoff_djangoserver-space/capstone'
                            '/review.json', json_payload=payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)