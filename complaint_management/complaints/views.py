from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Complaint
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User,Group
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def dashboard(request):
    return render(request, 'admin/dashboard.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']  # Get the selected role
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on role
            if role == 'user':
                return redirect('/dashboard')
            elif role == 'engineer':
                return redirect('/engineer/complaints/')
            elif role == 'admin':
                return redirect('/engineer/notify/')
            else:
                return render(request, 'login.html', {'error': 'Invalid role selected'})
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')
    
# Signup view
def signup_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        role = request.POST['role']  # Capture the role from the form

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            # Create the user
            user = User.objects.create_user(username=username, password=password, email=email)

            # Assign the user to the appropriate group based on the role
            if role == 'User':
                group, created = Group.objects.get_or_create(name='User')  # Ensure the group exists
                user.groups.add(group)
            elif role == 'Engineer':
                group, created = Group.objects.get_or_create(name='Engineer')  # Ensure the group exists
                user.groups.add(group)
            else:
                messages.error(request, "Invalid role selected.")
                return redirect('signup')

            # Save the user and show success message
            user.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')

    return render(request, 'signup.html')

# Logout view
def logout_user(request):
    logout(request)
    return redirect('login')

# Home views
def user_home(request):
    return render(request, 'user/home.html')

def engineer_home(request):
    return render(request, 'engineer/home.html')

def admin_home(request):
    return render(request, 'admin/home.html')

def check_login_redirect(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='User').exists():
            return redirect('user_home')
        elif request.user.groups.filter(name='Engineer').exists():
            return redirect('engineer_home')
        elif request.user.is_superuser:
            return redirect('admin_home')
    else:
        return redirect('login')



def home(request):
    return render(request, 'base.html')


@login_required
def raise_complaint(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        suburb = request.POST.get('suburb')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        country = request.POST.get('country')
        location = request.POST.get('location', '')  # Optional field
        latitude = request.POST.get('latitude', None)
        longitude = request.POST.get('longitude', None)
        image = request.FILES.get('image')  # Handle uploaded image
        Complaint.objects.create(
            user=request.user,
            title=title,
            description=description,
            suburb=suburb,
            pincode=pincode,
            state=state,
            country=country,
            location=location,
            latitude=latitude,
            longitude=longitude,
            image=image
        )
        
        # Send email notification
        subject = 'Complaint Raised'
        message = 'A new complaint has been raised. Please check the portal for more details.'
        from_email = 'virendersinghrajput63@gmail.com'
        recipient_list = ['mrpromax96@gmail.com']
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        return redirect('view_user_complaints')
    return render(request, 'user/raise_complaint.html')

@login_required
def engineer_complaints(request):
    complaints = Complaint.objects.all()  # Fetch all complaints
    return render(request, 'engineer/complaints.html', {'complaints': complaints})

@login_required
def view_user_complaints(request):
    # Fetch complaints for the logged-in user, excluding completed complaints
    complaints = Complaint.objects.filter(user=request.user).exclude(status='Completed')
    suburb = request.GET.get('suburb','N/A')
    return render(request, 'user/view_complaints.html', {'complaints': complaints,'suburb':suburb})


@login_required
def engineer_view_complaints(request):
    subject = 'Complaint Raised'
    message = 'A new complaint has been raised in your jurisdiction. Please check the portal for more details.'
    from_email = 'virendersinghrajput63@gmail.com'
    recipient_list = [settings.EMAIL_HOST_USER]
    complaints = Complaint.objects.filter(status='Pending')
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
    return render(request, 'engineer/view_complaints.html', {'complaints': complaints})

@login_required
def accept_complaint(request, complaint_id):
    if request.method == "POST":
        complaint = get_object_or_404(Complaint, id=complaint_id)
        complaint.status = "Accepted"
        complaint.assigned_engineer = request.user  # Assigning the current user as the engineer
        complaint.save()
        return redirect('user_complaints')

@login_required
def notify_user(request):
    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")  # Fetch from POST data
        complaint = get_object_or_404(Complaint, id=complaint_id)

        # Update complaint status
        complaint.status = "Resolved"
        complaint.save()

        # Send email notification
        subject = 'Complaint Resolved'
        message = f'Your complaint "{complaint.title}" has been resolved. Thank you for your patience.'
        from_email = 'mrpromax96@gmail.com'
        recipient_list = [complaint.user.email]  # Ensure user model has an email field
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        # Redirect to the same page to see updated complaints
        return redirect('notify_user')

    # Fetch all complaints with status="Accepted"
    complaints = Complaint.objects.filter(status="Accepted")
    return render(request, 'engineer/notify.html', {'complaints': complaints})

@login_required
def engineer_dashboard(request):
    # Complaints not yet assigned
    unassigned_complaints = Complaint.objects.filter(engineer__isnull=True).order_by('-id')
    # Complaints assigned to the current engineer
    assigned_complaints = Complaint.objects.filter(engineer=request.user).order_by('-id')
    return render(request, 'engineer/dashboard.html', {
        'unassigned_complaints': unassigned_complaints,
        'assigned_complaints': assigned_complaints,
    })


@login_required
def assign_complaint(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    complaint.engineer = request.user
    complaint.status = 'In Progress'
    complaint.save()
    return redirect('engineer_dashboard')


@login_required
def update_complaint_status(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id, engineer=request.user)
    if request.method == "POST":
        new_status = request.POST['status']
        complaint.status = new_status
        complaint.save()
        return redirect('engineer_dashboard')
    return render(request, 'engineer/update_status.html', {'complaint': complaint})