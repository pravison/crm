from django.contrib import admin
from clients.models import Staff
from .models import Invoice, RealEstateContract
# Register your models here.
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'invoice_date', 'recipient_full_name', 'service_or_item',  'due_date', 'settled']
    list_filter = [ 'settled', 'invoice_date', 'due_date']
    search_fields = ['title', 'invoice_date', 'recipient_full_name', 'due_date', 'settled', 'recipient_phone_number', 'property_name', 'service_or_item']
    list_display_links= ['title', 'invoice_date', 'recipient_full_name', 'due_date', 'settled']
    readonly_fields =['client', 'created_by']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
            obj.created_by = staff
        # Save the tenant with the modified object
        super().save_model(request, obj, form, change)   

    def get_queryset(self, request):
        # Default queryset
        qs = super().get_queryset(request)
        
        # Check if the user is associated with a client
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            return qs.filter(client=staff.client)
        return qs.none()
admin.site.register(Invoice, InvoiceAdmin)

class RealEstateContractAdmin(admin.ModelAdmin):
    readonly_fields =['client', 'created_by']
admin.site.register(RealEstateContract, RealEstateContractAdmin)