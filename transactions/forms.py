from django import forms
from .models import RealEstateContract, Invoice

class CreateInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('title', 'due_date', 'recipient_full_name', 'recipient_email', 'recipient_phone_number', 'property_name', 'price', 'property_address', 'transaction_type', 'service_or_item', 'amount', 'tax_included', 'tax_rate', 'discounts', 'payment_methods_accepted', 'payment_details', 'reference_instructions', 'additional_information')
        widgets = {
            'title' : forms.TextInput(attrs={'class': "form-control",  'id': 'title'}),
            'due_date' : forms.DateInput(attrs={'class': "form-control", 'type':'date',  'id': 'due_date'}),
            'recipient_full_name' : forms.TextInput(attrs={'class': "form-control", 'id': 'recipient_full_name'}),
			'recipient_email' : forms.EmailInput(attrs={'class': "form-control", 'id': 'recipient_email'}),
            'recipient_phone_number' : forms.NumberInput(attrs={'class': "form-control", 'id': 'recipient_phone_number', 'placeholder':"invoice recipient phone number"}),
			'property_name' : forms.TextInput(attrs={'class': "form-control",  'id': 'property_name'}),
            'price' : forms.NumberInput(attrs={'class': "form-control",  'id': 'property_price'}),
            'property_address' : forms.Textarea(attrs={'class': "form-control",  'id': 'property_address'}),
            'transaction_type' : forms.Textarea(attrs={'class': "form-control",  'id': 'transaction_type'}),
            'service_or_item' : forms.TextInput(attrs={'class': "form-control",  'id': 'service_or_item'}),
            'amount' : forms.NumberInput(attrs={'class': "form-control",  'id': 'amount'}),
            'tax_included' : forms.CheckboxInput(attrs={'id': 'tax_included'}),
            'tax_rate' : forms.NumberInput(attrs={'class': "form-control",  'id': 'tax_rate'}),
            'discounts' : forms.NumberInput(attrs={'class': "form-control",  'id': 'discounts'}),
            'payment_methods_accepted' : forms.Textarea(attrs={'class': "form-control",  'id': 'payment_methods_accepted'}),
            'payment_details' : forms.Textarea(attrs={'class': "form-control",  'id': 'payment_details'}),
            'reference_instructions' : forms.Textarea(attrs={'class': "form-control",  'id': 'reference_instructions'}),
            'additional_information' : forms.Textarea(attrs={'class': "form-control",  'id': 'additional_information'}),
            'settled' : forms.CheckboxInput(attrs={'id': 'settled'}),
            }
        



