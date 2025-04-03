from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from datetime import date, timedelta
from django.utils.timezone import now
from clients.models import Client, Staff
from .models import Invoice, RealEstateContract
from .forms import CreateInvoiceForm, RealEstateContractForm
from ai.models import  Escalation
from customers.models import Conversation
from clients.decorators import team_member_required, dynamic_login_required
from django.shortcuts import render, redirect
# Create your views here.

@dynamic_login_required
@team_member_required
def create_invoice(request, slug):
    client = Client.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    if request.method == 'POST':
        form = CreateInvoiceForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.client = client
            instance.created_by = staff
            instance.tax_rate = Decimal(form.cleaned_data['tax_rate']) if form.cleaned_data['tax_rate'] else Decimal(0)
            instance.discounts = Decimal(form.cleaned_data['discounts']) if form.cleaned_data['discounts'] else Decimal(0)
            instance.property_price = Decimal(form.cleaned_data['property_price']) if form.cleaned_data['property_price'] else Decimal(0)
            tax_rate = form.cleaned_data['tax_rate']
            tax_included = form.cleaned_data['tax_included']
            if tax_rate and tax_rate <=0 :
                messages.success(request, "enter valid tax rate it be above 0 ")
                return redirect('create_invoice', slug)
            grand_total = Decimal(form.cleaned_data['amount'] + (((tax_rate*form.cleaned_data['amount']/100) if tax_rate else 0) if not  tax_included else 0) - (form.cleaned_data['discounts'] if form.cleaned_data['discounts'] else Decimal(0)))
            instance.grand_total = grand_total

            instance.save()
            messages.success(request, "Invoice Created Succesfully")
            return redirect('invoices', slug)
        messages.success(request, "error creating invoice makesure to fill your information correctly")
        return redirect('create_invoice', slug)
    else:
        form = CreateInvoiceForm()
        context = {
            'client' : client,
            'staff' : staff,
            'escalations' : escalations,
            'escalations_count' :  escalations_count,
            'chats' : chats,
            'chats_count' : chats_count,
            'form': form
        }
        return render(request, 'transactions/create-invoice.html', context)

@dynamic_login_required
@team_member_required
def invoices(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    
    invoices = Invoice.objects.filter(client=client).order_by('-id')
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'invoices':invoices,
        'current_date' : date.today()
    }
    return render(request, 'transactions/invoices.html', context)


def view_invoice(request, slug):
    invoice_id = request.GET.get('invoice_id')
    if not invoice_id:
        messages.success(request, "reselect invoice, no invoice associated with query")
        return redirect('invoices', slug)
    invoice = Invoice.objects.filter(id=invoice_id).first()
    if not invoice:
        messages.success(request, "Invoice not found reselect")
        return redirect('invoices', slug)
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    
    tax = Decimal((invoice.tax_rate * invoice.amount)/100)
    context = {
        'client' : client,
        'invoice':invoice,
        'tax': tax
    }
    return render(request, 'transactions/view-invoice.html', context)

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_pdf(request, slug):
    invoice_id = request.GET.get('invoice_id')
    contract_id = request.GET.get('contract_id')
    
    if invoice_id :
        if not invoice_id:
            return HttpResponse('invoice not found, this usually occurs when you interfered with the shared link or mistyped the link reach out to be send another link')
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return HttpResponse('invoice not found, this usually occurs when you interfered with the shared link or mistyped the link reach out to be send another link')
        client = Client.objects.filter(slug=slug).first()
        tax = Decimal((invoice.tax_rate * invoice.amount)/100)
        # Load the HTML template
        template = get_template('transactions/view-invoice.html')
        context = {
            'invoice': invoice, 
            'tax': tax,
            'client': client
        }
        html = template.render(context)

        # Create a PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'

        # Generate the PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response

    elif contract_id:
        if not contract_id:
            return HttpResponse('contract not found, this usually occurs when you interfered with the shared link or mistyped the link reach out to be send another link')
        contract = RealEstateContract.objects.filter(id=contract_id).first()
        if not contract:
            return HttpResponse('contract not found, this usually occurs when you interfered with the shared link or mistyped the link reach out to be send another link')
        client = Client.objects.filter(slug=slug).first()
        
        # Load the HTML template
        template = get_template('transactions/view-contract.html')
        context = {
            'client' : client,
            'contract':contract
        }
        html = template.render(context)

        # Create a PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="contract_{contract.id}.pdf"'

        # Generate the PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return HttpResponse('Error acceseing the document please refresh the page and retry')





@dynamic_login_required
@team_member_required
def create_contract(request, slug):
    client = Client.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    if request.method == 'POST':
        form = RealEstateContractForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.client = client
            instance.created_by = staff
            instance.save()
            messages.success(request, "Contract created successfully.")
            return redirect('contracts', slug)  # Redirect to a contracts list or detail page
        else:
            messages.error(request, "Error creating contract. Please check the form for errors.")
    else:
        form = RealEstateContractForm()
        context = {
            'client' : client,
            'staff' : staff,
            'escalations' : escalations,
            'escalations_count' :  escalations_count,
            'chats' : chats,
            'chats_count' : chats_count,
            'form': form
        }
        return render(request, 'transactions/create_contract.html', context)


@dynamic_login_required
@team_member_required
def contracts(request, slug):
    client = Client.objects.filter(slug=slug).first()
    clients = Client.objects.filter(user=request.user)
    staff = Staff.objects.filter(user=request.user, client=client).first()

    escalations = Escalation.objects.filter(client=client, done=False)
    escalations_count = escalations.count()

    chats = Conversation.objects.filter(client=client, read=False)
    chats_count = chats.count()
    
    contracts = RealEstateContract.objects.filter(client=client).order_by('-id')
    context = {
        'client' : client,
        'clients' : clients,
        'staff' : staff,
        'escalations' : escalations,
        'escalations_count' :  escalations_count,
        'chats' : chats,
        'chats_count' : chats_count,
        'contracts': contracts,
        'current_date' : date.today()
    }
    return render(request, 'transactions/contracts.html', context)


def view_contract(request, slug):
    contract_id = request.GET.get('contract_id')
    if not contract_id:
        messages.success(request, "reselect contract, no contract associated with query")
        return redirect('invoices', slug)
    contract = RealEstateContract.objects.filter(id=contract_id).first()
    if not contract:
        messages.success(request, "contract not found reselect")
        return redirect('contracts', slug)
    client = Client.objects.filter(slug=slug).first()
    context = {
        'client' : client,
        'contract':contract
    }
    return render(request, 'transactions/view-contract.html', context)



