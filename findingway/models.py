from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta

# class User(AbstractUser):
#     phone_number = models.CharField(max_length=15, blank=True, null=True)

#     def __str__(self):
#         return self.username
# class Stop(models.Model):
#     ride = models.ForeignKey('Ride', on_delete=models.CASCADE, related_name='stops')
#     location = models.CharField(max_length=255)
#     order = models.IntegerField()  # To maintain stop sequence
    
#     class Meta:
#         ordering = ['order']

#     def __str__(self):
#         return f"Stop {self.order} - {self.location}"
# class Ride(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='rides'
#     )
#     RIDE_TYPES = [
#         ('TRANSFER', 'Transfer'),
#         ('HOURLY', 'Hourly'),
#     ]
    
#     LOCATION_TYPES = [
#         ('SEARCH', 'Search All'),
#         ('ADDRESS', 'Address'),
#         ('AIRPORT', 'Airport'),
#         ('LANDMARK', 'Landmark'),
#     ]
#     num_travelers = models.PositiveIntegerField(default=1)
#     num_kids = models.PositiveIntegerField(default=0)
#     num_bags = models.PositiveIntegerField(default=0)
#     starting_location = models.CharField(max_length=255)
#     ending_location = models.CharField(max_length=255)
#     time = models.DateTimeField(default=timezone.now)
#     duration = models.IntegerField(default=0)  # Duration in minutes
#     distance = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         null=True, 
#         blank=True
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('SCHEDULED', 'Scheduled'),
#             ('CONFIRMED', 'confirmed'),
#             ('COMPLETED', 'Completed'),
#             ('CANCELLED', 'Cancelled')
#         ],
#         default='SCHEDULED'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     price=models.IntegerField
    
#     @property
#     def end_time(self):
#         return self.time + timedelta(minutes=self.duration)

#     @classmethod
#     def get_booked_slots(cls, date):
#         # Get all rides for the given date
#         day_start = datetime.combine(date, datetime.min.time())
#         day_end = datetime.combine(date, datetime.max.time())
        
#         rides = cls.objects.filter(
#             time__date=date,
            
#         )
        
#         booked_slots = []
#         for ride in rides:
#             current_time = ride.time
#             while current_time < ride.end_time:
#                 booked_slots.append(current_time.strftime('%H:%M'))
#                 current_time += timedelta(minutes=15)
                
#         return booked_slots
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

class Stop(models.Model):
    ride = models.ForeignKey('Ride', on_delete=models.CASCADE, related_name='stops')
    location = models.CharField(max_length=255)
    flight_number = models.CharField(max_length=20, blank=True, default='')
    order = models.IntegerField()  # To maintain stop sequence
    location_type = models.CharField(
        max_length=10,
        choices=[
            ('SEARCH', 'Search All'),
            ('ADDRESS', 'Address'),
            ('AIRPORT', 'Airport'),
            ('LANDMARK', 'Landmark'),
        ],
        default='SEARCH'
    )
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ['ride', 'order']

    def __str__(self):
        return f"Stop {self.order} - {self.location}"

class Ride(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides'
    )
    
    RIDE_TYPES = [
        ('TRANSFER', 'Transfer'),
        ('HOURLY', 'Hourly'),
    ]
    ride_type = models.CharField(max_length=10, choices=RIDE_TYPES, default='TRANSFER')
    
    LOCATION_TYPES = [
        ('SEARCH', 'Search All'),
        ('ADDRESS', 'Address'),
        ('AIRPORT', 'Airport'),
        ('LANDMARK', 'Landmark'),
    ]
    
    # Passenger details
    num_travelers = models.PositiveIntegerField(default=1)
    num_kids = models.PositiveIntegerField(default=0)
    num_bags = models.PositiveIntegerField(default=0)
    starting_flight_number = models.CharField(max_length=20, blank=True, default='')
    ending_flight_number = models.CharField(max_length=20, blank=True, default='')
    # Location details
    starting_location = models.CharField(max_length=255)
    starting_location_type = models.CharField(max_length=10, choices=LOCATION_TYPES, default='SEARCH')
    starting_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    starting_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    ending_location = models.CharField(max_length=255)
    ending_location_type = models.CharField(max_length=10, choices=LOCATION_TYPES, default='SEARCH')
    ending_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    ending_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Time details
    time = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(default=0)  # Duration in minutes
    
    # Ride details
    distance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Changed from IntegerField
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('SCHEDULED', 'Scheduled'),
            ('CONFIRMED', 'Confirmed'),  # Fixed capitalization
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='SCHEDULED'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Added for tracking updates

    @property
    def end_time(self):
        return self.time + timedelta(minutes=self.duration)

    @classmethod
    def get_booked_slots(cls, date):
        # Get all rides for the given date
        rides = cls.objects.filter(
            time__date=date,
            status__in=['SCHEDULED', 'CONFIRMED']  # Only check active bookings
        )
        
        booked_slots = []
        for ride in rides:
            current_time = ride.time
            while current_time < ride.end_time:
                booked_slots.append(current_time.strftime('%H:%M'))
                current_time += timedelta(minutes=15)
                
        return booked_slots

    def get_full_route(self):
        """Returns complete route including pickup, stops, and dropoff"""
        stops = list(self.stops.all().order_by('order'))
        return [
            {'type': 'pickup', 'location': self.starting_location, 'lat': self.starting_lat, 'lng': self.starting_lng},
            *[{'type': 'stop', 'location': stop.location, 'lat': stop.lat, 'lng': stop.lng} for stop in stops],
            {'type': 'dropoff', 'location': self.ending_location, 'lat': self.ending_lat, 'lng': self.ending_lng}
        ]

    def __str__(self):
        return f"Ride from {self.starting_location} to {self.ending_location} on {self.time.date()}"

    class Meta:
        ordering = ['-time']