

from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from clients.models import Client, Staff
from datetime import date

# Create your models here.
class Invoice(models.Model):
    client  = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='invoice')
    created_by = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL, related_name='invoice')
    title = models.CharField(max_length=500)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    settled =  models.BooleanField(default=False)
    recipient_full_name = models.CharField(max_length=300)
    recipient_email = models.EmailField(null=True, blank=True)
    recipient_phone_number = models.CharField(max_length=20)

    property_name  = models.CharField(max_length=20,  null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2,  null=True, blank=True)
    property_address = models.TextField(max_length=500, null=True, blank=True)
    transaction_type = models.CharField(max_length=100, choices=(('rent', 'rent'), ('sale', 'sale'), ('lease', 'lease')))
    # property_description= models.TextField(max_length=500, null=True, blank=True)

    service_or_item= models.CharField(max_length=300, help_text="Brokerage Fee, Property Sale Price, Maintenance Fees, Document Preparation Fees.")
    amount = models.DecimalField(max_digits=20, decimal_places=2, help_text="rent amount, item amount, commission or service amount chargged ..")
    
    tax_included= models.BooleanField(default=False, help_text="check the box or set to true if tax is included in the above amount and vice versa")
    tax_rate= models.IntegerField(  null=True, blank=True, help_text="percentage charged tax if included or want to include in total amount if not leave it blank")

    discounts = models.DecimalField(max_digits=20,  null=True, blank=True, decimal_places=2, help_text="Discounts you provide if any")
    grand_total= models.DecimalField(max_digits=20,  null=True, blank=True, decimal_places=2, help_text="the total amount including taxes minus discounts ")

    payment_methods_accepted = models.TextField(max_length=20,  null=True, blank=True, help_text="Bank transfer, credit card, paybill, till check, etc.") 
    payment_details= models.TextField(max_length=20,  null=True, blank=True, help_text="bank account number, bank name, and  till number etc...")
    reference_instructions = models.TextField(max_length=20,  null=True, blank=True, help_text="e.g.,Include invoice number as payment reference if required")

    additional_information = models.TextField(max_length=500,  null=True, blank=True, help_text="Late payment penalties or other terms.")

    def __str__(self):
        return self.title

    @property
    def days_until_due(self):
        try:
            total_days = abs((self.due_date - date.today()).days)
        except:
            total_days = 0

        return total_days


class RealEstateContract(models.Model):
    # Contract Type
    CONTRACT_TYPES = [
        ('sale', 'Sale Agreement'),
        ('lease', 'Lease Agreement'),
        ('rental', 'Rental Agreement'),
        ('listing', 'Listing Agreement'),
        ('purchase', 'Purchase Agreement'),
    ]
    client  = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='contract')
    created_by = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL, related_name='contract')
    contract_type = models.CharField(
        max_length=20, 
        choices=CONTRACT_TYPES, 
        help_text="Select the type of contract, e.g., Sale, Lease, or Rental."
    )
    date_created = models.DateField(
        auto_now_add=True, 
        help_text="The date when the contract was created."
    )
    start_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="The start date of the contract, if applicable."
    )
    end_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="The end date of the contract, if applicable."
    )

    # Parties Involved
    seller_landlord_name = models.CharField(
        max_length=255, 
        help_text="Full name of the seller or landlord."
    )
    seller_landlord_contact = models.CharField(
        max_length=255, 
        help_text="Contact information of the seller or landlord."
    )
    buyer_tenant_name = models.CharField(
        max_length=255, 
        help_text="Full name of the buyer or tenant."
    )
    buyer_tenant_contact = models.CharField(
        max_length=255, 
        help_text="Contact information of the buyer or tenant."
    )
    agent_name = models.CharField(
        null=True, 
        blank=True,
        max_length=255, 
        help_text="agent Full name "
    )
    agent_contact = models.CharField(
        null=True, 
        blank=True,
        max_length=255, 
        help_text="agent Contact ."
    )
    agent_license_number = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        help_text="The license number of the agent, if applicable."
    )

    # Property Details
    property_name = models.CharField(
        max_length=255, 
        null=True, 
        blank=True
    )
    property_address = HTMLField(
        null=True, 
        blank=True, 
        help_text="The full address of the property involved in the contract."
    )
    property_description = HTMLField(
        null=True, 
        blank=True, 
        help_text="A brief description of the property, including its features."
    )
    included_fixtures = HTMLField(
        null=True, 
        blank=True, 
        help_text="List of fixtures and fittings included in the contract."
    )
    excluded_fixtures = HTMLField(
        null=True, 
        blank=True, 
        help_text="List of fixtures and fittings excluded from the contract."
    )

    # Financial Terms
    price_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The total price or rental amount agreed upon."
    )
    deposit_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The deposit amount to be paid upfront."
    )
    deposit_due_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="The due date for the deposit payment."
    )
    payment_schedule = HTMLField(
        null=True, 
        blank=True, 
        help_text="Details of the payment schedule, if applicable."
    )
    taxes_fees = HTMLField(
        null=True, 
        blank=True, 
        help_text="Information about taxes or fees associated with the contract."
    )

    # Terms and Conditions
    contingencies =HTMLField(
        null=True, 
        blank=True, 
        help_text="Conditions that must be met for the contract to proceed."
    )
    possession_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="The date when the buyer or tenant can take possession."
    )
    default_clauses = HTMLField(
        null=True, 
        blank=True, 
        help_text="Clauses outlining actions in case of default by any party."
    )
    termination_conditions = HTMLField(
        null=True, 
        blank=True, 
        help_text="Conditions under which the contract can be terminated."
    )

    # Legal Clauses
    dispute_resolution = HTMLField(
        null=True, 
        blank=True, 
        help_text="Details on how disputes will be resolved."
    )
    governing_law = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        help_text="The legal jurisdiction governing the contract."
    )
    non_disclosure_clause = models.BooleanField(
        default=False, 
        help_text="Indicates if a non-disclosure agreement is included."
    )
    indemnification_clause = models.BooleanField(
        default=False, 
        help_text="Indicates if an indemnification clause is included."
    )

    # Optional Customizable Clauses
    pets_policy =HTMLField(
        null=True, 
        blank=True, 
        help_text="Details about pet policies, if applicable."
    )
    maintenance_responsibilities = HTMLField(
        null=True, 
        blank=True, 
        help_text="Responsibilities for property maintenance."
    )
    additional_terms = HTMLField(
        null=True, 
        blank=True, 
        help_text="Any additional terms or conditions for the contract."
    )

    # Attachments
    attachments = models.FileField(
        upload_to='contract_attachments/', 
        null=True, 
        blank=True, 
        help_text="Upload any supporting documents related to the contract."
    )

    # Signatures
    seller_landlord_signature = models.ImageField(
        upload_to='signatures/', 
        null=True, 
        blank=True, 
        help_text="Upload the signature of the seller or landlord."
    )
    buyer_tenant_signature = models.ImageField(
        upload_to='signatures/', 
        null=True, 
        blank=True, 
        help_text="Upload the signature of the buyer or tenant."
    )
    witness_signature = models.ImageField(
        upload_to='signatures/', 
        null=True, 
        blank=True, 
        help_text="Upload the signature of a witness, if required."
    )

    def __str__(self):
        return f"{self.contract_type.capitalize()} - {self.property_address[:50]}..."
