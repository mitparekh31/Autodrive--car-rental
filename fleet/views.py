from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
from .models import Car, Category, Booking, Review, Driver, Payment

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
    certified_drivers = Driver.objects.filter(is_available=True).order_by('-rating')

    today_date = date.today()
    tomorrow_date = today_date + timedelta(days=1)

    # Check vehicle availability for default dates (today to tomorrow)
    car_conflict = car.get_overlapping_booking(today_date, tomorrow_date)
    is_car_available_for_dates = (car_conflict is None)
    car_conflict_info = (
        f"Booked ({car_conflict.start_date.strftime('%b %d')} - {car_conflict.end_date.strftime('%b %d')})"
        if car_conflict else None
    )
    upcoming_car_bookings = car.get_upcoming_bookings()

    # Pre-calculate availability for default dates (today to tomorrow)
    drivers_with_status = []
    available_drivers_count = 0
    for d in certified_drivers:
        conflict = d.get_overlapping_booking(today_date, tomorrow_date)
        is_free = (conflict is None)
        if is_free:
            available_drivers_count += 1
        conflict_msg = f"Booked ({conflict.start_date.strftime('%b %d')} - {conflict.end_date.strftime('%b %d')})" if conflict else None
        drivers_with_status.append({
            'driver': d,
            'is_available_for_dates': is_free,
            'conflict_info': conflict_msg,
        })

    today = today_date.strftime('%Y-%m-%d')
    tomorrow = tomorrow_date.strftime('%Y-%m-%d')
    
    context = {
        'car': car,
        'similar_cars': similar_cars,
        'reviews': reviews,
        'drivers': certified_drivers,
        'drivers_with_status': drivers_with_status,
        'available_drivers_count': available_drivers_count,
        'today': today,
        'tomorrow': tomorrow,
        'is_car_available_for_dates': is_car_available_for_dates,
        'car_conflict_info': car_conflict_info,
        'upcoming_car_bookings': upcoming_car_bookings,
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

    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "Administrators cannot book vehicles. Please manage fleet operations via the Admin Dashboard.")
        return redirect('car_detail', car_id=car.id)

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        pickup_time = request.POST.get('pickup_time', '10:00 AM')
        pickup_location = request.POST.get('pickup_location', '').strip() or 'Downtown Central Hub'
        return_location = request.POST.get('return_location', '').strip() or pickup_location

        driver_name = request.POST.get('driver_name', '').strip() or request.user.get_full_name() or request.user.username
        driver_email = request.POST.get('driver_email', '').strip() or request.user.email or f"{request.user.username}@autodrive.io"
        driver_phone = request.POST.get('driver_phone', '').strip() or "+91 98765 43210"

        drive_mode = request.POST.get('drive_mode', 'self')
        driver_id = request.POST.get('driver_id')
        customer_license = request.POST.get('customer_license', '').strip()

        assigned_driver = None
        chauffeur_fee = Decimal('0.00')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid dates provided. Please select valid rental dates.")
            return redirect('car_detail', car_id=car.id)

        if end_date <= start_date:
            messages.error(request, "Return date must be at least 1 day after pick-up date.")
            return redirect('car_detail', car_id=car.id)

        try:
            with transaction.atomic():
                # Lock car row for concurrency safety during booking
                car_locked = Car.objects.select_for_update().get(id=car.id)

                # Strict car slot overlap check: Ensure car is not already booked during this time slot
                conflicting_car = car_locked.get_overlapping_booking(start_date, end_date)
                if conflicting_car:
                    messages.error(
                        request,
                        f"🚫 Time Slot Unavailable: {car_locked.name} is already booked from "
                        f"{conflicting_car.start_date.strftime('%b %d, %Y')} to "
                        f"{conflicting_car.end_date.strftime('%b %d, %Y')} "
                        f"(Booking #{conflicting_car.booking_ref}). "
                        f"Please choose a different time slot or select another luxury vehicle."
                    )
                    return redirect('car_detail', car_id=car.id)

                num_days = (end_date - start_date).days
                subtotal = car_locked.daily_rate * num_days

                if drive_mode == 'chauffeur':
                    if not driver_id:
                        messages.error(request, "Please select a certified chauffeur to proceed with driver service.")
                        return redirect('car_detail', car_id=car.id)
                    try:
                        assigned_driver = Driver.objects.select_for_update().get(id=driver_id, is_available=True)
                    except (Driver.DoesNotExist, ValueError):
                        messages.error(request, "Selected certified driver is invalid or currently inactive.")
                        return redirect('car_detail', car_id=car.id)

                    # Strict overlap check: Ensure driver is not already booked during this time window
                    conflicting = assigned_driver.get_overlapping_booking(start_date, end_date)
                    if conflicting:
                        messages.error(
                            request,
                            f"Chauffeur {assigned_driver.name} is already reserved from {conflicting.start_date.strftime('%b %d, %Y')} "
                            f"to {conflicting.end_date.strftime('%b %d, %Y')}. Please choose another certified driver or select different dates."
                        )
                        return redirect('car_detail', car_id=car.id)

                    chauffeur_fee = assigned_driver.daily_fee * num_days

                grand_total = subtotal + chauffeur_fee

                # Payment Details from Dummy Gateway Form
                payment_method = request.POST.get('payment_method', 'card')
                card_number = request.POST.get('card_number', '').replace(' ', '').strip()
                upi_id = request.POST.get('upi_id', '').strip()
                bank_name = request.POST.get('bank_name', '').strip()
                simulate_action = request.POST.get('simulate_payment_action', 'success')

                is_failed = (simulate_action == 'fail' or card_number.endswith('0000'))
                booking_status = 'PENDING' if is_failed else 'CONFIRMED'
                payment_status = 'FAILED' if is_failed else 'PAID'
                txn_id = f"TXN-FAIL-{uuid.uuid4().hex[:8].upper()}" if is_failed else f"TXN-{uuid.uuid4().hex[:10].upper()}"
                paid_at = None if is_failed else timezone.now()

                card_brand = 'Visa'
                if card_number.startswith('5'):
                    card_brand = 'Mastercard'
                elif card_number.startswith('3'):
                    card_brand = 'American Express'
                elif card_number.startswith('6'):
                    card_brand = 'RuPay'
                last4 = card_number[-4:] if len(card_number) >= 4 else '4242'

                booking = Booking.objects.create(
                    user=request.user,
                    car=car_locked,
                    start_date=start_date,
                    end_date=end_date,
                    pickup_time=pickup_time,
                    pickup_location=pickup_location,
                    return_location=return_location,
                    drive_mode=drive_mode,
                    assigned_driver=assigned_driver,
                    customer_license=customer_license,
                    chauffeur_fee=chauffeur_fee,
                    driver_name=driver_name,
                    driver_email=driver_email,
                    driver_phone=driver_phone,
                    daily_rate_at_booking=car_locked.daily_rate,
                    num_days=num_days,
                    subtotal=subtotal,
                    discount_percent=0,
                    discount_amount=0,
                    insurance_opt=False,
                    chauffeur_opt=(drive_mode == 'chauffeur'),
                    gps_opt=False,
                    total_price=grand_total,
                    status=booking_status,
                    payment_status=payment_status,
                    payment_method=payment_method,
                    transaction_id=txn_id,
                    paid_at=paid_at
                )

                Payment.objects.update_or_create(
                    booking=booking,
                    defaults={
                        'transaction_id': txn_id,
                        'payment_method': payment_method,
                        'amount': grand_total,
                        'status': 'SUCCESS' if not is_failed else 'FAILED',
                        'card_last_four': last4,
                        'card_brand': card_brand,
                        'upi_id': upi_id if payment_method == 'upi' else '',
                        'bank_name': bank_name if payment_method == 'netbanking' else '',
                        'gateway_response': 'Simulated Payment Gateway Approval (HTTP 200 - OK)' if not is_failed else 'Simulated Issuer Decline (Card ending in 0000 - Insufficient Test Funds)'
                    }
                )
        except Exception as e:
            messages.error(request, f"Unable to complete reservation: {str(e)}")
            return redirect('car_detail', car_id=car.id)

        if is_failed:
            messages.warning(
                request,
                f"⚠️ Payment Declined: Bank Issuer declined transaction #{txn_id}. "
                f"Your vehicle slot has been provisionally reserved (#{booking.booking_ref}). "
                f"Please complete payment to confirm your booking."
            )
            return redirect('checkout_payment', booking_ref=booking.booking_ref)

        method_names = dict(Booking.PAYMENT_METHOD_CHOICES)
        method_label = method_names.get(payment_method, 'Payment')
        messages.success(
            request,
            f"🎉 Reservation Confirmed! Payment of ₹{grand_total:,.0f} Successful via {method_label}! (Txn ID: #{txn_id}). Your Booking #{booking.booking_ref} is confirmed."
        )
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
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, "Administrators manage fleet operations from the Admin Dashboard.")
        return redirect('admin_dashboard')

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
def delete_car_view(request, car_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access restricted to Fleet Manager administrators.")
        return redirect('home')

    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        car_name = car.name
        car.delete()
        messages.success(request, f"🗑️ Vehicle '{car_name}' has been permanently deleted from the fleet inventory.")
        next_page = request.POST.get('next')
        if next_page == 'fleet':
            return redirect('fleet_list')
        return redirect('admin_dashboard')

    messages.warning(request, "Please confirm deletion using the action button.")
    return redirect('admin_dashboard')


@login_required
def admin_dashboard_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access restricted to Fleet Manager administrators.")
        return redirect('home')

    total_cars = Car.objects.count()
    total_bookings = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='CONFIRMED').count()
    total_revenue = Booking.objects.filter(status__in=['CONFIRMED', 'COMPLETED']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(is_available=True).count()

    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    fleet = Car.objects.all().order_by('-created_at')
    certified_drivers = Driver.objects.all().order_by('-rating', '-experience_years')

    context = {
        'total_cars': total_cars,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'total_drivers': total_drivers,
        'active_drivers': active_drivers,
        'recent_bookings': recent_bookings,
        'fleet': fleet,
        'drivers': certified_drivers,
        'categories': Category.objects.all(),
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


def driver_availability_api(request):
    """
    API endpoint returning all certified drivers with availability status
    for the requested start_date and end_date.
    """
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'start_date and end_date are required'}, status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid date format (must be YYYY-MM-DD)'}, status=400)

    if end_date <= start_date:
        return JsonResponse({'error': 'end_date must be after start_date'}, status=400)

    drivers = Driver.objects.filter(is_available=True).order_by('-rating')
    drivers_data = []
    available_count = 0

    for d in drivers:
        conflict = d.get_overlapping_booking(start_date, end_date)
        is_free = (conflict is None)
        if is_free:
            available_count += 1
        conflict_msg = f"Booked ({conflict.start_date.strftime('%b %d')} - {conflict.end_date.strftime('%b %d')})" if conflict else None

        drivers_data.append({
            'id': d.id,
            'name': d.name,
            'rating': str(d.rating),
            'badge_type': d.badge_type,
            'experience_years': d.experience_years,
            'daily_fee': float(d.daily_fee),
            'is_available': is_free,
            'conflict_info': conflict_msg,
        })

    return JsonResponse({
        'status': 'success',
        'start_date': start_date_str,
        'end_date': end_date_str,
        'available_count': available_count,
        'total_count': len(drivers_data),
        'drivers': drivers_data,
    })


def car_availability_api(request):
    """
    API endpoint returning real-time slot availability for a specified car and date range.
    """
    car_id = request.GET.get('car_id')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not car_id or not start_date_str or not end_date_str:
        return JsonResponse({'error': 'car_id, start_date and end_date are required'}, status=400)

    try:
        car = Car.objects.get(id=car_id)
    except (Car.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Car not found'}, status=404)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid date format (must be YYYY-MM-DD)'}, status=400)

    if end_date <= start_date:
        return JsonResponse({'error': 'end_date must be after start_date'}, status=400)

    conflict = car.get_overlapping_booking(start_date, end_date)
    is_free = (conflict is None)
    conflict_msg = (
        f"Booked from {conflict.start_date.strftime('%b %d, %Y')} to {conflict.end_date.strftime('%b %d, %Y')} (#{conflict.booking_ref})"
        if conflict else None
    )

    upcoming = car.get_upcoming_bookings()
    booked_slots = [
        {
            'start': b.start_date.strftime('%Y-%m-%d'),
            'end': b.end_date.strftime('%Y-%m-%d'),
            'start_display': b.start_date.strftime('%b %d, %Y'),
            'end_display': b.end_date.strftime('%b %d, %Y'),
            'ref': b.booking_ref
        }
        for b in upcoming
    ]

    return JsonResponse({
        'status': 'success',
        'car_id': car.id,
        'car_name': car.name,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'is_available': is_free,
        'conflict_info': conflict_msg,
        'booked_slots': booked_slots,
    })


