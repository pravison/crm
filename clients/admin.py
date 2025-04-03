from django.contrib import admin
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Client, Staff, FAQ, Industry

# User = get_user_model()

class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'business_name', 'phone_number', 'location']
    list_filter = ['created_on']
    search_fields = ['client_name', 'business_name', 'phone_number', 'location']
    list_display_links= ['client_name', 'business_name', 'phone_number', 'location']
    exclude=['user']    

    def save_model(self, request, obj, form, change):
        # Save the tenant with the modified object
        super().save_model(request, obj, form, change)   

    def get_queryset(self, request):
        # Default queryset
        qs = super().get_queryset(request)
        
        # Check if the user is associated with a client
        clients = Client.objects.filter(user=request.user)
        staff = Staff.objects.filter(user=request.user).first()
        if clients:
            return qs.filter(user=request.user)
        
        elif staff:
            return qs.filter(id=staff.client.id)
        else:
        # If neither client nor staff is found, return an empty queryset
            return qs.none()            
admin.site.register(Client, ClientAdmin)


class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'phone_number', 'client__business_name']
    list_filter = ['date_joined']
    search_fields = ['name', 'role', 'phone_number', 'client__business_name', 'date_joined']
    list_display_links= ['name', 'role', 'phone_number', 'client__business_name']
    exclude=['client', 'user']    

    def get_queryset(self, request):
        # Default queryset
        qs = super().get_queryset(request)

        # Get all client accounts associated with the logged-in user
        clients = Client.objects.filter(user=request.user)
        staff = Staff.objects.filter(user=request.user).first()
        if clients.exists():
            # If the user owns one or more client accounts, show all staff across these accounts
            return qs.filter(client__in=clients)
        
        # Check if the user is a staff member
        
        elif staff:
            # If user is staff, show only staff within the same client account
            return qs.filter(user=request.user)
        
        # If neither client owner nor staff, return an empty queryset
        else:
            return qs.none()
admin.site.register(Staff, StaffAdmin)

class FAQAdmin(admin.ModelAdmin):
    list_display = ['question']
    search_fields = ['question', 'answer']
    list_display_links= ['question']
admin.site.register(FAQ, FAQAdmin)

admin.site.register(Industry)