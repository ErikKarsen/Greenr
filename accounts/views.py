from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random


from .forms import *
from .models import *

from friend.models import FriendList, FriendRequest
from friend.utils import get_friend_request_or_false
from friend.friend_request_status import FriendRequestStatus

from django.db.models import Sum


# Create your views here.
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
    journeys = request.user.customer.journey_set.all()
    context['journeys'] = journeys
    user = request.user


    try:
        friend_list = FriendList.objects.get(user=user)
    except FriendList.DoesNotExist:
        friend_list = FriendList(user=user)
        friend_list.save()

    friends_list = friend_list.friends.all()

    profiles = Customer.objects.exclude(id=user.id)

    profiles_list = list(profiles)


    suggested_profiles = []

    try:
        while profiles_list:
            random_profiles = random.sample(profiles_list, 3)
            for profile in random_profiles:
                if profile not in suggested_profiles:
                    if profile not in friends_list:
                        profiles_list.remove(profile)
                        suggested_profiles.append(profile)
                
            if len(suggested_profiles) >= 3:
                break

    except ValueError:
        pass

    context['suggested_profiles'] = suggested_profiles


    total_emissions = 0
    for i in journeys:
        duration = i.duration_hours * 60 + i.duration_minutes
        total_emissions += duration * i.transportation.carbon_price
    context['total_emissions'] = round(total_emissions, 2)
    

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

    if request.method == 'POST':
        form = JourneyForm(request.POST, instance=journey)
        if form.is_valid():
            form.save()
            return redirect('accounts:home')

    context = {'form': form}
    return render(request, 'accounts/journey_form.html', context)

@login_required(login_url='login')
def deleteJourney(request, pk):
    journey = Journey.objects.get(id=pk)


    if request.method == 'POST':
        journey.delete()
        return redirect('accounts:home')
        
    context = {'item': journey}
    return render(request, 'accounts/delete.html', context)