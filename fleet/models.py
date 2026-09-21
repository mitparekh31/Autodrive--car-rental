from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default="fa-car")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
        ('Direct-Drive', 'Direct-Drive Dual Motor'),
    ]

    FUEL_CHOICES = [
        ('Electric', 'Electric'),
        ('Gasoline', 'Gasoline'),
        ('Hybrid', 'Hybrid'),
    ]

    name = models.CharField(max_length=150)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(default=2025)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="cars")
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, help_text="Direct link to car image")
    image = models.ImageField(upload_to="cars/", blank=True, null=True)
    
    # Specs
    horsepower = models.IntegerField(help_text="Horsepower (HP)")
    zero_to_sixty = models.CharField(max_length=20, default="3.2s", help_text="0-60 mph time")
    top_speed = models.CharField(max_length=20, default="180 mph")
    seats = models.IntegerField(default=5)
    transmission = models.CharField(max_length=30, choices=TRANSMISSION_CHOICES, default='Automatic')
    fuel_type = models.CharField(max_length=30, choices=FUEL_CHOICES, default='Electric')
    range_or_economy = models.CharField(max_length=50, default="300 mi range")
    luggage_capacity = models.CharField(max_length=50, default="3 Bags")
    
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    tagline = models.CharField(max_length=255, default="100% Real-Time Availability Guarantee")
    features = models.TextField(help_text="Comma-separated features e.g. Autopilot, Premium Audio, Glass Roof", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

    @property
    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(",") if f.strip()]
        return []

    @property
    def primary_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=80"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    booking_ref = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="bookings")
    
    start_date = models.DateField()
    end_date = models.DateField()
    pickup_time = models.CharField(max_length=20, default="10:00 AM")
    pickup_location = models.CharField(max_length=200, default="Downtown Central Hub")
    return_location = models.CharField(max_length=200, default="Downtown Central Hub")
    
    driver_name = models.CharField(max_length=150)
    driver_email = models.EmailField()
    driver_phone = models.CharField(max_length=30)
    
    daily_rate_at_booking = models.DecimalField(max_digits=10, decimal_places=2)
    num_days = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.IntegerField(default=0) # 0, 10, or 25
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Optional Add-ons
    insurance_opt = models.BooleanField(default=False) # +$25/day
    chauffeur_opt = models.BooleanField(default=False) # +$80/day
    gps_opt = models.BooleanField(default=False)       # +$10/day
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            self.booking_ref = f"AD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_ref} - {self.car.name} by {self.user.username}"


class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review ({self.rating}/5) for {self.car.name} by {self.user.username}"
