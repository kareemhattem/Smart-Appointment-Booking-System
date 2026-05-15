import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import User
from providers.models import Category, ProviderProfile, AvailabilitySlot
from appointments.models import Appointment
from reviews.models import Review
from notifications.models import Notification
from datetime import date, time, timedelta


def run():
    print("Seeding database...")

    # Categories
    categories_data = [
        ('General Medicine', 'bi-heart-pulse', 'Primary care and general health consultations'),
        ('Dentistry', 'bi-emoji-smile', 'Dental care and oral health'),
        ('Dermatology', 'bi-person', 'Skin, hair, and nail conditions'),
        ('Cardiology', 'bi-heart', 'Heart and cardiovascular health'),
        ('Physiotherapy', 'bi-activity', 'Physical rehabilitation and therapy'),
        ('Psychology', 'bi-brain', 'Mental health and counseling'),
    ]

    categories = {}
    for name, icon, desc in categories_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
        categories[name] = cat
        print(f"  Category: {name}")

    # Admin user
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create(
            username='admin',
            email='admin@smartbook.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True,
            password=make_password('Admin@1234'),
        )
        print(f"  Admin: {admin.username} / Admin@1234")

    # Providers
    providers_data = [
        ('dr_sarah', 'Sarah', 'Johnson', 'sarah@smartbook.com', 'General Medicine', 'Dr.', 'Family Medicine Specialist', 12, 80.00, 'New York'),
        ('dr_mike', 'Michael', 'Chen', 'mike@smartbook.com', 'Cardiology', 'Dr.', 'Interventional Cardiologist', 15, 120.00, 'Los Angeles'),
        ('dr_emma', 'Emma', 'Williams', 'emma@smartbook.com', 'Dermatology', 'Dr.', 'Cosmetic Dermatologist', 8, 95.00, 'Chicago'),
        ('dr_james', 'James', 'Brown', 'james@smartbook.com', 'Dentistry', 'Dr.', 'Orthodontist & General Dentist', 10, 75.00, 'Houston'),
        ('pt_lisa', 'Lisa', 'Davis', 'lisa@smartbook.com', 'Physiotherapy', 'PT.', 'Sports Rehabilitation Specialist', 6, 65.00, 'Phoenix'),
        ('dr_alex', 'Alex', 'Martinez', 'alex@smartbook.com', 'Psychology', 'Dr.', 'Clinical Psychologist', 9, 110.00, 'San Diego'),
    ]

    providers = []
    for username, first, last, email, cat_name, title, spec, exp, fee, loc in providers_data:
        if not User.objects.filter(username=username).exists():
            p = User.objects.create(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                role='provider',
                password=make_password('Provider@1234'),
            )
            ProviderProfile.objects.create(
                user=p,
                category=categories[cat_name],
                title=title,
                specialization=spec,
                experience_years=exp,
                consultation_fee=fee,
                location=loc,
                is_available=True,
            )
            # Add availability slots
            for day in [0, 1, 2, 3, 4]:  # Mon-Fri
                AvailabilitySlot.objects.get_or_create(
                    provider=p,
                    day_of_week=day,
                    start_time=time(9, 0),
                    defaults={'end_time': time(17, 0), 'is_active': True},
                )
            providers.append(p)
            print(f"  Provider: {username} / Provider@1234")

    # Regular users
    users_data = [
        ('john_doe', 'John', 'Doe', 'john@example.com'),
        ('jane_smith', 'Jane', 'Smith', 'jane@example.com'),
        ('bob_wilson', 'Bob', 'Wilson', 'bob@example.com'),
    ]

    regular_users = []
    for username, first, last, email in users_data:
        if not User.objects.filter(username=username).exists():
            u = User.objects.create(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                role='user',
                password=make_password('User@1234'),
            )
            regular_users.append(u)
            print(f"  User: {username} / User@1234")

    # Sample appointments
    if Appointment.objects.count() == 0 and providers and regular_users:
        today = date.today()
        appt_data = [
            (regular_users[0], providers[0], today + timedelta(days=3), time(10, 0), time(10, 30), 'confirmed', 'Annual checkup'),
            (regular_users[0], providers[1], today + timedelta(days=7), time(14, 0), time(14, 45), 'pending', 'Heart palpitations'),
            (regular_users[1], providers[2], today - timedelta(days=5), time(11, 0), time(11, 30), 'completed', 'Skin rash'),
            (regular_users[1], providers[3], today + timedelta(days=2), time(9, 0), time(9, 45), 'confirmed', 'Tooth cleaning'),
            (regular_users[2], providers[4], today - timedelta(days=10), time(15, 0), time(16, 0), 'completed', 'Knee rehabilitation'),
        ]

        for patient, provider, appt_date, start, end, status, reason in appt_data:
            appt = Appointment.objects.create(
                patient=patient,
                provider=provider,
                appointment_date=appt_date,
                start_time=start,
                end_time=end,
                status=status,
                reason=reason,
            )
            print(f"  Appointment: {patient.username} → {provider.username} ({status})")

            # Add reviews for completed appointments
            if status == 'completed' and not hasattr(appt, 'review'):
                Review.objects.create(
                    appointment=appt,
                    reviewer=patient,
                    provider=provider,
                    rating=5,
                    comment='Excellent service, very professional and thorough.',
                )
                print(f"    Review added for appointment #{appt.pk}")

    print("\nSeed complete.")
    print("\nLogin credentials:")
    print("  Admin:    admin / Admin@1234")
    print("  Provider: dr_sarah / Provider@1234")
    print("  User:     john_doe / User@1234")


if __name__ == '__main__':
    run()
