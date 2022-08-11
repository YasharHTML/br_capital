from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_investor, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('offer/<str:pk>/', views.offer, name='offer'),
    path('offers/', views.offers, name='offers'),
]