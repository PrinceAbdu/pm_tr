from datetime import datetime as dt, timedelta, timezone
from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Ride
from django.contrib.auth import login,authenticate
from django.contrib.auth import logout
from findingway.models import User  
# Create your views here.

def home(request):
    return render(request,"index.html")
def signin_signup(request):
    print("we are redirectinoggggg")
    return render(request,"signup.html")
def logout_view(request):
    """
    Logs out the user and redirects them to the homepage or login page.
    """
    logout(request)
    # messages.success(request, "You have successfully logged out.")
    return redirect('home') 
# def signup(request):
#     return render(request,"signup.html")
# def signin(request):
#     print("pringintint")
#     return render(request,"signin.html")
def signout(request):
    """
    Logs out the user and redirects them to the homepage or login page.
    """
    logout(request)
    # messages.success(request, "You have successfully logged out.")
    return redirect('home') 
def signup(request):
    """Handle user registration"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Basic validation
        if password1 != password2:
            return render(request, 'signup.html', {
                'signup_error': 'Passwords do not match'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {
                'signup_error': 'Username already exists'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {
                'signup_error': 'Email already exists'
            })

        # Create new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                phone_number=phone_number
            )
            if 'pending_ride_data' in request.session:
               data = request.session.pop('pending_ride_data')
               create_ride(request, data)
            login(request, user)
            return redirect('profile')  
        # Redirect to profile page after successful signup
        except Exception as e:
            return render(request, 'signup.html', {
                'signup_error': 'Error creating account. Please try again.'
            })

    return redirect('signin_signup')

@login_required
def profile(request):
    """
    View for user profile page
    Shows user information and ride history
    Requires user to be logged in
    """
    # Get the user's rides ordered by most recent first
    rides = Ride.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate ride statistics
    total_rides = rides.count()
    completed_rides = rides.filter(status='COMPLETED').count()
    scheduled_rides = rides.filter(status='SCHEDULED').count()
    
    context = {
        'user': request.user,
        'rides': rides,
        'total_rides': total_rides,
        'completed_rides': completed_rides,
        'scheduled_rides': scheduled_rides,
    }
    
    return render(request, 'profile.html', context)


def signin(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if 'pending_ride_data' in request.session:
               data = request.session.pop('pending_ride_data')
               create_ride(request, data)
            
        
            return redirect('profile')
        else:
            return render(request, 'signup.html', {
                'signin_error': 'Invalid username or password'
            })

    return redirect('signin_signup')

def store_ride_in_session(request, ride_data):
    """Store ride details in session for later booking"""
    # Parse duration into minutes
    duration_text = ride_data.get('duration', '')  # "X hours Y mins"
    duration_minutes = 0
    if duration_text:
        duration_parts = duration_text.split()
        for i in range(0, len(duration_parts), 2):
            value = int(duration_parts[i])
            unit = duration_parts[i + 1].lower()
            if 'hour' in unit:
                duration_minutes += value * 60
            elif 'min' in unit:
                duration_minutes += value

    request.session['pending_ride'] = {
        'starting_location': ride_data.get('from'),
        'ending_location': ride_data.get('to'),
        'time': f"{ride_data.get('date')} {ride_data.get('time')}",
        'distance': ride_data.get('distance'),
        'duration': duration_minutes  # Store the parsed duration
    }
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def send_contact_email(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        subject_type = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Construct the email subject and message
        email_subject = f"Contact Form: {subject_type}"
        email_message = f"""
        You have received a new message from the website contact form:
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {subject_type}
        
        Message:
        {message}
        """
        
        # Send the email
        try:
            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,  # From email
                ['palmvalleytransportation@gmail.com'],  # To email
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            print(str(e))  # Log the error
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
# @login_required
# def create_ride(request):
#     """Handle ride creation with duration"""
#     if request.method == 'POST':
#         try:
#             # Get ride details from POST data
#             duration_text = request.POST.get('duration', '')  # "X hours Y mins"
#             # Parse duration into minutes
#             duration_parts = duration_text.split()
#             duration_minutes = 0
#             for i in range(0, len(duration_parts), 2):
#                 value = int(duration_parts[i])
#                 unit = duration_parts[i + 1].lower()
#                 if 'hour' in unit:
#                     duration_minutes += value * 60
#                 elif 'min' in unit:
#                     duration_minutes += value

#             ride_data = {
#                 'starting_location': request.POST.get('from'),
#                 'ending_location': request.POST.get('to'),
#                 'time': dt.strptime(
#                     f"{request.POST.get('date')} {request.POST.get('time')}", 
#                     '%Y-%m-%d %H:%M'
#                 ),
#                 'distance': float(request.POST.get('distance', 0)),
#                 'duration': duration_minutes
#             }
            
#             # Create new ride
#             ride = Ride.objects.create(
#                 user=request.user,
#                 **ride_data
#             )
            
#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Ride booked successfully',
#                 'redirect_url': reverse('profile')
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=400)
    
#     return JsonResponse({
#         'status': 'error',
#         'message': 'Invalid request method'
#     }, status=400)
def book_ride(request):
    """Handle ride booking process"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Store ride details in session
            store_ride_in_session(request, request.POST)
            return JsonResponse({
                'status': 'redirect',
                'url': reverse('signin_signup')
            })
        
        # User is authenticated, create the ride
        create_ride(request)
        
    # If not POST, redirect to calculator section
    return render(request, 'index.html', {'scroll_to_section': 'calculatorSection'})
