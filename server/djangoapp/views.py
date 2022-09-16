from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
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
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


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
        # Return a list of dealer short name
        return HttpResponse(names)
    if request.method == 'POST':
        return add_review(request, dealer_id)
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...


def add_review(request, dealer_id):
    if request.method == 'POST' and User.is_authenticated:
        review = {
            "id": 232,
            "name": "Gora Zettoi",
            "dealership": dealer_id,
            "review": "proofed foreground capability",
            "purchase": True,
            "purchase_date": "09/17/2012",
            "car_make": "Pontiac",
            "car_model": "Firebird",
            "car_year": 1994
        }
        payload = {"review": review}
        resp = post_request('https://eu-de.functions.appdomain.cloud/api/v1/web/alexoff_djangoserver-space/capstone'
                            '/review.json', json_payload=payload)
        return HttpResponse(resp)