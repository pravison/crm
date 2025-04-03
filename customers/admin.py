from django.contrib import admin
from datetime import  date, timedelta
from ai.models import TaskPipeline
from business.functions import follow_up_immediately
from clients.models import Client, Staff
from . models import Customer, Conversation, CustomerHistory,  Interaction, CustomerNicheSegment, CustomerMessage, Comment, Testimonial, NewsletterSubscription

# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'funnel_stage' ]
    list_filter = ['funnel_stage', 'date_added', 'last_talked' ] 
    search_fields = ['client__business_name', 'name', 'phone_number', 'funnel_stage', 'description']
    list_display_links= ['name', 'phone_number', 'funnel_stage' ]
    exclude=['client']

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
        super().save_model(request, obj, form, change)
        # check if any task that is not done  and is accociated with customer instance 
        # task = Task.objects.filter(customer=obj.customer, user=request.user, done=False).first()
        today = date.today()
        tommorow = today + timedelta(days=1)
        after_tommorow = today + timedelta(days=2)
        after_two_days = today + timedelta(days=3)
        if change:
            customer = Customer.objects.filter(id=obj.id).first()
            # customer_added = customer.date_added.date()
            tasks = TaskPipeline.objects.filter(customer=customer).count()
            if tasks < 2:
                fromId=obj.phone_number
                follow_up_immediately(staff.client, fromId)
                TaskPipeline.objects.create(
                    customer=obj,
                    client = staff.client,
                    staff = staff,
                    task = """Draft a follow-up message after one  day """,
                    follow_up_date =  tommorow
                )
                TaskPipeline.objects.create(
                    customer=obj,
                    client = staff.client,
                    staff = staff,
                    task = """Draft a follow-up message after two  days """,
                    follow_up_date =  after_tommorow
                )
                TaskPipeline.objects.create(
                    client = staff.client,
                    staff = staff,
                    customer=obj,
                    task = """Draft a follow-up message after three  days """,
                    follow_up_date =  after_two_days
                )
        
        else:
            fromId=obj.phone_number
            follow_up_immediately(staff.client, fromId)
            TaskPipeline.objects.create(
                client = staff.client,
                staff = staff,
                    customer=obj,
                    task = """Draft a follow-up message after one  days """,
                    follow_up_date =  tommorow
                )
            TaskPipeline.objects.create(
                client = staff.client,
                staff = staff,
                customer=obj,
                task = """Draft a follow-up message after two  days """,
                follow_up_date =  after_tommorow
                )
            TaskPipeline.objects.create(
                    client = staff.client,
                    staff = staff,
                    customer=obj,
                    task = """Draft a follow-up message after three  days """,
                    follow_up_date =  after_two_days
                )

        # obj.save()  # Ensure obj is saved after making changes
        # Save  the modified object

    def get_queryset(self, request):
        # Default queryset
        qs = super().get_queryset(request)
        
        # Check if the user is associated with a client
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            return qs.filter(client=staff.client)
        return qs.none()   
admin.site.register(Customer, CustomerAdmin)


class ConversationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'sender', 'date_added', 'read']
    list_filter = ['sender', 'read', 'date_added']
    search_fields = ['staff__name', 'client__business_name', 'customer', 'sender', 'date_added', 'read', 'message']
    list_display_links= ['customer', 'sender', 'date_added', 'read']
    exclude=['client', 'staff']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
            obj.staff = staff
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
admin.site.register(Conversation, ConversationAdmin)


class CustomerHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'history_status', 'date']
    list_filter = ['history_status', 'date']
    search_fields = ['client__business_name', 'customer', 'product', 'history_status', 'date']
    list_display_links= ['customer', 'product', 'history_status', 'date']
    exclude=['client']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
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
admin.site.register(CustomerHistory, CustomerHistoryAdmin)


# my assumption is if you add an interaction you neeed to send customer amessage thanking him or her for the ooportunity
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'next_step', 'next_step_date' ]
    list_filter = ['customer','date_created' ] 
    search_fields = ['client__client_name', 'client__business_name', 'conversation_summary', 'next_step', 'next_step_date']
    list_display_links= ['customer', 'next_step', 'next_step_date' ]
    exclude=['client', 'staff']
    

    def save_model(self, request, obj, form, change):

        if not change:
            staff = Staff.objects.filter(user=request.user).first()
            if staff:
                obj.client = staff.client
                obj.staff = staff
            # my assumption is if you add an interaction you neeed to send customer amessage thanking him or her for the ooportunity
            fromId=obj.customer.phone_number
            follow_up_immediately(staff.client, fromId)
        # check if any task that is nit done is accociated with customer instance 
        tasks = TaskPipeline.objects.filter(customer=obj.customer, done=False)
        # if we update the task 
        if tasks:
            for task in tasks:
                if task.task == obj.next_step:
                    task.follow_up_date = obj.next_step_date
                    task.save()
            
        else :# if not we add a new task
            TaskPipeline.objects.create(
                task = obj.next_step,
                customer =  obj.customer,
                follow_up_date = obj.next_step_date
            )

        #  updating customer sales field 

        if not obj.customer_sales_funnel_stage:
            pass
        else:
            customer = obj.customer
            customer.funnel_stage = obj.customer_sales_funnel_stage
            customer.save()

        # obj.save()  # Ensure obj is saved after making changes
        # Save  the modified object
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Default queryset
        qs = super().get_queryset(request)
        
        # Check if the user is associated with a client
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            return qs.filter(client=staff.client)
        return qs.none()       
admin.site.register(Interaction, InteractionAdmin)

class CustomerNicheSegmentAdmin(admin.ModelAdmin):
    list_display = ['segment']
    search_fields = ['client__business_name', 'segment', 'outreach_message']
    list_display_links= ['segment']
    exclude=['client']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
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
admin.site.register(CustomerNicheSegment, CustomerNicheSegmentAdmin)


class CustomerMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email', 'replied']
    list_filter = ['replied', 'date_sent']
    search_fields = ['client__client_name', 'client__business_name', 'name', 'phone_number', 'email', 'replied']
    list_display_links= ['name', 'phone_number', 'email', 'replied']
    exclude=['client']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
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
admin.site.register(CustomerMessage, CustomerMessageAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['customer_name',  'email', 'product']
    list_filter = ['useful', 'date']
    search_fields = ['client__client_name', 'client__business_name', 'customer_name',  'email', 'product', 'message']
    list_display_links= ['customer_name',  'email', 'product']
    exclude=['client']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
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
admin.site.register(Comment, CommentAdmin)


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'product', 'number_of_stars']
    list_filter = ['approved', 'number_of_stars', 'date_created']
    search_fields = ['client__client_name', 'client__business_name', 'customer_name', 'product', 'number_of_stars', 'message']
    list_display_links= ['customer_name', 'product', 'number_of_stars']
    exclude=['client']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
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
admin.site.register(Testimonial, TestimonialAdmin)

class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'whatsapp_number', 'email']
    search_fields = ['client__client_name', 'client__business_name', 'customer_name', 'whatsapp_number', 'email']
    list_display_links= ['customer_name', 'whatsapp_number', 'email']
    exclude=['client']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.client = staff.client
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
admin.site.register(NewsletterSubscription, NewsletterSubscriptionAdmin)