# def signin_admin(request):
# path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')
# @require_http_methods(["GET"])
# @ensure_csrf_cookie

# def get_available_slots(request):
#     """Return available time slots for a given date"""
#     if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse({'error': 'Invalid request'}, status=400)

#     date_str = request.GET.get('date')
#     if not date_str:
#         return JsonResponse({'error': 'Date is required'}, status=400)
    
#     try:
#         # Convert the input date string to a timezone-aware datetime
#         selected_date = timezone.make_aware(dt.strptime(date_str, '%Y-%m-%d'))
        
#         # Get current time with proper timezone
#         now = timezone.now()
#         today = now.date()
#         max_date = today + timedelta(days=7)
        
#         if selected_date.date() < today:
#             return JsonResponse({'error': 'Cannot book rides for past dates'}, status=400)
#         if selected_date.date() > max_date:
#             return JsonResponse({'error': 'Cannot book rides more than 7 days in advance'}, status=400)
            
#         # Get all booked slots for the date
#         booked_slots = Ride.get_booked_slots(selected_date.date())
        
#         # Generate all possible slots (every 15 minutes)
#         all_slots = []
#         current_time = timezone.make_aware(dt.combine(selected_date.date(), dt.min.time().replace(hour=8)))
#         end_time = timezone.make_aware(dt.combine(selected_date.date(), dt.min.time().replace(hour=23)))
        
#         # If it's today, only show future slots
#         if selected_date.date() == today:
#             if now.time() > current_time.time():
#                 # Round up to next 15-minute slot
#                 minutes = (now.minute // 15 + 1) * 15
#                 current_time = timezone.make_aware(dt.combine(
#                     today,
#                     dt.min.time().replace(hour=now.hour, minute=minutes)
#                 ))
#                 if minutes >= 60:
#                     current_time += timedelta(hours=1)
#                     current_time = current_time.replace(minute=0)
        
#         while current_time <= end_time:
#             slot = current_time.strftime('%H:%M')
#             if slot not in booked_slots:
#                 all_slots.append(slot)
#             current_time += timedelta(minutes=15)
        
#         return JsonResponse({'available_slots': all_slots})
            
#     except ValueError:
#         return JsonResponse({'error': 'Invalid date format'}, status=400)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
# In views.py
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import JsonResponse
from .models import Ride
def bookridepage(request):
   return render(request, "bookaride.html")

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
import json
from .models import Ride, Stop
from decimal import Decimal

