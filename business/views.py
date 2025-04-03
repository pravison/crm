from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .functions import handleWhatsappCall, follow_up_tasks_today, add_customers_to_pipeline, save_conversation, aiWorkReport, chatbotResponse
from customers.models import Customer, Conversation
from clients.models import Client, Staff
from ai.models import TaskPipeline, Escalation, AI_Agent , SalesFunnelStageInstruction, Whatsapp
# from store.models import Product
import json
from datetime import  date, timedelta
from django.utils import timezone


current_date = timezone.now().date()

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(10)

today = date.today()
tommorow = today + timedelta(days=1)
after_tommorow = today + timedelta(days=2)
fourth_day = today + timedelta(days=2)

processed_message_ids = set()

@login_required
def index(request):
    chats= Conversation.objects.filter(date_added=current_date)
    total_chats = chats.count()
    tasks= TaskPipeline.objects.filter(follow_up_date=current_date, done=True)
    total_tasks = tasks.count()
    escalations = Escalation.objects.filter(date=current_date)
    total_escalations = escalations.count()
    ai = AI_Agent.objects.order_by('id').first()
    instruction = SalesFunnelStageInstruction.objects.order_by('id').first()
    whatsap = Whatsapp.objects.order_by('id').first()
    customer = Customer.objects.order_by('id').first()
    company = Client.objects.order_by('id').first()
    title = company.company_name if company else "Your Site"
    
    tenant_domain = request.get_host()
    context = {
        'title' : title, 
        'total_chats': total_chats, 
        'total_tasks': total_tasks, 
        'total_escalations': total_escalations,
        'ai': ai,
        'instruction' : instruction,
        'whatsap': whatsap,
        'company': company,
        'customer': customer,
        'tenant_domain': tenant_domain
    }
    return render(request, 'index.html', context)

def terms(request):
    chats= Conversation.objects.filter(date_added=current_date)
    total_chats = chats.count()
    tasks= TaskPipeline.objects.filter(follow_up_date=current_date, done=True)
    total_tasks = tasks.count()
    escalations = Escalation.objects.filter(date=current_date)
    total_escalations = escalations.count()
    context = {
       
    }
    return render(request, 'terms.html', context)
def privacy(request):
    chats= Conversation.objects.filter(date_added=current_date)
    total_chats = chats.count()
    tasks= TaskPipeline.objects.filter(follow_up_date=current_date, done=True)
    total_tasks = tasks.count()
    escalations = Escalation.objects.filter(date=current_date)
    total_escalations = escalations.count()
    context = {
       
    }
    return render(request, 'policy.html', context)
        
@csrf_exempt
def whatsappWebhook(request, slug):
    client = Client.objects.filter(slug=slug).first()
    whatsapp = Whatsapp.objects.filter(client=client).first()
    if request.method == "GET":
        VERIFY_TOKEN = whatsapp.whatsapp_verify_token
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('error', status=403)
        
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'object' in data and data['object'] == 'whatsapp_business_account':
            try:
                for entry in data.get('entry', []):
                    changes = entry.get('changes', [])
                    if changes:
                        value = changes[0].get('value', {})
                        metadata = value.get('metadata', {})
                        phoneId = metadata.get('phone_number_id')
                        contacts = value.get('contacts', [])
                        if contacts:
                            profileName = contacts[0].get('profile', {}).get('name')
                            # whatsAppId = contacts[0].get('wa_id')
                        messages = value.get('messages', [])
                        if messages:
                            fromId = messages[0].get('from')
                            text = messages[0].get('text', {}).get('body')
                            message_id = messages[0].get('id')


                            # Check if customer with the phone number exists
                            customer = Customer.objects.filter(client=client, phone_number=fromId).order_by('id').first()
                            if not customer:
                                customer= Customer.objects.get_or_create(
                                        client=client,
                                        phone_number=fromId,
                                        whatsapp_profile = profileName,
                                    )   
                            
                            tasks = TaskPipeline.objects.filter(client=client, customer=customer).count()
                            if tasks < 2:
                                TaskPipeline.objects.create(
                                    customer=customer,
                                    task = """compose a thoughtfull follow-up message to send to a customer one day after customer reaching out to us.""",
                                    follow_up_date =  tommorow
                                )
                                TaskPipeline.objects.create(
                                    customer=customer,
                                    task = """Draft a follow-up message to a customer for two days after customer reaching out to us.""",
                                    follow_up_date =  after_tommorow
                                )
                                TaskPipeline.objects.create(
                                    customer=customer,
                                    task = """Draft a follow-up message to a customer for 3 days after customer reaching out to us. """,
                                    follow_up_date =  fourth_day
                                )
                            
                            # Process the message only if it hasn't been processed before
                            if message_id not in processed_message_ids:
                                processed_message_ids.add(message_id)
                                sender = 'customer'
                                message = text
                                save_conversation(client, customer, message, sender )
                                customer_message = text
                                handleWhatsappCall(client, fromId, customer_message)
                                
                                break
                            break

            except Exception as e:
                print(f"Error processing webhook data: {e}")
                return HttpResponse('error', status=500)
        else:
            return HttpResponse('error', status=400)

        return HttpResponse('success', status=200)
    
@login_required
def leadsWarmupPage(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    tasks = TaskPipeline.objects.filter(
        client=client,
        follow_up_date = today
        ).order_by('id')
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'tasks': tasks
    }
    return render(request, 'leads_warmup.html', context)


def addCustomersForFollowUp(request, slug):
    client = Client.objects.filter(slug=slug).first()
    add_customers_to_pipeline(client)
    aiWorkReport(client)
    return JsonResponse({"status": "customers have been addepd for follow-up"})


def customersForFollowUp(request, slug):
    client = Client.objects.filter(slug=slug).first()
    follow_up_tasks_today(client)
    return JsonResponse({"status": "customers have beeb followed up"})






@csrf_exempt
def chatbot_response(request, slug):
    client = Client.objects.filter(slug=slug).first()
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        history = data.get('history', [])  # List of recent messages

        # Generate the bot response
        bot_response = chatbotResponse(client, user_message, history)

        # Return the AI's response to the frontend
        return JsonResponse({"response": bot_response})

    return JsonResponse({"error": "Invalid request method"}, status=400)

