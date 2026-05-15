from django.db import models
from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-grid')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='providers')
    title = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    location = models.CharField(max_length=200, blank=True)
    is_available = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='providers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        reviews = self.user.received_reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0

    def total_reviews(self):
        return self.user.received_reviews.count()

    def total_appointments(self):
        return self.user.provider_appointments.count()

    def get_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/images/default-provider.svg'

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.category}'


class AvailabilitySlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]

    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['provider', 'day_of_week', 'start_time']

    def get_day_name(self):
        return dict(self.DAY_CHOICES).get(self.day_of_week, '')

    def __str__(self):
        return f'{self.provider.username} - {self.get_day_name()} {self.start_time}-{self.end_time}'
