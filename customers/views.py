from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count, Q, Max, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from clients.models import Client, Staff
from .models import Customer, Conversation, Interaction
from .forms import AddInteractionForm, AddTaskPipelineForm, EditEscaltion, AddCustomerForm
from ai.models import TaskPipeline, Escalation, AI_Agent, Whatsapp
from clients.decorators import team_member_required, dynamic_login_required
# from store.models import Product
from business.functions import sendWhatsappMessage, follow_up_immediately
from django.utils import timezone
from datetime import date, timedelta
import json

# Create your views here.
@dynamic_login_required
@team_member_required
def chat_lists(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    whatsapp = Whatsapp.objects.order_by('id').first()
    ai = AI_Agent.objects.order_by('id').first()
    customers = Customer.objects.filter(client=client).annotate(unread_count=Count('conversations', filter=Q(conversations__read=False)), last_message_send=Max('conversations__timestamp')).order_by('-last_message_send')
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'customers': customers,
        'whatsapp' : whatsapp,
        'ai': ai
        # 'customers_with_converstaions' : customers_with_converstaions
    }
    return render(request, 'customers/chats-lists.html', context)

@dynamic_login_required
@team_member_required
def chat(request, slug):
    customer_id = request.GET.get('customer_id')
    if not customer_id:
            messages.success(request, "Customer does not exists suggest head to customers list and select customer again!")
            return redirect('chat_lists', slug)
    customer = None
    if customer_id:
        customer = Customer.objects.filter(id=customer_id).first()
        if customer is None:
            messages.success(request, "Customer does not exists suggest head to customers list and select customer again!")
            return redirect('chat_lists', slug)
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    customer_chats = Conversation.objects.filter(customer=customer, client=client).order_by('timestamp')

    unread_chats = customer_chats.filter(read=False)
    for chat in unread_chats:
        chat.read=True
        chat.save()

    ai = AI_Agent.objects.order_by('id').first()
    tenant_domain = request.get_host()
    if request.method == 'POST':
        message = request.POST['message']

        chat = Conversation(customer=customer, client=client, staff=staff, sender="AI", message=message, read=True)
        chat.save()
        # sending message throug whatsap
        fromId = customer.phone_number
        # sendWhatsappMessage(fromId, message)
        messages.success(request, f'message send to {customer.name}')
        customer.last_talked = timezone.now().date()
        customer.save()
        url = reverse('chat', kwargs={'slug': slug})  # Generates '/pravison/chat/' with the slug
        # Add the query parameter
        query_params = f'?customer_id={customer.id}'
        # Redirect to the complete URL
        return redirect(url + query_params)
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'customer': customer,
        'customer_chats': customer_chats,
        'tenant_domain': tenant_domain,
        'ai': ai
    }
    return render(request, 'customers/chat.html', context)

@dynamic_login_required
@team_member_required
def write_message(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()

    customers = Customer.objects.filter(
        client=client
        ) 
    if request.method == "POST":
        selected_customers = request.POST.getlist('customers')
        funnel_stage = request.POST.get('funnel_stage')
        message_template = request.POST.get('message')

        if funnel_stage:
            if funnel_stage == 'all':
                customers_to_receive_messages = Customer.objects.all()
            else:
                customers_to_receive_messages = Customer.objects.filter(funnel_stage=funnel_stage)
        else:
            # get selected customer 
            customers_to_receive_messages = Customer.objects.filter(id__in = selected_customers)
        for customer in customers_to_receive_messages:

            personalized_message = message_template.replace('{name}', customer.name)
            
            chat = Conversation(customer=customer, sender="AI", message=personalized_message, read=True)
            chat.save()
            customer.last_talked = timezone.now().date()
            customer.save()
            # sending message through whatsap
            # fromId = customer.phone_number
            # sendWhatsappMessage(fromId, personalized_message)
        messages.success(request, f'message send to selected customers')
        return redirect('write_message', slug)
            
    
    
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'customers': customers
    }
    return render(request, 'customers/write-message.html', context)


