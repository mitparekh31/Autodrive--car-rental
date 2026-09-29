from django.test import TestCase, Client
from django.contrib.auth.models import User
from fleet.models import Category, Car, Booking, Driver
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




