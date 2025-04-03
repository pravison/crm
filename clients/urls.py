from django.urls import path
from ai.views import tasks, add_task, assign_task, knowledge_base, add_knowledge_base
from customers.views import chat_lists, chat, add_customer, customers, write_message, add_interaction, escalations, interactions
from transactions.views import create_invoice, invoices, view_invoice, generate_pdf, create_contract, view_contract, contracts
from business.views import whatsappWebhook, chatbot_response, customersForFollowUp, addCustomersForFollowUp, leadsWarmupPage
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register-user/', views.register_user, name='register_user'),
    path('add-business/', views.add_business, name='add_business'),
    path('client/', views.clients, name='clients'),
    path('login-user/', views.login_user, name='login_user'),
    path('<slug:slug>/login/', views.login_view, name='login'),
    path('<slug:slug>/logout/', views.logout_view, name='logout'),
    path('<slug:slug>/dashboard/', views.dashboard, name='dashboard'),
    path('<slug:slug>/policy/', views.policy, name='policy'),
    path('<slug:slug>/faqs/', views.faq, name='faqs'),
    path('<slug:slug>/documentation/', views.documentation, name='documentation'),
    path('<slug:slug>/add-staff/', views.add_staff, name='add_staff'),

    # transaction create_invoice
    path('<slug:slug>/create-invoice/', create_invoice, name='create_invoice'),
    path('<slug:slug>/invoices/', invoices, name='invoices'),
    path('<slug:slug>/view-invoice/', view_invoice, name='view_invoice'),
    path('<slug:slug>/generate-pdf/', generate_pdf, name='generate_pdf'),
    path('<slug:slug>/create-contract/', create_contract, name='create_contract'),
    path('<slug:slug>/contracts/', contracts, name='contracts'),
    path('<slug:slug>/view-contract/', view_contract, name='view_contract'),

    # ai
    path('<slug:slug>/escaltions/', escalations, name='escalations'),
    path('<slug:slug>/task-pipelines/', tasks, name='tasks'),
    path('<slug:slug>/add-task/', add_task, name='add_task'),
    path('<slug:slug>/assign_task/', assign_task, name='assign_task'),
    path('<slug:slug>/knowledge-base/', knowledge_base, name='knowledge_base'),
    path('<slug:slug>/add-knowledge-base/', add_knowledge_base, name='add_knowledge_base'),


    # customers
    path('<slug:slug>/chat-list/', chat_lists, name='chat_lists'),
    path('<slug:slug>/chat/', chat, name='chat'),
    path('<slug:slug>/add-customer/', add_customer, name='add_customer'),
    path('<slug:slug>/customers/', customers, name='customers'),
    path('<slug:slug>/write-message/', write_message, name='write_message'),
    path('<slug:slug>/add-interaction/', add_interaction, name='add_interaction'),
    path('<slug:slug>/escalations/', escalations, name='escalations'),
    path('<slug:slug>/interactions/', interactions, name='interactions'),

    # business
    path('<slug:slug>/02a10962-b38b-4d7a-a62c-4f22e2a32e46/', whatsappWebhook, name='whatsapp_webhook'),
    path('<slug:slug>/leads_warmup_page/', leadsWarmupPage, name='leads_warmup_page'),
    path('<slug:slug>/add_customer_to_pipeline/', addCustomersForFollowUp, name='add_customer_to_pipeline'),
    path('<slug:slug>/follow_up_customers/', customersForFollowUp, name='follow_up_customers'),
    path('<slug:slug>/chatbot-response/', chatbot_response, name='chatbot_response'),
]