from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CreateUserForm, JourneyForm
from .models import *
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
                    name=user.username
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
                return redirect('home')
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