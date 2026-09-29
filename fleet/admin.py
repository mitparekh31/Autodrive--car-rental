from django.contrib import admin
from .models import Category, Car, Booking, Review, Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'rating', 'experience_years', 'daily_fee', 'phone', 'is_available')
    list_filter = ('is_available', 'badge_type')
    search_fields = ('name', 'phone', 'license_number')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'model', 'year', 'category', 'daily_rate', 'fuel_type', 'is_available')
    list_filter = ('category', 'fuel_type', 'transmission', 'is_available')
    search_fields = ('name', 'make', 'model')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'user', 'car', 'drive_mode', 'assigned_driver', 'start_date', 'end_date', 'total_price', 'status')
    list_filter = ('status', 'drive_mode', 'start_date')
    search_fields = ('booking_ref', 'user__username', 'car__name', 'driver_name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
