from django.urls import path

from friend.views import(
    send_friend_request,
    # accept_friend_request
)

app_name = "friend"

urlpatterns = [
    path('friend_request/<str:pk>/', send_friend_request, name="friend-request"),
    # path('accept_friend_request/<friend_request_id>', accept_friend_request, name="friend-request-accept"),
]
