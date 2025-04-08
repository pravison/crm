from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import AI_Agent ,  Whatsapp, Escalation, TaskPipeline, KnowledgeBase
from .forms import AddTaskPipelineForm, AddKnowledgeBaseForm
from clients.models import Client, Staff
from customers.models import Customer, Conversation
from clients.decorators import team_member_required, dynamic_login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@dynamic_login_required
@team_member_required
@csrf_exempt
def assign_task(request, slug):
    client = Client.objects.filter(slug=slug).first()
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        staff_id = data.get('staff_id')
        follow_up_date = data.get('follow_up_date')

        try:
            task = TaskPipeline.objects.get(id=task_id, client=client)
            staff = Staff.objects.get(id=staff_id, client=client)
            task.staff = staff
            task.follow_up_date = follow_up_date
            task.save()
            return JsonResponse({'message': 'Task successfully assigned!'}, status=200)
        except TaskPipeline.DoesNotExist:
            return JsonResponse({'error': 'Task not found.'}, status=404)
        except Staff.DoesNotExist:
            return JsonResponse({'error': 'Staff not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request.'}, status=400)


@dynamic_login_required
@team_member_required
def tasks(request, slug):
    # Get only one client matching the slug
    client = Client.objects.filter(slug=slug).first()
    if not client:
        return redirect('some_error_page')  # Add error handling if needed

    # Only get clients related to this user
    clients = Client.objects.filter(user=request.user)

    # Use select_related to avoid extra queries for user and client
    staff = Staff.objects.select_related('user', 'client').filter(user=request.user, client=client).first()

    # Count only — no need to load entire objects
    escalations_count = Escalation.objects.filter(client=client, done=False).count()
    chats_count = Conversation.objects.filter(client=client, read=False).count()

    # Load only tasks with relevant staff or no staff assigned
    tasks = TaskPipeline.objects.filter(
        client=client
    ).filter(
        Q(staff__isnull=True) | Q(staff=staff)
    ).select_related('staff').order_by('-id')

    context = {
        'client': client,
        'clients': clients,
        'staff': staff,
        'escalations_count': escalations_count,
        'chats_count': chats_count,
        'tasks': tasks,
    }
    return render(request, 'ai/tasks.html', context)

@dynamic_login_required
@team_member_required
def add_task(request, slug):
    customer_id = request.GET.get('customer_id')
    customer = None
    if customer_id:
        customer = Customer.objects.filter(id=customer_id).first()
        if customer is None:
            messages.success(request, "Customer does not  we suggest you head to customers list and select customer again!")
            return redirect('add_task', slug)
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()

    if request.method == 'POST':
        form = AddTaskPipelineForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.client=client
            instance.staff = staff
            instance.customer = customer
            instance.save()

            messages.success(request, "Task succesfully added")
            return redirect('add_task', slug)
        messages.success(request, "error adding task makesure to fill your information correctly")
        return redirect('add_task', slug)
    else:
        form = AddTaskPipelineForm()
        context = {
            'client' : client,
            'clients' : clients,
            'staff' : staff,
            'escalations' : escalations,
            'escalations_count' :  escalations_count,
            'chats' : chats,
            'chats_count' : chats_count,
            'form': form,
            'customer_id': customer_id
        }
        return render(request, 'ai/add-task.html', context)

@dynamic_login_required
@team_member_required
def knowledge_base(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    
    knowledge_base = KnowledgeBase.objects.filter(client=client)
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'knowledge_base': knowledge_base
    }
    return render(request, 'ai/knowledge-base.html', context)

@dynamic_login_required
@team_member_required
def add_knowledge_base(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    if request.method == 'POST':
        form = AddKnowledgeBaseForm(request.POST, request.FILES)
        if form.is_valid():
            instance=form.save()
            instance.client=client
            instance.save()
            messages.success(request, "Knowledge base added succesfuly")
            return redirect('knowledge_base', slug)
        messages.success(request, "error adding Knowledge base makesure to fill your information correctly")
        return redirect('add_knowledge_base', slug)
    else:
        form = AddKnowledgeBaseForm()
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
        return render(request, 'ai/add-knowledge-base.html', context)