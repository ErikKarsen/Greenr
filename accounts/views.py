from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import *
from .models import *
from friend.models import FriendList, FriendRequest
from django.db.models import Sum


# Create your views here.
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
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
                return redirect('login')
                


        context = {'form': form}
        return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                if request.user.customer.first_name:
                    return redirect('home')
                else:
                    return redirect('update_customer')
            else:
                messages.info(request, 'Invalid Username or Password')
                
        context = {}
        return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):

    journeys = request.user.customer.journey_set.all()


    total_emissions = 0
    for i in journeys:
        duration = i.duration_hours * 60 + i.duration_minutes
        total_emissions += duration * i.transportation.carbon_price

    context = {'journeys': journeys, 'total_emissions': round(total_emissions, 2)}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def userPage(request, pk):

    is_self = True
    user = request.user
    customer = Customer.objects.get(id=pk)

    if user.is_authenticated and user != customer.user:
        is_self = False
        
    context = {'customer':customer, 'is_self': is_self}
    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
def updateCustomer(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('user_page')
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
            return redirect('home')

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
            return redirect('home')

    context = {'form': form}
    return render(request, 'accounts/journey_form.html', context)

@login_required(login_url='login')
def deleteJourney(request, pk):
    journey = Journey.objects.get(id=pk)

    if request.method == 'POST':
        journey.delete()
        return redirect('home')
        
    context = {'item': journey}
    return render(request, 'accounts/delete.html', context)