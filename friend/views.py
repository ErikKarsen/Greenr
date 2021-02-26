# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from accounts.models import Customer
from accounts.views import userPage
from friend.models import FriendRequest, FriendList


@login_required(login_url='login')
def send_friend_request(request, pk):
	user = request.user
	payload = {}
	if user.is_authenticated:
		user_id = pk
		if user_id:
			receiver = Customer.objects.get(pk=user_id).user
			try:
				# Get any friend requests (active and not-active)
				friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
				# find if any of them are active (pending)
				try:
					for request in friend_requests:
						if request.is_active:
							raise Exception("You already sent them a friend request.")
					# If none are active create a new friend request
					FriendRequest.objects.create(sender=user, receiver=receiver)
					payload['response'] = "Friend request sent."
				except Exception as e:
					payload['response'] = str(e)
			except FriendRequest.DoesNotExist:
				# There are no friend requests so create one.
				FriendRequest.objects.create(sender=user, receiver=receiver)
				payload['response'] = "Friend request sent."

			if payload['response'] == None:
				payload['response'] = "Something went wrong."
		else:
			payload['response'] = "Unable to send a friend request."
	else:
		payload['response'] = "You must be authenticated to send a friend request."

	return redirect('accounts:user_page', pk=pk)

@login_required(login_url='login')
def accept_friend_request(request, pk):
	sender = Customer.objects.get(pk=pk).user
	receiver = request.user
	payload = {}

	try:
		friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).order_by('-id')[0]
	except FriendRequest.DoesNotExist:
		payload['response'] = "Friend Request does not exist."

	if friend_request:
		# found the request. Now accept it
		friend_request.accept()

	return redirect('accounts:user_page', pk=pk)

@login_required(login_url='login')
def decline_friend_request(request, pk):
	sender = Customer.objects.get(pk=pk).user
	receiver = request.user
	payload = {}

	try:
		friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).order_by('-id')[0]
	except FriendRequest.DoesNotExist:
		payload['response'] = "Friend request does not exist."

	if friend_request:
		# found the request. Now decline it
		friend_request.decline()
	
	return redirect('accounts:user_page', pk=pk)

@login_required(login_url='login')
def cancel_friend_request(request, pk):
	receiver = Customer.objects.get(pk=pk).user
	sender = request.user
	payload = {}

	try:
		friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).order_by('-id')[0]
	except FriendRequest.DoesNotExist:
		payload['response'] = "Friend request does not exist."

	if friend_request:
		# found the request. Now cancel it
		friend_request.cancel()

	return redirect('accounts:user_page', pk=pk)

@login_required(login_url='login')
def get_friends_list(request):
	context = {}
	user = request.user

	
	friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
	context['friend_requests'] = friend_requests

	friends_list = FriendList.objects.get(user=user).friends.all()
	context['friends_list'] = friends_list

	return render(request, "friend/network.html", context)