class RealEstateContractForm(forms.ModelForm):
    class Meta:
        model = RealEstateContract
        fields = [
            'contract_type', 'start_date', 'end_date', 'seller_landlord_name', 
            'seller_landlord_contact', 'buyer_tenant_name', 'buyer_tenant_contact', 'agent_name',
            'agent_contact', 'agent_license_number', 'property_name', 'property_address', 'property_description', 
            'included_fixtures', 'excluded_fixtures', 'price_amount', 'deposit_amount', 
            'deposit_due_date', 'payment_schedule', 'taxes_fees', 'contingencies', 
            'possession_date', 'default_clauses', 'termination_conditions', 
            'dispute_resolution', 'governing_law', 'non_disclosure_clause', 
            'indemnification_clause', 'pets_policy', 'maintenance_responsibilities', 
            'additional_terms', 'attachments'
        ]
        widgets = {
            'contract_type': forms.Select(attrs={'class': "form-control", 'id': 'contract_type'}),
            'start_date': forms.DateInput(attrs={'class': "form-control", 'type': 'date', 'id': 'start_date'}),
            'end_date': forms.DateInput(attrs={'class': "form-control", 'type': 'date', 'id': 'end_date', 'placeholder': "Optional"}),
            'seller_landlord_name': forms.TextInput(attrs={'class': "form-control", 'id': 'seller_landlord_name'}),
            'seller_landlord_contact': forms.TextInput(attrs={'class': "form-control", 'id': 'seller_landlord_contact'}),
            'buyer_tenant_name': forms.TextInput(attrs={'class': "form-control", 'id': 'buyer_tenant_name'}),
            'buyer_tenant_contact': forms.TextInput(attrs={'class': "form-control", 'id': 'buyer_tenant_contact'}),
            'agent_name': forms.TextInput(attrs={'class': "form-control", 'id': 'agent_name', 'placeholder': "Optional"}),
            'agent_contact': forms.TextInput(attrs={'class': "form-control", 'id': 'agent_contact', 'placeholder': "Optional"}),
            'agent_license_number': forms.TextInput(attrs={'class': "form-control", 'id': 'agent_license_number', 'placeholder': "Optional"}),
            'property_name': forms.TextInput(attrs={'class': "form-control", 'id': 'property_name'}),
            'property_address': forms.Textarea(attrs={'class': "form-control", 'id': 'property_address'}),
            'property_description': forms.Textarea(attrs={'class': "form-control", 'id': 'property_description', 'placeholder': "Optional"}),
            'included_fixtures': forms.Textarea(attrs={'class': "form-control", 'id': 'included_fixtures', 'placeholder': "Optional"}),
            'excluded_fixtures': forms.Textarea(attrs={'class': "form-control", 'id': 'excluded_fixtures', 'placeholder': "Optional"}),
            'price_amount': forms.NumberInput(attrs={'class': "form-control", 'id': 'price_amount', 'placeholder': "Optional"}),
            'deposit_amount': forms.NumberInput(attrs={'class': "form-control", 'id': 'deposit_amount', 'placeholder': "Optional"}),
            'deposit_due_date': forms.DateInput(attrs={'class': "form-control", 'type': 'date', 'id': 'deposit_due_date', 'placeholder': "Optional"}),
            'payment_schedule': forms.Textarea(attrs={'class': "form-control", 'id': 'payment_schedule', 'placeholder': "Optional"}),
            'taxes_fees': forms.Textarea(attrs={'class': "form-control", 'id': 'taxes_fees', 'placeholder': "Optional"}),
            'contingencies': forms.Textarea(attrs={'class': "form-control", 'id': 'contingencies', 'placeholder': "Optional"}),
            'possession_date': forms.DateInput(attrs={'class': "form-control", 'type': 'date', 'id': 'possession_date', 'placeholder': "Optional"}),
            'default_clauses': forms.Textarea(attrs={'class': "form-control", 'id': 'default_clauses', 'placeholder': "Optional"}),
            'termination_conditions': forms.Textarea(attrs={'class': "form-control", 'id': 'termination_conditions', 'placeholder': "Optional"}),
            'dispute_resolution': forms.Textarea(attrs={'class': "form-control", 'id': 'dispute_resolution', 'placeholder': "Optional"}),
            'governing_law': forms.TextInput(attrs={'class': "form-control", 'id': 'governing_law', 'placeholder': "Optional"}),
            'non_disclosure_clause': forms.CheckboxInput(attrs={'id': 'non_disclosure_clause'}),
            'indemnification_clause': forms.CheckboxInput(attrs={'id': 'indemnification_clause'}),
            'pets_policy': forms.Textarea(attrs={'class': "form-control", 'id': 'pets_policy', 'placeholder': "Optional"}),
            'maintenance_responsibilities': forms.Textarea(attrs={'class': "form-control", 'id': 'maintenance_responsibilities', 'placeholder': "Optional"}),
            'additional_terms': forms.Textarea(attrs={'class': "form-control", 'id': 'additional_terms', 'placeholder': "Optional"}),
            'attachments': forms.ClearableFileInput(attrs={'class': "form-control", 'id': 'attachments', 'placeholder': "Optional"}),
            
        }
