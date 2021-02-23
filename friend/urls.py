from django.urls import path

from friend.views import(
    send_friend_request,
    accept_friend_request,
    decline_friend_request,
    cancel_friend_request
)

app_name = "friend"

urlpatterns = [
    path('friend_request/<str:pk>/', send_friend_request, name="friend-request"),
    path('accept_friend_request/<str:pk>', accept_friend_request, name="friend-request-accept"),
    path('friend_request_decline/<str:pk>/', decline_friend_request, name='friend-request-decline'),
    path('friend_request_cancel/<str:pk>/', cancel_friend_request, name='friend-request-cancel'),

]
