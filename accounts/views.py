from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random
import operator

import calendar
import datetime 
import numpy as np


from .forms import *
from .models import *

from friend.models import FriendList, FriendRequest
from friend.utils import get_friend_request_or_false
from friend.friend_request_status import FriendRequestStatus

from django.db.models import Sum


# Create your views here.

def error_404_view(request, exception):
    context = {'error': 404}
    return render(request, 'accounts/error.html', context)

def error_500_view(request):
    context = {'error': 500}
    return render(request, 'accounts/error.html', context)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('accounts:home')
    else:
        form = CreateUserForm()
        
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')

                Customer.objects.create(
                    user=user,
                    username=user.username,
                    email=user.email
                )

                messages.success(request, 'Account for ' + username + ' was successfully created.')
                return redirect('accounts:login')
                


        context = {'form': form}
        return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('accounts:home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                if request.user.customer.first_name:
                    return redirect('accounts:home')
                else:
                    return redirect('accounts:update_customer')
            else:
                messages.info(request, 'Invalid Username or Password')
                
        context = {}
        return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('accounts:login')

@login_required(login_url='login')
def home(request):
    context = {}

    # Current datetime
    now = datetime.datetime.now()

    # Get num days in current month
    days_current_month = calendar.monthrange(now.year, now.month)[1]
    current_month = now.strftime("%b")

    # Create graph labels list
    labels = [str(i) + ' ' + current_month for i in range(1, days_current_month + 1)]
    context['labels'] = labels

    # Estimated emissions based on user baseline
    estimated_daily = np.arange(0, 1000, 1000/days_current_month).tolist() 
    array_estimated_emissions = np.array(estimated_daily)
    rounded_estimated_emissions = np.around(array_estimated_emissions, 1)
    estimated_emissions = list(rounded_estimated_emissions)
    context['estimated_emissions'] = estimated_emissions

    # Get users journeys within current month, descending order
    journeys = request.user.customer.journey_set.all().filter(date_created__month=now.month).order_by('-date_created')
    context['journeys'] = journeys

    # Get users meals within current month, descending order
    recent_meals = request.user.customer.meal_set.all().filter(date_created__month=now.month).order_by('-date_created')
    context['recent_meals'] = recent_meals

    # Create dictionary of day/emissions
    daily_emissions = {}
    for day in labels:
        daily_emissions[day] = 0

    # Sum total_emissions and add emissions per day to dictionary
    total_emissions = 0
    for i in recent_meals:
        total_emissions += i.diet.carbon_price_per_meal
        daily_emissions[str(i.date_created.day) + ' ' + str(i.date_created.strftime("%b"))] += i.diet.carbon_price_per_meal

    # Create dictionary of transportations/occurences
    most_common_transport = {}
    for i in journeys:
        duration = i.duration_hours * 60 + i.duration_minutes
        journey_emissions = duration * i.transportation.carbon_price
        total_emissions += journey_emissions
        daily_emissions[str(i.date_created.day) + ' ' + str(i.date_created.strftime("%b"))] += journey_emissions

        # Count occurences of transportations
        if i.transportation.name not in most_common_transport:
            most_common_transport[i.transportation.name] = 1
        else:
            most_common_transport[i.transportation.name] += 1
    try:
        most_common_transport = max(most_common_transport.items(), key=operator.itemgetter(1))[0]
    except ValueError:
        most_common_transport = None
        pass

    context['total_emissions'] = round(total_emissions, 2)
    context['most_common_transport'] = str(most_common_transport)
    
    # Use numpy to make cumulative array of emissions, round to 1 decimal place
    cumulative_daily_emissions = np.cumsum(list(daily_emissions.values()))
    rounded_cumulative_daily_emissions = np.around(cumulative_daily_emissions, 1)
    actual_emissions = list(rounded_cumulative_daily_emissions)
    context['actual_emissions'] = actual_emissions

    # Set colors for line graph
    chart_colors = []
    for i in range(min(len(estimated_emissions), len(actual_emissions))):
        if estimated_emissions[i] <= actual_emissions[i] and estimated_emissions[i] != 0:
            chart_colors.append('rgb(255, 15, 15)')
        else:
            chart_colors.append('rgb(0, 99, 132)')

    context['chart_colors'] = chart_colors
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def userPage(request, pk):
    context = {}
    customer = Customer.objects.get(id=pk)
    context['customer'] = customer
    account = customer.user
    try:
        friend_list = FriendList.objects.get(user=account)
    except FriendList.DoesNotExist:
        friend_list = FriendList(user=account)
        friend_list.save()
    friends = friend_list.friends.all()
    context['friends'] = friends

    is_self = True
    is_friend = False
    user = request.user
    friend_requests = None
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value # range: ENUM -> friend/friend_request_status.FriendRequestStatus
    if user.is_authenticated and user != account:
        is_self = False
        if friends.filter(pk=user.id):
            is_friend = True
        else:
            # CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
            if get_friend_request_or_false(sender=account, receiver=user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id

            # CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
            elif get_friend_request_or_false(sender=user, receiver=account) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

            # CASE3: No request has been sent. FriendRequestStatus.NO_REQUEST_SENT
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

    else:
        try:
            friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
        except:
            pass

    context['is_self'] = is_self
    context['is_friend'] = is_friend
    context['request_sent'] = request_sent
    context['friend_requests'] = friend_requests
    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
def updateCustomer(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('accounts:home')
        print(form.errors)

    context = {'form': form}
    return render(request, 'accounts/customer_form.html', context)

@login_required(login_url='login')
def createJourney(request):
    form = JourneyForm()
    if request.method == 'POST':
        form = JourneyForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.customer = Customer.objects.get(user=request.user.id)
            stock.save()
            return redirect('accounts:home')

    context = {'form': form}
    return render(request, 'accounts/journey_form.html', context)

@login_required(login_url='login')
def updateJourney(request, pk):
    journey = Journey.objects.get(id=pk)
    form = JourneyForm(instance=journey)

    if request.user.customer == journey.customer:
        if request.method == 'POST':
            form = JourneyForm(request.POST, instance=journey)
            if form.is_valid():
                form.save()
                return redirect('accounts:home')
    else:
        raise Exception("That Journey isn't yours to update.")

    context = {'form': form}
    return render(request, 'accounts/journey_form.html', context)

@login_required(login_url='login')
def deleteJourney(request, pk):
    journey = Journey.objects.get(id=pk)

    if request.user.customer == journey.customer:
        journey.delete()
    else:
        raise Exception("That Journey isn't yours to delete.")
    
    return redirect('accounts:home')

@login_required(login_url='login')
def createMeal(request):
    form = MealForm()
    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.customer = Customer.objects.get(user=request.user.id)
            stock.save()
            return redirect('accounts:home')

    context = {'form': form}
    return render(request, 'accounts/meal_form.html', context)

@login_required(login_url='login')
def updateMeal(request, pk):
    meal = Meal.objects.get(id=pk)
    form = MealForm(instance=meal)

    if request.user.customer == meal.customer:
        if request.method == 'POST':
            form = MealForm(request.POST, instance=meal)
            if form.is_valid():
                form.save()
                return redirect('accounts:home')
    else:
        raise Exception("That Meal isn't yours to update.")

    context = {'form': form}
    return render(request, 'accounts/meal_form.html', context)

@login_required(login_url='login')
def deleteMeal(request, pk):
    meal = Meal.objects.get(id=pk)

    if request.user.customer == meal.customer:
            meal.delete()
    else:
        raise Exception("That Meal isn't yours to delete.")

    return redirect('accounts:home')