# @login_required
# @csrf_protect
def create_ride(request, data):
   try:
       ride = Ride.objects.create(
           user=request.user,
           ride_type=data.get('ride_type', 'TRANSFER'),
           num_travelers=data.get('num_travelers', 1),
           num_kids=data.get('num_kids', 0),
           num_bags=data.get('num_bags', 0),
           starting_location=data['starting_location'],
           starting_location_type=data.get('starting_location_type', 'SEARCH'),
           starting_lat=data.get('starting_lat'),
           starting_lng=data.get('starting_lng'),
           ending_location=data.get('ending_location', ''),
           ending_location_type=data.get('ending_location_type', 'SEARCH'),
           ending_lat=data.get('ending_lat', ''),
           ending_lng=data.get('ending_lng', ''),
           time=data['time'],
           status='SCHEDULED',
           distance=Decimal(str(data.get('distance', 0))),
           duration=data.get('duration', 0)
       )
       
       for stop_data in data.get('stops', []):
           Stop.objects.create(
               ride=ride,
               location=stop_data['location'],
               order=stop_data['order'],
               location_type=stop_data.get('location_type', 'SEARCH'),
               lat=stop_data.get('lat'),
               lng=stop_data.get('lng')
           )

       base_price = 50
       distance_rate = 2
       price = base_price + (Decimal(str(data.get('distance', 0))) * distance_rate)
       ride.price = price
       print("??????????????????????hereeeeee??????????")
       ride.save()

       return JsonResponse({
           'success': True,
           'ride_id': ride.id,
           'price': float(price)
       })

   except Exception as e:
       return JsonResponse({
           'success': False, 
           'error': str(e)
       }, status=500)