@login_required
def checkout_payment_view(request, booking_ref):
    """
    Dedicated luxury payment gateway screen for verifying and paying a reservation.
    """
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)
    payment = getattr(booking, 'payment_record', None)

    context = {
        'booking': booking,
        'car': booking.car,
        'payment': payment,
    }
    return render(request, 'fleet/checkout_payment.html', context)


@login_required
def process_payment_view(request, booking_ref):
    """
    Process dummy payment from dedicated checkout portal with card/UPI/bank simulation.
    """
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'card')
        card_number = request.POST.get('card_number', '').replace(' ', '').strip()
        card_name = request.POST.get('card_name', '').strip() or booking.driver_name
        upi_id = request.POST.get('upi_id', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        simulate_action = request.POST.get('simulate_payment_action', 'success')

        is_failed = (simulate_action == 'fail' or card_number.endswith('0000'))

        if is_failed:
            txn_id = f"TXN-FAIL-{uuid.uuid4().hex[:8].upper()}"
            booking.payment_status = 'FAILED'
            booking.transaction_id = txn_id
            booking.save()

            Payment.objects.update_or_create(
                booking=booking,
                defaults={
                    'transaction_id': txn_id,
                    'payment_method': payment_method,
                    'amount': booking.total_price,
                    'status': 'FAILED',
                    'card_last_four': card_number[-4:] if len(card_number) >= 4 else '0000',
                    'card_brand': 'Test Card',
                    'upi_id': upi_id,
                    'bank_name': bank_name,
                    'gateway_response': 'Simulated Issuer Decline (Card ending in 0000 - Insufficient Test Funds)'
                }
            )
            messages.error(
                request,
                f"❌ Payment Declined: Simulated issuer declined transaction #{txn_id}. Please try a valid test card or UPI."
            )
            return redirect('checkout_payment', booking_ref=booking.booking_ref)

        # Successful payment approval
        txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        card_brand = 'Visa'
        if card_number.startswith('5'):
            card_brand = 'Mastercard'
        elif card_number.startswith('3'):
            card_brand = 'American Express'
        elif card_number.startswith('6'):
            card_brand = 'RuPay'
        last4 = card_number[-4:] if len(card_number) >= 4 else '4242'

        booking.status = 'CONFIRMED'
        booking.payment_status = 'PAID'
        booking.payment_method = payment_method
        booking.transaction_id = txn_id
        booking.paid_at = timezone.now()
        booking.save()

        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'transaction_id': txn_id,
                'payment_method': payment_method,
                'amount': booking.total_price,
                'status': 'SUCCESS',
                'card_last_four': last4,
                'card_brand': card_brand,
                'upi_id': upi_id,
                'bank_name': bank_name,
                'gateway_response': 'Simulated Payment Gateway Approval (HTTP 200 - OK)'
            }
        )

        method_names = dict(Booking.PAYMENT_METHOD_CHOICES)
        method_label = method_names.get(payment_method, 'Payment')
        messages.success(
            request,
            f"🎉 Reservation Confirmed! Payment of ₹{booking.total_price:,.0f} Successful via {method_label}! (Txn #{txn_id}). Your reservation is confirmed."
        )
        return redirect('my_bookings')

    return redirect('checkout_payment', booking_ref=booking.booking_ref)


@login_required
def payment_receipt_view(request, booking_ref):
    """
    Printable / Downloadable Digital Tax Invoice & Payment Receipt.
    """
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)
    payment = getattr(booking, 'payment_record', None)
    context = {
        'booking': booking,
        'payment': payment,
        'car': booking.car,
    }
    return render(request, 'fleet/payment_receipt.html', context)



