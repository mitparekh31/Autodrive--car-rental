from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Sum
from datetime import datetime, date, timedelta
from .models import Car, Category, Booking, Review

def home_view(request):
    categories = Category.objects.all()
    featured_cars = Car.objects.filter(is_available=True)[:6]
    all_cars = Car.objects.filter(is_available=True)
    
    total_fleet = Car.objects.count()
    
    context = {
        'categories': categories,
        'featured_cars': featured_cars,
        'all_cars': all_cars,
        'total_fleet': total_fleet,
    }
    return render(request, 'fleet/home.html', context)


def fleet_list_view(request):
    cars = Car.objects.all()
    categories = Category.objects.all()
    
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    transmission = request.GET.get('transmission', '')
    fuel = request.GET.get('fuel', '')
    sort_by = request.GET.get('sort', 'default')

    if query:
        cars = cars.filter(
            Q(name__icontains=query) | 
            Q(make__icontains=query) | 
            Q(model__icontains=query) |
            Q(features__icontains=query)
        )

    if category_slug:
        cars = cars.filter(category__slug=category_slug)

    if transmission:
        cars = cars.filter(transmission=transmission)

    if fuel:
        cars = cars.filter(fuel_type=fuel)

    if sort_by == 'price_low':
        cars = cars.order_by('daily_rate')
    elif sort_by == 'price_high':
        cars = cars.order_by('-daily_rate')
    elif sort_by == 'power':
        cars = cars.order_by('-horsepower')
    elif sort_by == 'newest':
        cars = cars.order_by('-year')

    context = {
        'cars': cars,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'selected_transmission': transmission,
        'selected_fuel': fuel,
        'sort_by': sort_by,
    }
    return render(request, 'fleet/fleet_list.html', context)


def car_detail_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    similar_cars = Car.objects.filter(category=car.category).exclude(id=car.id)[:3]
    reviews = car.reviews.all().order_by('-created_at')

    today = date.today().strftime('%Y-%m-%d')
    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    context = {
        'car': car,
        'similar_cars': similar_cars,
        'reviews': reviews,
        'today': today,
        'tomorrow': tomorrow,
    }
    return render(request, 'fleet/car_detail.html', context)


@login_required
def add_review_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 5))
            rating = max(1, min(5, rating))
        except (ValueError, TypeError):
            rating = 5
        comment = request.POST.get('comment', '').strip()
        if comment:
            Review.objects.create(
                car=car,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, "✨ Thank you! Your review has been published.")
        else:
            messages.error(request, "Please enter a review comment.")
    return redirect('car_detail', car_id=car.id)


@login_required
def book_car_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        pickup_time = request.POST.get('pickup_time', '10:00 AM')
        pickup_location = request.POST.get('pickup_location', '').strip() or 'Downtown Central Hub'
        return_location = request.POST.get('return_location', '').strip() or pickup_location

        driver_name = request.POST.get('driver_name', '').strip() or request.user.get_full_name() or request.user.username
        driver_email = request.POST.get('driver_email', '').strip() or request.user.email or f"{request.user.username}@autodrive.io"
        driver_phone = request.POST.get('driver_phone', '').strip() or "+91 98765 43210"

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid dates provided. Please select valid rental dates.")
            return redirect('car_detail', car_id=car.id)

        if end_date <= start_date:
            messages.error(request, "Return date must be at least 1 day after pick-up date.")
            return redirect('car_detail', car_id=car.id)

        num_days = (end_date - start_date).days
        subtotal = car.daily_rate * num_days
        grand_total = subtotal

        booking = Booking.objects.create(
            user=request.user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            pickup_time=pickup_time,
            pickup_location=pickup_location,
            return_location=return_location,
            driver_name=driver_name,
            driver_email=driver_email,
            driver_phone=driver_phone,
            daily_rate_at_booking=car.daily_rate,
            num_days=num_days,
            subtotal=subtotal,
            discount_percent=0,
            discount_amount=0,
            insurance_opt=False,
            chauffeur_opt=False,
            gps_opt=False,
            total_price=grand_total,
            status='CONFIRMED'
        )

        messages.success(request, f"🎉 Reservation Confirmed! Your Booking Ref is #{booking.booking_ref}")
        return redirect('my_bookings')

    return redirect('car_detail', car_id=car.id)


def compare_cars_view(request):
    all_cars = Car.objects.all()
    selected_ids = request.GET.getlist('car_ids')

    if not selected_ids:
        cars_to_compare = Car.objects.all()[:3]
        selected_id_ints = [car.id for car in cars_to_compare]
    else:
        selected_id_ints = [int(i) for i in selected_ids if i.isdigit()]
        cars_to_compare = Car.objects.filter(id__in=selected_id_ints)

    context = {
        'all_cars': all_cars,
        'cars_to_compare': cars_to_compare,
        'selected_ids': selected_id_ints,
    }
    return render(request, 'fleet/compare.html', context)


@login_required
def my_bookings_view(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bookings': user_bookings,
    }
    return render(request, 'fleet/my_bookings.html', context)


@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.save()
        messages.info(request, f"Booking #{booking.booking_ref} has been cancelled.")
    return redirect('my_bookings')


@login_required
def add_car_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access restricted to Fleet Manager administrators.")
        return redirect('fleet_list')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        make = request.POST.get('make', '').strip()
        model = request.POST.get('model', '').strip()
        try:
            year = int(request.POST.get('year') or 2025)
            daily_rate = float(request.POST.get('daily_rate') or 5000)
            horsepower = int(request.POST.get('horsepower') or 400)
            seats = int(request.POST.get('seats') or 4)
        except ValueError:
            messages.error(request, "Invalid numeric values provided.")
            return redirect('fleet_list')

        category_id = request.POST.get('category')
        category = get_object_or_404(Category, id=category_id)

        zero_to_sixty = request.POST.get('zero_to_sixty', '3.5s').strip()
        top_speed = request.POST.get('top_speed', '180 mph').strip()
        transmission = request.POST.get('transmission', 'Automatic')
        fuel_type = request.POST.get('fuel_type', 'Gasoline')
        luggage_capacity = request.POST.get('luggage_capacity', '2 Bags').strip()
        tagline = request.POST.get('tagline', '100% Real-Time Availability Guarantee').strip()
        features = request.POST.get('features', '').strip()
        is_featured = request.POST.get('is_featured') == 'on'

        image_file = request.FILES.get('image')

        car = Car.objects.create(
            name=name,
            make=make,
            model=model,
            year=year,
            category=category,
            daily_rate=daily_rate,
            horsepower=horsepower,
            zero_to_sixty=zero_to_sixty,
            top_speed=top_speed,
            seats=seats,
            transmission=transmission,
            fuel_type=fuel_type,
            luggage_capacity=luggage_capacity,
            image=image_file,
            tagline=tagline,
            features=features,
            is_featured=is_featured,
            is_available=True
        )

        messages.success(request, f"🚗 Successfully added '{car.name}' to the fleet inventory!")
        return redirect('fleet_list')

    return redirect('fleet_list')


@login_required
def admin_dashboard_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access restricted to Fleet Manager administrators.")
        return redirect('home')

    total_cars = Car.objects.count()
    total_bookings = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='CONFIRMED').count()
    total_revenue = Booking.objects.filter(status__in=['CONFIRMED', 'COMPLETED']).aggregate(Sum('total_price'))['total_price__sum'] or 0

    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    fleet = Car.objects.all().order_by('-created_at')

    context = {
        'total_cars': total_cars,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'fleet': fleet,
    }
    return render(request, 'fleet/admin_dashboard.html', context)


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to AutoDrive, {user.username}!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get('next') or 'home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

