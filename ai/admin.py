from django.contrib import admin
from .models import AI_Agent, TaskPipeline, Escalation,  SalesFunnelStageInstruction, Whatsapp, AiReport, KnowledgeBase
from clients.models import Client, Staff

# Register your models here.
class AI_AgentAdmin(admin.ModelAdmin):
    list_display = ['agent_name']
    search_fields =['agent_name']
    list_display_links= ['agent_name']
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
admin.site.register(AI_Agent, AI_AgentAdmin)

class TaskPipelineAdmin(admin.ModelAdmin):
    list_display = ['customer', 'task', 'staff', 'follow_up_date' ]
    list_filter = [ 'done', 'for_ai_to_do', 'follow_up_date', 'follow_up_time'] 
    search_fields = ['customer__name', 'customer__phone_number', 'customer__email',  'task', 'staff__name', 'staff__phone_number', 'follow_up_date' ]
    list_display_links= ['customer', 'task', 'staff', 'follow_up_date' ]
    exclude=['client']    

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
    
admin.site.register(TaskPipeline, TaskPipelineAdmin)

class EscalationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date', 'staff', 'done' ]
    list_filter = [ 'done', 'date' ] 
    search_fields = ['customer__name', 'customer__phone_number', 'customer__email', 'staff__name', 'staff__phone_number', 'date', 'reasons']
    list_display_links= ['customer', 'date', 'staff', 'done' ]
    exclude=['client'] 

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
    
admin.site.register(Escalation, EscalationAdmin)


class SalesFunnelStageInstructionAdmin(admin.ModelAdmin):
    list_display = ['funnel_stage', 'days_to_follow_up' ]
    list_filter = ['funnel_stage']
    search_fields = ['funnel_stage', 'days_to_follow_up', 'instructions' ]
    list_display_links= ['funnel_stage', 'days_to_follow_up' ]
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
admin.site.register(SalesFunnelStageInstruction, SalesFunnelStageInstructionAdmin)

class WhatsappAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_number', 'whatsapp_phone_number_id' ]
    search_fields = ['whatsapp_number', 'whatsapp_phone_number_id' ]
    list_display_links= ['whatsapp_number', 'whatsapp_phone_number_id' ]
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
admin.site.register(Whatsapp, WhatsappAdmin)


class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'description', 'web_url', 'api_url' ]
    list_display_links= ['title']
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
admin.site.register(KnowledgeBase, KnowledgeBaseAdmin)



class AiReportAdmin(admin.ModelAdmin):
    list_display = ['ai', 'send', 'last_updated']
    list_filter = ['send', 'last_updated']
    search_fields = ['ai__agent_name', 'send', 'last_updated']
    list_display_links= ['ai', 'send', 'last_updated']
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
admin.site.register(AiReport, AiReportAdmin)