@dynamic_login_required
@team_member_required
def add_customer(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    if request.method == 'POST':
        form = AddCustomerForm(request.POST)
        if form.is_valid():
            instance=form.save()
            instance.client=client
            phone_number=form.cleaned_data['phone_number']
            customer = Customer.objects.filter(client=client, phone_number=phone_number).exists() 
            if customer:
                messages.success(request, "Customer with such same phone number already exists")
                return redirect('add_customer', slug)
            else:
                instance.save()
                messages.success(request, "Customer succesfully added")
                today = date.today()
                tommorow = today + timedelta(days=1)
                after_tommorow = today + timedelta(days=2)
                after_two_days = today + timedelta(days=3)
                
                TaskPipeline.objects.create(
                    client = client,
                    staff = staff,
                    customer=instance,
                    task = """Draft a follow-up message after one  day """,
                    follow_up_date =  tommorow
                )
                messages.success(request, "customer added to be followed up tommorow")
                TaskPipeline.objects.create(
                    client = client,
                    staff = staff,
                    customer=instance,
                    task = """Draft a follow-up message after two days """,
                    follow_up_date =  after_tommorow
                )
                messages.success(request, "customer added to be followed up after tommorow")
                TaskPipeline.objects.create(
                    client = client,
                    staff = staff,
                    customer=instance,
                    task = """Draft a follow-up message after two days """,
                    follow_up_date =  after_two_days
                )
                messages.success(request, "customer added to be followed up after three days")
                follow_up_immediately(client.id, phone_number)# the function cant caryy whole model but somethind like a text or id can wok
                messages.success(request, "customer is being followed up immediately by AI ")
                
                return redirect('add_customer', slug)
        messages.success(request, "error adding customer makesure to fill your information correctly")
        return redirect('add_customer', slug)
    else:
        form = AddCustomerForm()
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
        return render(request, 'customers/add-customer.html', context)

@dynamic_login_required
@team_member_required
def customers(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    customers = Customer.objects.filter(
        client=client
        )
    
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'customers': customers
    }
    return render(request, 'customers/customers.html', context)


@dynamic_login_required
@team_member_required
def add_interaction(request, slug):
    customer_id = request.GET.get('customer_id')
    customer = None
    if customer_id:
        customer = Customer.objects.filter(id=customer_id).first()
        if customer is None:
            messages.error(request, "Customer does not exist. Please head to the customers list and select the customer again!")
            return redirect('add_task', slug)

    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()

    query = request.GET.get('query', '')

    if request.method == 'POST':
        form = AddInteractionForm(request.POST, customer=customer)  # Pass customer and request
        if form.is_valid():
            instance = form.save(commit=False)
            if customer:
                instance.customer = customer
            instance.client = client
            instance.staff = staff
            instance.save()
            follow_up_immediately(client, customer.phone_number)
            TaskPipeline.objects.create(
                client=client,
                staff=staff,
                customer=customer,
                task=form.cleaned_data['next_step'],
                follow_up_date=form.cleaned_data['next_step_date']
            )

            messages.success(request, "Interaction successfully added.")

            if form.cleaned_data['customer_sales_funnel_stage']:
                customer.funnel_stage = form.cleaned_data['customer_sales_funnel_stage']
                customer.save()

            # Redirect based on query
            if query == 'escalations':
                return redirect('escalations')
            elif query == 'customers':
                return redirect('customers', slug)
            elif query == 'chat':
                url = reverse('chat', kwargs={'slug': slug})
                return redirect(f"{url}?customer_id={customer.id}")
            else:
                return redirect('chat_lists', slug)
        else:
            messages.error(request, "Error occurred while adding interaction. Please try again.")
    else:
        form = AddInteractionForm( customer=customer)

    context = {
        'client': client,
        'clients': clients,
        'staff': staff,
        'escalations': escalations,
        'escalations_count': escalations_count,
        'chats': chats,
        'chats_count': chats_count,
        'customer': customer,
        'form': form,
        'query': query,
    }
    return render(request, 'customers/add-interaction.html', context)


@login_required
def edit_escalation(request, id):
    ai = AI_Agent.objects.order_by('id').first()
    tenant_domain = request.get_host()
    company = CompanyInformation.objects.order_by('id').first()
    title = company.company_name if company else "Your Site"
    escalate = Escalation.objects.filter(id=id).first()
    if request.method == 'POST':
        form = EditEscaltion(request.POST, instance=escalate)
        if form.is_valid():
            form.save()
            messages.success(request, "task succesfully added")
            return redirect('escalations')
            
    else:
        form = EditEscaltion(instance=escalate)
        context = {
            'company' : company,
            'escalate' : escalate,
            'title': title,
            'form': form,
            'tenant_domain': tenant_domain,
            'ai': ai
        }
        return render(request, 'edit-escalation.html', context)
    

@dynamic_login_required
@team_member_required
def escalations(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    escalations_lists = Escalation.objects.filter(client=client).order_by('-id')
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'escalations_lists': escalations_lists
    }
    return render(request, 'customers/escalations.html', context)


@dynamic_login_required
@team_member_required
def interactions(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    interactions = Interaction.objects.filter(
        client=client
        ).filter(
            Q(staff__isnull=True) | Q(staff=staff)
        )
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'interactions': interactions
    }
    return render(request, 'customers/interactions.html', context)

