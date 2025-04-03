from django.shortcuts import render, redirect
import secrets
import string
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.contrib.auth import authenticate, login, logout
from .models import Client, TermsAndPolicy, Staff, FAQ
from .forms import AddStaffForm
from ai.models import AI_Agent ,  Whatsapp, Escalation, TaskPipeline
from customers.models import CustomerMessage, Conversation, Interaction, Customer
from clients.decorators import team_member_required, dynamic_login_required
from django.http import JsonResponse
from django.http import HttpResponseForbidden
import json

# Create your views here.
from django.contrib.auth.models import Group
def register_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        client_name = request.POST.get('client_name')
        business_name = request.POST.get('business_name')
        industry = request.POST.get('industry')

        # Validate inputs
        if password != confirm_password:
            messages.success(request, 'Passwords do not match.')
            return redirect('register_user')

        if User.objects.filter(username=username).exists():
            messages.success(request, 'Username already exists.')
            return redirect('register_user')

        if Client.objects.filter(business_name=business_name).exists():
            messages.success(request, 'Business name already exists. We suggest adding some characters.')
            return redirect('register_user')
        
        # Create user and client
        slug = slugify(business_name)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_staff = True  # Mark the user as staff
        user.save()

        client = Client.objects.create(
            user=user,
            slug=slug,
            email=email,
            client_name=client_name,
            business_name=business_name,
            phone_number=phone_number,
            industry=industry,
        )
        
        Staff.objects.create(
            user=user,
            client=client,
            email=email,
            phone_number=phone_number,
            name=client_name,
            role='owner',
        )
        
        group_name = "clients"  # Replace with the actual group name
        group, created = Group.objects.get_or_create(name=group_name)

        user.groups.add(group)

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard', slug)

    return render(request, 'clients/pages-register.html')

@login_required(login_url="/login-user/")
def add_business(request):
    current_clients = Client.objects.filter(user=request.user).first()
    if current_clients:
        if request.method == "POST":
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            business_name = request.POST.get('business_name')
            industry = request.POST.get('industry')

            if Client.objects.filter(business_name=business_name).exists():
                messages.success(request, 'Business name already exists. We suggest adding some characters.')
                return redirect('add_business')
            
            # Create user and client
            slug = slugify(business_name)

            
            client = Client.objects.create(
                user= request.user,
                slug=slug,
                email=email,
                client_name=current_clients.client_name,
                business_name=business_name,
                phone_number=phone_number,
                industry=industry,
            )
            
            Staff.objects.create(
                user=request.user,
                client=client,
                email=email,
                phone_number=phone_number,
                name=current_clients.client_name,
                role='owner',
            )

            return redirect('dashboard', slug)

        return render(request, 'clients/add-client.html')
    else:
        messages.success(request, 'You dont have any Business account created create one...')
        return redirect('register_user')
    
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "logged in successfully...")
            if next:
                return redirect('index')
        else:
            messages.success(request, "Check your username or password *all are case sensitive*")
            return redirect('login_user')
    else:
        return render(request, 'clients/login.html')



def login_view(request, slug):
    client = Client.objects.filter(slug=slug).first()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            

            team = Staff.objects.filter(client=client)
            is_team_member = team.filter(user=request.user).exists()
            if not is_team_member:
                messages.success(request, "You have NO permission to login into this account")
                logout(request)
                return redirect('index')
            else:
                messages.success(request, "You Have Been Logged In!")
                return redirect('dashboard', slug)
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('login', slug)
    else:
        return render(request, 'clients/pages-login.html', {'client': client})


def logout_view(request, slug):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('login', slug)



def index(request):
    clients = None
    if request.user.is_authenticated:
        clients = Client.objects.filter(user=request.user)
        staff = Staff.objects.filter(user=request.user).first()
        if clients:
            return redirect('clients')
        elif staff:
            return redirect('dashboard', staff.client.slug)
    context = {
        'clients':clients
    }
    return render(request, 'home/index.html', context)

@login_required(login_url="/login-user/")
def clients(request):
    clients = Client.objects.filter(user=request.user)
    if not clients:
        return HttpResponseForbidden("You do not have permission to visit this page.")
    clients_count = clients.count()
    client = clients.first()
    if clients_count <= 1:
        return redirect('dashboard', client.slug)
    
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    
    context = {
        'clients': clients,
        'client': client,
        'staff': staff,
        'escalations': escalations,
        'escalations_count': escalations_count,
        'chats': chats,
        'chats_count': chats_count,
    }
    return render(request, 'clients/clients.html', context)


