from django.urls import path

from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"


urlpatterns = [
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('', views.home, name='home'),
    path('account/<str:pk>/', views.userPage, name="user_page"),
    path('edit_profile/', views.updateCustomer, name='update_customer'),

    path('create_journey', views.createJourney, name='create_journey'),
    path('update_journey/<str:pk>/', views.updateJourney, name='update_journey'),
    path('delete_journey/<str:pk>/', views.deleteJourney, name='delete_journey'),


    path('create_meal', views.createMeal, name='create_meal'),
    path('update_meal/<str:pk>/', views.updateMeal, name='update_meal'),
    path('delete_meal/<str:pk>/', views.deleteMeal, name='delete_meal'),

    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
     name='reset_password'),

    path('password_reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'), 
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_form.html'), 
     name='password_reset_confirm'),

    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_done.html'), 
        name='password_reset_complete'),
]
