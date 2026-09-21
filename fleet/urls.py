from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('fleet/', views.fleet_list_view, name='fleet_list'),
    path('fleet/add/', views.add_car_view, name='add_car'),
    path('car/<int:car_id>/', views.car_detail_view, name='car_detail'),
    path('car/<int:car_id>/book/', views.book_car_view, name='book_car'),
    path('car/<int:car_id>/review/', views.add_review_view, name='add_review'),
    path('compare/', views.compare_cars_view, name='compare'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