@dynamic_login_required
@team_member_required
def dashboard(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()

    tasks = TaskPipeline.objects.filter(
        client=client,
        done=False,
        follow_up_date=now().date(),
        follow_up_date__isnull=False
        ).filter(
            Q(staff__isnull=True) | Q(staff=staff)
        )
    
    customer_messages = CustomerMessage.objects.filter(
        client=client,
        replied=False,
        )
    
    interactions = Interaction.objects.filter(
        client=client,
        date_created__date=now().date()
        ).filter(
            Q(staff__isnull=True) | Q(staff=staff)
        )
    
    customers = Customer.objects.filter(
        client=client,
        date_added__date=now().date(),
        )
    context = {
        'client': client,
        'clients': clients,
        'staff': staff,
        'escalations': escalations,
        'escalations_count': escalations_count,
        'chats': chats,
        'chats_count': chats_count,
        'tasks': tasks,
        'customer_messages': customer_messages, 
        'interactions':interactions,
        'customers':customers
    }
    return render(request, 'dashboard/dashboard.html', context)



def policy(request, slug):
    client = Client.objects.filter(slug=slug).first()
    policy = TermsAndPolicy.objects.order_by('id').first()
    title = client.business_name if client else "Your Site"
    ai = AI_Agent.objects.order_by('id').first()
    

    return render(request, 'policy.html', {'title' : title, 'client': client, 'policy': policy, 'ai': ai})



# Create your views here.
def documentation(request, slug):
    client = Client.objects.filter(slug=slug).first()
    title = client.business_name if client else "Your Site"
    ai = AI_Agent.objects.order_by('id').first()
    
    tenant_domain = request.get_host()


    webhook_url = f"https://{tenant_domain}/02a10962-b38b-4d7a-a62c-4f22e2a32e46/"
    
    whatsap = Whatsapp.objects.order_by('id').first()
    verify_token  = request.session.get('verify_token')

    characters = string.ascii_letters + string.digits

    if whatsap and not whatsap.whatsapp_verify_token:
        if not verify_token:
            verify_token = "".join(secrets.choice(characters)for _ in range(100))
            request.session['verify_token'] = verify_token
    else:
        verify_token = "".join(secrets.choice(characters)for _ in range(100))
        request.session['verify_token'] = verify_token
    context ={
        'title' : title,
        'verify_token': verify_token,
        'webhook_url': webhook_url,
        'tenant_domain': tenant_domain,
        'whatsap': whatsap,
        'ai': ai

    }
    return render(request, 'documentation.html', context)

def faq(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    
    faqs = FAQ.objects.filter(client=client).all()
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'faqs': faqs
    }
    return render(request, 'clients/faq.html', context)

@dynamic_login_required
@team_member_required
def add_staff(request, slug):
    clients = Client.objects.filter(user=request.user)
    if not clients:
        messages.success(request, 'You dont have permission to add staff.')
        return redirect('dashboard', slug)
    client = Client.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.success(request, 'Passwords do not match.')
            return redirect('add_staff', slug)

        if User.objects.filter(username=username).exists():
            messages.success(request, 'Username already exists.')
            return redirect('add_staff', slug)
        user = User.objects.create_user(
            username=username,
            password=password,
        )
        user.is_staff = True  # Mark the user as staff
        user.save()
        group_name = "staffs"  # Replace with the actual group name
        group, created = Group.objects.get_or_create(name=group_name)

        user.groups.add(group)
        form = AddStaffForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.client = client
            instance.user = user
            instance.save()
            messages.success(request, "Staff added Succesfully")
            messages.success(request, "share with him or her the username and paswword plus your page url to log in")
            return redirect('dashboard', slug)
        messages.success(request, "error adding staff makesure to fill your information correctly")
        return redirect('add_staff', slug)
    else:
        form = AddStaffForm()
        context = {
            'client' : client,
            'clients' : clients,
            'staff' : staff,
            'escalations' : escalations,
            'escalations_count' :  escalations_count,
            'chats' : chats,
            'chats_count' : chats_count,
            'form': form
        }
        return render(request, 'clients/add_staff.html', context)