@require_http_methods(["POST"])
def book_a_ride(request):
    try:
        # Parse the JSON data from request body
        data = json.loads(request.body)
        print("before the if statement????????")
        if not request.user.is_authenticated:
            print("we are inside authenticated")
            request.session['pending_ride_data'] = data
            print("about to reutnr jason")
            return JsonResponse({
                'success': False,
                'redirect': True,
                'url': '/signin_signup'
            })

        # Create ride from session data if exists
        ride_data = request.session.pop('pending_ride_data', None)
        print("Parsed data:", data)
        if ride_data:
            data = ride_data
        print(f"???????????????????????????????????????{data['time']}")
        
        # Create the ride instance
        ride = Ride.objects.create(
            user=request.user,
            ride_type=data.get('ride_type', 'TRANSFER'),
            num_travelers=data.get('num_travelers', 1),
            num_kids=data.get('num_kids', 0),
            num_bags=data.get('num_bags', 0),
            starting_location=data['starting_location'],
            starting_location_type=data.get('starting_location_type', 'SEARCH'),
            starting_lat=data.get('starting_lat'),
            starting_lng=data.get('starting_lng'),
            starting_flight_number=data.get('starting_flight_number', ''),
            ending_location=data['ending_location'],
            ending_location_type=data.get('ending_location_type', 'SEARCH'),
            ending_lat=data.get('ending_lat'),
            ending_lng=data.get('ending_lng'),
            ending_flight_number=data.get('ending_flight_number', ''),
            time=data['time'],
            status='SCHEDULED',
            # Save distance and duration
            distance=Decimal(str(data.get('distance', 0))),
            duration=data.get('duration', 0)  # Duration in minutes
        )
        
        # Create stops if any
        stops_data = data.get('stops', [])
        for stop_data in stops_data:
            Stop.objects.create(
                ride=ride,
                location=stop_data['location'],
                order=stop_data['order'],
                location_type=stop_data.get('location_type', 'SEARCH'),
                lat=stop_data.get('lat'),
                lng=stop_data.get('lng'),
                flight_number=stop_data.get('flight_number', '')
            )
        
        # Calculate preliminary price based on distance and duration
        # You can modify this pricing logic according to your needs
        base_price = 50  # Base price in your currency
        distance_rate = 2  # Price per km
        price = base_price + (Decimal(str(data.get('distance', 0))) * distance_rate)
        
        # Update ride with calculated price
        ride.price = price
        print("???????????here ??????????")
        ride.save()
        
        # Return success response
        return JsonResponse({
            'success': True,
            'ride_id': ride.id,
            'url': '/profile',
            'price': float(price)  # Convert Decimal to float for JSON serialization
        })
        
    except KeyError as e:
        return JsonResponse({
            'success': False,
            'error': f'Missing required field: {str(e)}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
@staff_member_required
def admin_dashboard(request):
    # Get unique dates with rides
    dates_with_rides = Ride.objects.dates('time', 'day', order='DESC')
    
    # Get rides for selected date
    selected_date = request.GET.get('date')
    rides = []
    
    if selected_date:
        rides = Ride.objects.filter(
            time__date=selected_date,
            status='SCHEDULED'
        ).order_by('time')
    
    return render(request, 'admin_dashboard.html', {
        'dates': dates_with_rides,
        'rides': rides,
        'selected_date': selected_date
    })

@staff_member_required
def update_ride_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
        
    ride_id = request.POST.get('ride_id')
    status = request.POST.get('status')
    print("8888888888888888888888888")
    print(status)
    print("8888888888888888888888888")

        
    try:
        ride = Ride.objects.get(id=ride_id)
        ride.status = status
        ride.save()
        return JsonResponse({'success': True})
    except Ride.DoesNotExist:
        return JsonResponse({'error': 'Ride not found'}, status=404)
def get_available_slots(request):
    """Return available time slots for a given date and check for overlaps"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    print("here we are")
    date_str = request.GET.get('date')
    duration_str = request.GET.get('duration')  # Expected format: "X hours Y mins"
    selected_time = request.GET.get('selected_time')  # HH:MM format
    print("here we are2")
    
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)
    
    try:
        # Convert the input date string to a timezone-aware datetime
        try:
            selected_date = timezone.make_aware(dt.strptime(date_str, '%Y-%m-%d'))
        except ValueError as e:
            # Handle invalid date string
            print(f"Invalid date format: {e}")
        except Exception as e:
            # Handle other potential errors
            print(f"Error processing date: {e}")
        print("here we are3")
        
        # Get current time with proper timezone
        now = timezone.now()
        today = now.date()
        max_date = today + timedelta(days=7)
        
        if selected_date.date() < today:
            return JsonResponse({'error': 'Cannot book rides for past dates'}, status=400)
        if selected_date.date() > max_date:
            return JsonResponse({'error': 'Cannot book rides more than 7 days in advance'}, status=400)
        print("here we are4")
        
        # If checking for specific time slot overlap
        if duration_str and selected_time:
            # Parse duration into minutes
            duration_parts = duration_str.split()
            duration_minutes = 0
            for i in range(0, len(duration_parts), 2):
                value = int(duration_parts[i])
                unit = duration_parts[i + 1].lower()
                if 'hour' in unit:
                    duration_minutes += value * 60
                elif 'min' in unit:
                    duration_minutes += value
            
            # Convert selected time to datetime
            time_obj = dt.strptime(selected_time, '%H:%M').time()
            start_datetime = timezone.make_aware(dt.combine(selected_date.date(), time_obj))
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Check for overlaps
            existing_rides = Ride.objects.filter(
                time__date=selected_date.date(),
                status='SCHEDULED'
            )
            
            for ride in existing_rides:
                ride_end_time = ride.time + timedelta(minutes=ride.duration)
                if (start_datetime < ride_end_time and 
                    end_datetime > ride.time):
                    return JsonResponse({
                        'overlap': True,
                        'busy_start': ride.time.strftime('%H:%M'),
                        'busy_end': ride_end_time.strftime('%H:%M'),
                        'requested_start': start_datetime.strftime('%H:%M'),
                        'requested_end': end_datetime.strftime('%H:%M')
                    })
            
            return JsonResponse({'overlap': False})
            
        # Get all booked slots for the date
        booked_slots = Ride.get_booked_slots(selected_date.date())
        
        # Generate all possible slots (every 15 minutes)
        all_slots = []
        current_time = timezone.make_aware(dt.combine(selected_date.date(), dt.min.time().replace(hour=8)))
        end_time = timezone.make_aware(dt.combine(selected_date.date(), dt.min.time().replace(hour=23)))
        
        # If it's today, only show future slots
        if selected_date.date() == today:
            if now.time() > current_time.time():
                minutes = (now.minute // 15 + 1) * 15
                current_time = timezone.make_aware(dt.combine(
                    today,
                    dt.min.time().replace(hour=now.hour, minute=minutes)
                ))
                if minutes >= 60:
                    current_time += timedelta(hours=1)
                    current_time = current_time.replace(minute=0)
        
        while current_time <= end_time:
            slot = current_time.strftime('%H:%M')
            if slot not in booked_slots:
                all_slots.append(slot)
            current_time += timedelta(minutes=15)
        
        return JsonResponse({'available_slots': all_slots})
            
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from datetime import datetime, timedelta
# from .models import Ride

# @csrf_exempt
# def get_available_slots(request):
#     """Return available time slots for a given date"""
#     print("Entering get_available_slots view")  # Debug print
#     try:
#         date_str = request.GET.get('date')
#         print(f"Received date: {date_str}")  # Debug print
        
#         if not date_str:
#             return JsonResponse({'error': 'Date is required'}, status=400)
        
#         # Parse date
#         selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#         print(f"Parsed date: {selected_date}")  # Debug print

#         # Get existing bookings for this date
#         try:
#             booked_slots = set()  # Use a set for faster lookups
#             rides = Ride.objects.filter(
#                 time__date=selected_date,
#                 status='SCHEDULED'
#             )
            
#             # Calculate booked time slots
#             for ride in rides:
#                 current_time = ride.time
#                 end_time = current_time + timedelta(minutes=ride.duration or 0)
#                 while current_time < end_time:
#                     booked_slots.add(current_time.strftime('%H:%M'))
#                     current_time += timedelta(minutes=15)
                    
#         except Exception as e:
#             print(f"Error getting booked slots: {str(e)}")  # Debug print
#             booked_slots = set()  # Continue with empty set if there's an error
        
#         # Generate all possible slots
#         available_slots = []
#         current_time = datetime.combine(selected_date, datetime.min.time().replace(hour=8))  # Start at 8 AM
#         end_time = datetime.combine(selected_date, datetime.min.time().replace(hour=20))     # End at 8 PM
        
#         while current_time <= end_time:
#             time_str = current_time.strftime('%H:%M')
#             if time_str not in booked_slots:
#                 available_slots.append(time_str)
#             current_time += timedelta(minutes=15)
        
#         print(f"Generated {len(available_slots)} available slots")  # Debug print
        
#         return JsonResponse({
#             'status': 'success',
#             'available_slots': available_slots
#         })
        
#     except ValueError as e:
#         print(f"ValueError: {str(e)}")  # Debug print
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Invalid date format'
#         }, status=400)
        
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")  # Debug print
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=500)

# views.py
# @staff_member_required
@staff_member_required
def update_ride_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
        
    ride_id = request.POST.get('ride_id')
    status = request.POST.get('status')
    
    # if status not in ['COMPLETED', 'CANCELLED']:
    #     return JsonResponse({'error': 'Invalid status'}, status=400)
        
    try:
        ride = Ride.objects.get(id=ride_id)
        ride.status = status
        ride.save()
        return JsonResponse({
            'success': True,
            'status': status,
            'ride_id': ride_id
        })
    except Ride.DoesNotExist:
        return JsonResponse({'error': 'Ride not found'}, status=404)
