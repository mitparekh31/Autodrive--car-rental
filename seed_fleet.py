import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from fleet.models import Category, Car, Booking, Review
from django.contrib.auth.models import User
from datetime import date, timedelta

def seed_database():
    print("[*] Seeding AutoDrive Fleet Data...")

    # Create default demo user matching screenshot "john_driver"
    user, created = User.objects.get_or_create(username="john_driver", email="john@autodrive.io")
    if created:
        user.set_password("password123")
        user.first_name = "John"
        user.last_name = "Driver"
        user.save()
        print("  - Created user 'john_driver' (Password: password123)")

    # Create admin staff user
    admin, admin_created = User.objects.get_or_create(username="admin", email="admin@autodrive.io", is_staff=True, is_superuser=True)
    if admin_created:
        admin.set_password("admin123")
        admin.save()
        print("  - Created admin user 'admin' (Password: admin123)")


    # Categories matching screenshot description
    categories_data = [
        {"name": "Electric Supercars", "icon": "fa-bolt", "description": "High voltage acceleration, zero emissions supercar fleet."},
        {"name": "Luxury Sedans", "icon": "fa-car-side", "description": "Ultra-comfort executive sedans for VIP transfers."},
        {"name": "Solo Track Bikes", "icon": "fa-motorcycle", "description": "Lightweight high-revving track bikes for adrenaline seekers."},
        {"name": "VIP 8-Seater Vans", "icon": "fa-van-shuttle", "description": "Chauffeur-driven luxury vans with reclining leather suites."},
        {"name": "Luxury SUVs", "icon": "fa-truck-monster", "description": "All-terrain luxury powerhouses."},
    ]

    cats = {}
    for cat_data in categories_data:
        c, _ = Category.objects.get_or_create(name=cat_data["name"], defaults=cat_data)
        cats[cat_data["name"]] = c
    print("  - Created Fleet Categories")


    # Fleet Vehicles Data (INR Pricing)
    cars_data = [
        {
            "name": "Porsche Taycan Turbo S",
            "make": "Porsche",
            "model": "Taycan Turbo S",
            "year": 2025,
            "category": cats["Electric Supercars"],
            "daily_rate": 8999.00,
            "horsepower": 750,
            "zero_to_sixty": "2.6s",
            "top_speed": "162 mph",
            "seats": 4,
            "transmission": "Automatic",
            "fuel_type": "Electric",
            "range_or_economy": "280 mi range",
            "luggage_capacity": "3 Bags",
            "is_available": True,
            "is_featured": True,
            "image_url": "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?auto=format&fit=crop&w=1200&q=80",
            "tagline": "100% Real-Time Availability Guarantee",
            "features": "Launch Control, Porsche Active Suspension, Carbon Ceramic Brakes, Burmester 3D Surround, Glass Roof"
        },
        {
            "name": "Tesla Roadster Performance",
            "make": "Tesla",
            "model": "Roadster",
            "year": 2025,
            "category": cats["Electric Supercars"],
            "daily_rate": 9999.00,
            "horsepower": 1020,
            "zero_to_sixty": "1.9s",
            "top_speed": "250 mph",
            "seats": 4,
            "transmission": "Direct-Drive",
            "fuel_type": "Electric",
            "range_or_economy": "620 mi range",
            "luggage_capacity": "2 Bags",
            "is_available": True,
            "is_featured": True,
            "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=1200&q=80",
            "tagline": "Tri-Motor All-Wheel Drive Thrill",
            "features": "Full Self-Driving Autopilot, Removable Glass Roof, Yoke Steering Wheel, 0-100mph in 4.2s"
        },
        {
            "name": "Mercedes-Maybach S 680",
            "make": "Mercedes-Benz",
            "model": "Maybach S 680",
            "year": 2025,
            "category": cats["Luxury Sedans"],
            "daily_rate": 11999.00,
            "horsepower": 621,
            "zero_to_sixty": "4.4s",
            "top_speed": "155 mph",
            "seats": 5,
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "range_or_economy": "18 MPG",
            "luggage_capacity": "4 Suitcases",
            "is_available": True,
            "is_featured": True,
            "image_url": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=80",
            "tagline": "Pinnacle of Executive Comfort & Prestige",
            "features": "Reclining Executive Seats, Calf Massage, Refrigerated Compartment, Champagne Flutes, Air Suspension"
        },
        {
            "name": "Ducati Panigale V4 S",
            "make": "Ducati",
            "model": "Panigale V4 S",
            "year": 2025,
            "category": cats["Solo Track Bikes"],
            "daily_rate": 4999.00,
            "horsepower": 215,
            "zero_to_sixty": "2.8s",
            "top_speed": "186 mph",
            "seats": 1,
            "transmission": "Manual",
            "fuel_type": "Gasoline",
            "range_or_economy": "38 MPG",
            "luggage_capacity": "Track Helmet Bag",
            "is_available": True,
            "is_featured": True,
            "image_url": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1200&q=80",
            "tagline": "Pure Moto GP Racing DNA",
            "features": "Ohlins Electronic Suspension, Cornering ABS EVO, Quickshifter Up/Down, Marchesini Forged Wheels"
        },
        {
            "name": "Mercedes Sprinter VIP Lounge",
            "make": "Mercedes-Benz",
            "model": "Sprinter VIP",
            "year": 2025,
            "category": cats["VIP 8-Seater Vans"],
            "daily_rate": 12999.00,
            "horsepower": 211,
            "zero_to_sixty": "8.5s",
            "top_speed": "120 mph",
            "seats": 8,
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "range_or_economy": "22 MPG",
            "luggage_capacity": "8 Large Luggage",
            "is_available": True,
            "is_featured": True,
            "image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=1200&q=80",
            "tagline": "Mobile Executive Suite for Corporate Teams",
            "features": "4K Smart TV, Onboard Wi-Fi, Nappa Leather Captain Chairs, Bar Console, Privacy Partition"
        },
        {
            "name": "Cadillac Escalade ESV V-Series",
            "make": "Cadillac",
            "model": "Escalade V-Series",
            "year": 2025,
            "category": cats["Luxury SUVs"],
            "daily_rate": 9499.00,
            "horsepower": 682,
            "zero_to_sixty": "4.3s",
            "top_speed": "140 mph",
            "seats": 7,
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "range_or_economy": "16 MPG",
            "luggage_capacity": "6 Large Bags",
            "is_available": True,
            "is_featured": True,
            "image_url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=80",
            "tagline": "Supercharged V8 Dominance & Luxury",
            "features": "38-inch Curved OLED Display, AKG Studio Reference 36-Speaker Sound, Super Cruise Hands-Free Driving"
        },
        {
            "name": "Ferrari SF90 Stradale",
            "make": "Ferrari",
            "model": "SF90 Stradale",
            "year": 2025,
            "category": cats["Electric Supercars"],
            "daily_rate": 15999.00,
            "horsepower": 986,
            "zero_to_sixty": "2.5s",
            "top_speed": "211 mph",
            "seats": 2,
            "transmission": "Automatic",
            "fuel_type": "Hybrid",
            "range_or_economy": "16 mi EV / V8 Twin-Turbo",
            "luggage_capacity": "1 Cabin Bag",
            "is_available": True,
            "is_featured": False,
            "image_url": "https://images.unsplash.com/photo-1583121274602-3e2820c69888?auto=format&fit=crop&w=1200&q=80",
            "tagline": "Ferrari Hybrid Hypercar Engineering",
            "features": "4WD eManettino Drive Modes, Assetto Fiorano Racing Package, Active Aerodynamics"
        },
        {
            "name": "Audi RS e-tron GT Carbon",
            "make": "Audi",
            "model": "RS e-tron GT",
            "year": 2025,
            "category": cats["Electric Supercars"],
            "daily_rate": 7999.00,
            "horsepower": 637,
            "zero_to_sixty": "3.1s",
            "top_speed": "155 mph",
            "seats": 5,
            "transmission": "Automatic",
            "fuel_type": "Electric",
            "range_or_economy": "240 mi range",
            "luggage_capacity": "3 Bags",
            "is_available": True,
            "is_featured": False,
            "image_url": "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=80",
            "tagline": "Electrified Grand Touring Perfection",
            "features": "Quattro All-Wheel Drive, Bang & Olufsen Sound System, Matrix LED Headlights with Laser Light"
        }
    ]

    for car_info in cars_data:
        car_obj, created_car = Car.objects.get_or_create(name=car_info["name"], defaults=car_info)
        if not created_car:
            car_obj.daily_rate = car_info["daily_rate"]
            car_obj.save()
            print(f"  - Updated car rate: {car_obj.name} -> INR {car_obj.daily_rate}")
        else:
            print(f"  - Added car: {car_obj.name}")

    from decimal import Decimal
    taycan = Car.objects.filter(name__icontains="Taycan").first()
    if taycan:
        sub = taycan.daily_rate * 5
        tot = sub + Decimal('2000.00')
        booking = Booking.objects.filter(user=user, car=taycan).first()
        if not booking:
            booking = Booking.objects.create(
                user=user,
                car=taycan,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=5),
                pickup_time="10:00 AM",
                pickup_location="Downtown Airport Executive Hub",
                return_location="Downtown Airport Executive Hub",
                driver_name="John Driver",
                driver_email="john@autodrive.io",
                driver_phone="+91 98765 43210",
                daily_rate_at_booking=taycan.daily_rate,
                num_days=5,
                subtotal=sub,
                discount_percent=0,
                discount_amount=Decimal('0.00'),
                insurance_opt=True,
                chauffeur_opt=False,
                gps_opt=True,
                total_price=tot,
                status="CONFIRMED"
            )
            print(f"  - Created sample booking #{booking.booking_ref} for {user.username}")
        else:
            print(f"  - Sample booking already exists: #{booking.booking_ref} for {user.username}")

    print("[+] AutoDrive Fleet Seeding Complete!")


if __name__ == '__main__':
    seed_database()
