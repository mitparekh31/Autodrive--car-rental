from django.test import TestCase, Client
from django.contrib.auth.models import User
from fleet.models import Category, Car, Booking
from datetime import date, timedelta

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
            daily_rate=299.00,
            horsepower=750,
            zero_to_sixty="2.6s",
            top_speed="162 mph",
            seats=4,
            transmission="Automatic",
            fuel_type="Electric"
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
