# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from accounts.models import Customer
from accounts.views import userPage
from friend.models import FriendRequest, FriendList


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



					# friend_request = FriendRequest(sender=user, receiver=receiver)
					# friend_request.save()
					payload['response'] = "Friend request sent."
				except Exception as e:
					payload['response'] = str(e)
			except FriendRequest.DoesNotExist:
				# There are no friend requests so create one.
				FriendRequest.objects.create(sender=user, receiver=receiver)

				# friend_request = FriendRequest(sender=user, receiver=receiver)
				# friend_request.save()
				payload['response'] = "Friend request sent."

			if payload['response'] == None:
				payload['response'] = "Something went wrong."
		else:
			payload['response'] = "Unable to send a friend request."
	else:
		payload['response'] = "You must be authenticated to send a friend request."

	print(payload['response'])

	return redirect('accounts:user_page', pk=pk)



    # return redirect('accounts:user_page' pk='{{user_id}}')


	# return HttpResponse(json.dumps(payload), content_type="application/json")


# def accept_friend_request(request, *args, **kwargs):
# 	user = request.user
# 	payload = {}
# 	if request.method == "GET" and user.is_authenticated:
# 		friend_request_id = kwargs.get("friend_request_id")
# 		if friend_request_id:
# 			friend_request = FriendRequest.objects.get(pk=friend_request_id)
# 			# confirm that is the correct request
# 			if friend_request.receiver == user:
# 				if friend_request:
# 					# found the request. Now accept it
# 					friend_request.accept()
# 					payload['response'] = "Friend request accepted."
# 				else:
# 					payload['response'] = "Something went wrong."
# 			else:
# 				payload['response'] = "That is not your request to accept."
# 		else:
# 			payload['response'] = "Unable to accept that friend request."
# 	else:
# 		payload['response'] = "You must ne authenticated to accept a friend request."
# 	return HttpResponse(json.dumps(payload), content_type="application/json")
	