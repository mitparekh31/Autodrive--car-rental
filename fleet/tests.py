from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from fleet.models import Category, Car, Booking, Driver, Payment
from datetime import date, timedelta
from decimal import Decimal

class AutoDriveFleetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testdriver", password="password123")
        self.category = Category.objects.create(name="Electric Supercars", icon="fa-bolt")
        self.car = Car.objects.create(
            name="Porsche Taycan Turbo S",
            make="Porsche",
            model="Taycan Turbo S",
            year=2025,
            category=self.category,
            daily_rate=Decimal("8999.00"),
            horsepower=750,
            zero_to_sixty="2.6s",
            top_speed="162 mph",
            seats=4,
            transmission="Automatic",
            fuel_type="Electric"
        )
        self.driver = Driver.objects.create(
            name="Rajesh Sharma",
            phone="+91 98201 12345",
            email="rajesh@autodrive.io",
            license_number="MH-01-2015-004928",
            experience_years=9,
            rating=Decimal("4.9"),
            trips_completed=520,
            daily_fee=Decimal("800.00"),
            badge_type="Master Executive Chauffeur",
            is_available=True
        )

    def test_homepage_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AutoDrive")
        self.assertContains(response, "RENT YOUR DREAM")

    def test_fleet_list_renders(self):
        response = self.client.get('/fleet/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Porsche Taycan Turbo S")

    def test_car_detail_renders(self):
        response = self.client.get(f'/car/{self.car.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Porsche Taycan Turbo S")

    def test_compare_matrix(self):
        response = self.client.get('/compare/')
        self.assertEqual(response.status_code, 200)

    def test_booking_creation(self):
        self.client.login(username="testdriver", password="password123")
        start = date.today().strftime('%Y-%m-%d')
        end = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        
        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': start,
            'end_date': end,
            'pickup_time': '10:00 AM',
            'pickup_location': 'Downtown Airport Hub',
            'return_location': 'Downtown Airport Hub',
            'insurance': 'on',
        })
        
        self.assertEqual(response.status_code, 302) # Redirect to my_bookings
        booking = Booking.objects.get(user=self.user, car=self.car)
        self.assertEqual(booking.num_days, 5)
        self.assertEqual(booking.discount_percent, 0)
        self.assertEqual(booking.status, 'CONFIRMED')
    def test_admin_cannot_book_car(self):
        admin_user = User.objects.create_user(username="adminuser", password="password123", is_staff=True)
        self.client.login(username="adminuser", password="password123")
        start = date.today().strftime('%Y-%m-%d')
        end = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')

        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': start,
            'end_date': end,
            'pickup_time': '10:00 AM',
            'pickup_location': 'Downtown Airport Hub',
            'return_location': 'Downtown Airport Hub',
            'drive_mode': 'self',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Administrators cannot book vehicles")
        self.assertEqual(Booking.objects.filter(user=admin_user).count(), 0)

    def test_admin_views_car_detail_without_reservation_feature(self):
        admin_user = User.objects.create_user(username="adminmanager", password="password123", is_staff=True)
        self.client.login(username="adminmanager", password="password123")
        response = self.client.get(f'/car/{self.car.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fleet Manager")
        self.assertContains(response, "Admin Console")
        self.assertNotContains(response, "Instant Reservation")
        self.assertNotContains(response, "Confirm Instant Booking")
        self.assertNotContains(response, "Pick-Up Date")

    def test_admin_my_bookings_redirects_to_dashboard(self):
        admin_user = User.objects.create_user(username="adminuser2", password="password123", is_staff=True)
        self.client.login(username="adminuser2", password="password123")
        response = self.client.get('/my-bookings/', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fleet Manager Dashboard")
        self.assertContains(response, "Administrators manage fleet operations from the Admin Dashboard")

    def test_admin_fleet_list_has_no_reserve_button(self):
        admin_user = User.objects.create_user(username="adminuser3", password="password123", is_staff=True)
        self.client.login(username="adminuser3", password="password123")
        response = self.client.get('/fleet/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage Specs")
        self.assertNotContains(response, "Reserve Ride")
        self.assertNotContains(response, "My Bookings")

    def test_admin_dashboard_shows_detailed_certified_drivers_roster(self):
        admin_user = User.objects.create_user(username="adminuser4", password="password123", is_staff=True)
        self.client.login(username="adminuser4", password="password123")
        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Certified Chauffeur Fleet & Drivers Roster")
        self.assertContains(response, self.driver.name)
        self.assertContains(response, self.driver.badge_type)
        self.assertContains(response, self.driver.license_number)
        self.assertContains(response, "4.9")
        self.assertContains(response, "9 Yrs Exp.")
        self.assertContains(response, "+91 98201 12345")
        self.assertContains(response, "800")
        self.assertContains(response, "Available")
        self.assertContains(response, "Fleet Inventory Management")
        self.assertContains(response, self.car.name)

    def test_add_car_modal_fields_equally_aligned(self):
        admin_user = User.objects.create_user(username="adminuser5", password="password123", is_staff=True)
        self.client.login(username="adminuser5", password="password123")
        response = self.client.get('/fleet/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "id=\"addCarModal\"")
        self.assertContains(response, "fleet-form-group")
        self.assertContains(response, "fleet-form-control")
        self.assertContains(response, "fleet-form-select")

    def test_admin_can_delete_car(self):
        admin_user = User.objects.create_user(username="adminuser6", password="password123", is_staff=True)
        self.client.login(username="adminuser6", password="password123")
        car_to_delete = Car.objects.create(
            name="Audi RS e-tron GT",
            make="Audi",
            model="e-tron GT",
            year=2024,
            category=self.category,
            daily_rate=Decimal("6500.00"),
            horsepower=637,
            zero_to_sixty="3.1s",
            top_speed="155 mph",
            seats=4
        )
        car_id = car_to_delete.id
        response = self.client.post(f'/fleet/{car_id}/delete/', {'next': 'dashboard'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Car.objects.filter(id=car_id).exists())
        self.assertContains(response, "permanently deleted")

    def test_non_admin_cannot_delete_car(self):
        self.client.login(username="testdriver", password="password123")
        response = self.client.post(f'/fleet/{self.car.id}/delete/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Car.objects.filter(id=self.car.id).exists())
        self.assertContains(response, "Access restricted to Fleet Manager administrators")

    def test_admin_dashboard_renders_delete_button_and_modal(self):
        admin_user = User.objects.create_user(username="adminuser7", password="password123", is_staff=True)
        self.client.login(username="adminuser7", password="password123")
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"adminDeleteCarModal{self.car.id}")
        self.assertContains(response, "Delete Vehicle")

    def test_driver_availability_schedule_overlap(self):
        start = date(2026, 10, 10)
        end = date(2026, 10, 15)

        # Before booking, driver is free
        self.assertTrue(self.driver.is_available_between(start, end))

        # Customer 1 books the driver
        Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=start,
            end_date=end,
            pickup_location="Airport Hub",
            return_location="Airport Hub",
            drive_mode="chauffeur",
            assigned_driver=self.driver,
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=5,
            subtotal=self.car.daily_rate * 5,
            total_price=self.car.daily_rate * 5 + self.driver.daily_fee * 5,
            status="CONFIRMED"
        )

        # Overlapping ranges must be unavailable
        self.assertFalse(self.driver.is_available_between(date(2026, 10, 12), date(2026, 10, 14)))
        self.assertFalse(self.driver.is_available_between(date(2026, 10, 8), date(2026, 10, 11)))
        self.assertFalse(self.driver.is_available_between(date(2026, 10, 14), date(2026, 10, 18)))

        # Non-overlapping ranges must remain available
        self.assertTrue(self.driver.is_available_between(date(2026, 10, 1), date(2026, 10, 5)))
        self.assertTrue(self.driver.is_available_between(date(2026, 10, 20), date(2026, 10, 25)))

    def test_customer2_cannot_book_driver_already_booked_by_customer1(self):
        customer1 = User.objects.create_user(username="customer1", password="password123")
        customer2 = User.objects.create_user(username="customer2", password="password123")

        start1 = date(2026, 11, 1)
        end1 = date(2026, 11, 5)

        # Customer 1 books Driver 1
        Booking.objects.create(
            user=customer1,
            car=self.car,
            start_date=start1,
            end_date=end1,
            drive_mode="chauffeur",
            assigned_driver=self.driver,
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=4,
            subtotal=self.car.daily_rate * 4,
            total_price=self.car.daily_rate * 4 + self.driver.daily_fee * 4,
            status="CONFIRMED"
        )

        # Customer 2 creates a separate car to avoid car conflicts
        car2 = Car.objects.create(
            name="Ferrari 296 GTB",
            make="Ferrari",
            model="296 GTB",
            year=2025,
            category=self.category,
            daily_rate=Decimal("12000.00"),
            horsepower=819,
            zero_to_sixty="2.9s",
            top_speed="205 mph",
            seats=2
        )

        # Customer 2 attempts to book Driver 1 for overlapping dates (Nov 3 to Nov 7)
        self.client.login(username="customer2", password="password123")
        response = self.client.post(f'/car/{car2.id}/book/', {
            'start_date': '2026-11-03',
            'end_date': '2026-11-07',
            'drive_mode': 'chauffeur',
            'driver_id': self.driver.id,
            'pickup_location': 'Airport Terminal',
            'return_location': 'Airport Terminal',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Chauffeur {self.driver.name} is already reserved")
        # Ensure customer2 was NOT able to book the driver
        self.assertEqual(Booking.objects.filter(user=customer2).count(), 0)

    def test_driver_availability_api(self):
        # Book driver for Dec 1 to Dec 5
        Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 5),
            drive_mode="chauffeur",
            assigned_driver=self.driver,
            driver_name="Test Driver",
            driver_email="test@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=4,
            subtotal=self.car.daily_rate * 4,
            total_price=self.car.daily_rate * 4,
            status="CONFIRMED"
        )

        # Query overlapping dates
        response = self.client.get('/api/driver-availability/?start_date=2026-12-02&end_date=2026-12-04')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')

        driver_item = next(d for d in data['drivers'] if d['id'] == self.driver.id)
        self.assertFalse(driver_item['is_available'])
        self.assertIn("Booked", driver_item['conflict_info'])

        # Query non-overlapping dates
        response2 = self.client.get('/api/driver-availability/?start_date=2026-12-10&end_date=2026-12-15')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        driver_item2 = next(d for d in data2['drivers'] if d['id'] == self.driver.id)
        self.assertTrue(driver_item2['is_available'])

    def test_car_double_booking_prevention_same_dates(self):
        """Verify another customer cannot book the same car for the exact same date slot."""
        customer1 = self.user
        customer2 = User.objects.create_user(username="customer2", password="password123")

        # Customer 1 books self.car for Nov 10 to Nov 15
        Booking.objects.create(
            user=customer1,
            car=self.car,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 15),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=5,
            subtotal=self.car.daily_rate * 5,
            total_price=self.car.daily_rate * 5,
            status="CONFIRMED"
        )

        # Customer 2 attempts to book the same car for the same dates
        self.client.login(username="customer2", password="password123")
        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-11-10',
            'end_date': '2026-11-15',
            'pickup_location': 'Hub',
            'return_location': 'Hub',
            'drive_mode': 'self',
            'customer_license': 'DL-TEST-999',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Time Slot Unavailable")
        self.assertContains(response, "already booked")
        # Customer 2 must NOT have any booking created
        self.assertEqual(Booking.objects.filter(user=customer2).count(), 0)

    def test_car_double_booking_prevention_overlapping_dates(self):
        """Verify another customer cannot book the car for overlapping start, end, or inner slots."""
        customer1 = self.user
        customer2 = User.objects.create_user(username="customer_overlap", password="password123")

        # Booking active from Nov 10 to Nov 20
        Booking.objects.create(
            user=customer1,
            car=self.car,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 20),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=10,
            subtotal=self.car.daily_rate * 10,
            total_price=self.car.daily_rate * 10,
            status="CONFIRMED"
        )

        self.client.login(username="customer_overlap", password="password123")

        # Attempt 1: Overlaps tail (Nov 18 to Nov 25)
        res1 = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-11-18',
            'end_date': '2026-11-25',
            'pickup_location': 'Hub',
            'return_location': 'Hub',
            'drive_mode': 'self',
        }, follow=True)
        self.assertContains(res1, "Time Slot Unavailable")
        self.assertEqual(Booking.objects.filter(user=customer2).count(), 0)

        # Attempt 2: Overlaps head (Nov 05 to Nov 12)
        res2 = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-11-05',
            'end_date': '2026-11-12',
            'pickup_location': 'Hub',
            'return_location': 'Hub',
            'drive_mode': 'self',
        }, follow=True)
        self.assertContains(res2, "Time Slot Unavailable")
        self.assertEqual(Booking.objects.filter(user=customer2).count(), 0)

        # Attempt 3: Completely inside (Nov 12 to Nov 17)
        res3 = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-11-12',
            'end_date': '2026-11-17',
            'pickup_location': 'Hub',
            'return_location': 'Hub',
            'drive_mode': 'self',
        }, follow=True)
        self.assertContains(res3, "Time Slot Unavailable")
        self.assertEqual(Booking.objects.filter(user=customer2).count(), 0)

    def test_car_booking_succeeds_for_distinct_non_overlapping_slots(self):
        """Verify another customer CAN book the same car outside of booked time slots."""
        customer1 = self.user
        customer2 = User.objects.create_user(username="customer_distinct", password="password123")

        # Customer 1 books Nov 10 to Nov 15
        Booking.objects.create(
            user=customer1,
            car=self.car,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 15),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=5,
            subtotal=self.car.daily_rate * 5,
            total_price=self.car.daily_rate * 5,
            status="CONFIRMED"
        )

        # Customer 2 books Nov 18 to Nov 22 (strictly after customer 1)
        self.client.login(username="customer_distinct", password="password123")
        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-11-18',
            'end_date': '2026-11-22',
            'pickup_location': 'Hub',
            'return_location': 'Hub',
            'drive_mode': 'self',
            'customer_license': 'DL-OK-12345',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservation Confirmed")
        self.assertEqual(Booking.objects.filter(user=customer2).count(), 1)

    def test_car_booking_succeeds_after_cancellation(self):
        """When an existing booking is cancelled, that slot becomes available again."""
        customer1 = self.user
        customer2 = User.objects.create_user(username="customer_rebook", password="password123")

        # Customer 1 books Nov 10 to Nov 15
        b1 = Booking.objects.create(
            user=customer1,
            car=self.car,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 15),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=5,
            subtotal=self.car.daily_rate * 5,
            total_price=self.car.daily_rate * 5,
            status="CONFIRMED"
        )

        # Customer 1 cancels the booking
        b1.status = 'CANCELLED'
        b1.save()

        # Customer 2 can now book the exact same slot
        self.client.login(username="customer_rebook", password="password123")
        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-11-10',
            'end_date': '2026-11-15',
            'pickup_location': 'Hub',
            'return_location': 'Hub',
            'drive_mode': 'self',
            'customer_license': 'DL-REBOOK-99',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservation Confirmed")
        self.assertEqual(Booking.objects.filter(user=customer2).count(), 1)

    def test_car_availability_api(self):
        """Test API endpoint /api/car-availability/ for conflicting and open slots."""
        # Create active booking for Dec 1 to Dec 5
        Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 5),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=4,
            subtotal=self.car.daily_rate * 4,
            total_price=self.car.daily_rate * 4,
            status="CONFIRMED"
        )

        # Overlapping query
        resp_conflict = self.client.get(f'/api/car-availability/?car_id={self.car.id}&start_date=2026-12-03&end_date=2026-12-07')
        self.assertEqual(resp_conflict.status_code, 200)
        data_conflict = resp_conflict.json()
        self.assertEqual(data_conflict['status'], 'success')
        self.assertFalse(data_conflict['is_available'])
        self.assertIn("Booked", data_conflict['conflict_info'])
        self.assertGreaterEqual(len(data_conflict['booked_slots']), 1)

        # Free slot query
        resp_free = self.client.get(f'/api/car-availability/?car_id={self.car.id}&start_date=2026-12-10&end_date=2026-12-15')
        self.assertEqual(resp_free.status_code, 200)
        data_free = resp_free.json()
        self.assertEqual(data_free['status'], 'success')
        self.assertTrue(data_free['is_available'])
        self.assertIsNone(data_free['conflict_info'])

    def test_model_clean_validation_prevents_overlap(self):
        """Test that Booking model clean() raises ValidationError on overlap."""
        Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date(2026, 12, 20),
            end_date=date(2026, 12, 25),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Customer 1",
            driver_email="customer1@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=5,
            subtotal=self.car.daily_rate * 5,
            total_price=self.car.daily_rate * 5,
            status="CONFIRMED"
        )

        user2 = User.objects.create_user(username="clean_test_user", password="password123")
        overlapping_booking = Booking(
            user=user2,
            car=self.car,
            start_date=date(2026, 12, 22),
            end_date=date(2026, 12, 28),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Customer 2",
            driver_email="customer2@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=6,
            subtotal=self.car.daily_rate * 6,
            total_price=self.car.daily_rate * 6,
            status="CONFIRMED"
        )

        with self.assertRaises(ValidationError):
            overlapping_booking.save()

    def test_dummy_payment_card_success(self):
        """Test successful dummy credit card payment during booking."""
        self.client.login(username="testdriver", password="password123")
        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-11-20',
            'end_date': '2026-11-24',
            'drive_mode': 'self',
            'payment_method': 'card',
            'card_number': '4532 8900 1234 8890',
            'card_name': 'Test Driver',
            'card_expiry': '12/28',
            'card_cvv': '889',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment of")
        self.assertContains(response, "Successful")
        booking = Booking.objects.get(user=self.user, start_date=date(2026, 11, 20))
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertEqual(booking.payment_status, 'PAID')
        self.assertTrue(booking.transaction_id.startswith('TXN-'))

        # Check Payment record
        payment = Payment.objects.get(booking=booking)
        self.assertEqual(payment.status, 'SUCCESS')
        self.assertEqual(payment.card_last_four, '8890')
        self.assertEqual(payment.card_brand, 'Visa')

    def test_dummy_payment_upi_success(self):
        """Test successful dummy UPI payment during booking."""
        self.client.login(username="testdriver", password="password123")
        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-12-01',
            'end_date': '2026-12-04',
            'drive_mode': 'self',
            'payment_method': 'upi',
            'upi_id': 'testdriver@okhdfcbank',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Successful via Instant UPI")
        booking = Booking.objects.get(user=self.user, start_date=date(2026, 12, 1))
        self.assertEqual(booking.payment_status, 'PAID')
        self.assertEqual(booking.payment_method, 'upi')

        payment = Payment.objects.get(booking=booking)
        self.assertEqual(payment.payment_method, 'upi')
        self.assertEqual(payment.upi_id, 'testdriver@okhdfcbank')

    def test_dummy_payment_decline_simulation_and_retry(self):
        """Test simulated declined payment, redirect to checkout, and subsequent payment retry."""
        self.client.login(username="testdriver", password="password123")

        # 1. Booking with simulated card decline
        response = self.client.post(f'/car/{self.car.id}/book/', {
            'start_date': '2026-12-10',
            'end_date': '2026-12-14',
            'drive_mode': 'self',
            'payment_method': 'card',
            'card_number': '4000 0000 0000 0000', # Trigger decline
            'simulate_payment_action': 'fail',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment Declined")
        booking = Booking.objects.get(user=self.user, start_date=date(2026, 12, 10))
        self.assertEqual(booking.status, 'PENDING')
        self.assertEqual(booking.payment_status, 'FAILED')

        # 2. Visit checkout payment portal
        checkout_page = self.client.get(f'/booking/{booking.booking_ref}/payment/')
        self.assertEqual(checkout_page.status_code, 200)
        self.assertContains(checkout_page, "AutoDrive Secure Payment Gateway")

        # 3. Retry payment with valid card
        retry_resp = self.client.post(f'/booking/{booking.booking_ref}/process-payment/', {
            'payment_method': 'card',
            'card_number': '4532 8900 1234 8890',
            'simulate_payment_action': 'success',
        }, follow=True)

        self.assertEqual(retry_resp.status_code, 200)
        self.assertContains(retry_resp, "Successful via Credit / Debit Card")

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertEqual(booking.payment_status, 'PAID')

    def test_tax_invoice_receipt_view(self):
        """Test tax invoice and payment receipt rendering."""
        self.client.login(username="testdriver", password="password123")
        b = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date(2026, 12, 15),
            end_date=date(2026, 12, 18),
            pickup_time="10:00 AM",
            pickup_location="Hub",
            return_location="Hub",
            driver_name="Test Driver",
            driver_email="test@autodrive.io",
            driver_phone="+91 98765 43210",
            daily_rate_at_booking=self.car.daily_rate,
            num_days=3,
            subtotal=self.car.daily_rate * 3,
            total_price=self.car.daily_rate * 3,
            status="CONFIRMED",
            payment_status="PAID"
        )

        response = self.client.get(f'/booking/{b.booking_ref}/receipt/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TAX INVOICE / RECEIPT")
        self.assertContains(response, b.booking_ref)
        self.assertContains(response, b.transaction_id)
        self.assertContains(response, "PAID & VERIFIED")




