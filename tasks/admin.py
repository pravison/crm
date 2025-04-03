from datetime import date, timedelta
from django.contrib import admin
from django.db.models import Q
from clients.models import Client, Staff
from. models import  DailyRoutineTemplate, Journal

# Register your models here.

# class TaskAdmin(admin.ModelAdmin):
#     list_display = ['task', 'customer', 'task_date', 'done' ]
#     list_filter = ['task_date', 'task_stage', 'done' ]
#     search_fields = ['task', 'task_date']
#     list_display_links= ['task', 'task_date']
#     exclude=['user']

#     def save_model(self, request, obj, form, change):
        
#         # Save the tenant with the modified object
        
#         if change:
#             if obj.done == True:
#                 if obj.task_stage == 'reaching out':
#                     obj.customer.last_talked = date.today()
#                     obj.customer.save()
#                 elif obj.task_stage == 'follow-up':
#                     obj.customer.last_talked = date.today()
#                     obj.customer.save()
#             # get yesrtaday date 
#             yesterday= date.today() -timedelta(days=1)
#             task_due_yestarday = Task.objects.filter(user=request.user, task_date=yesterday, done=False)
#             for task in task_due_yestarday:
#                 Task.objects.create(
#                     user = task.user,
#                     task=task.task,
#                     task_stage=task.task_stage,
#                     customer=task.customer,
#                     task_date=date.today(),
#                     done=False
#                 )

#             obj.user = request.user
#             obj.save()                  
#         else:
#             if obj.customer:
#                 task = Task.objects.filter(user=request.user, customer=obj.customer, done=False).first()
#                 if task:
#                     task.user=request.user
#                     task.customer=obj.customer
#                     task.task = obj.task
#                     task.task_stage = obj.task_stage if obj.task_stage else task.task_stage
#                     task.repeat = obj.repeat if obj.repeat else task.repeat
#                     task.days_to_repeat = obj.days_to_repeat if obj.days_to_repeat else task.days_to_repeat
#                     task.task_date = obj.task_date if obj.task_date else task.task_date
#                     task.done = obj.done if obj.done else task.done

#                     task.save()
                
#                     print(obj.customer)
#             obj.user = request.user
#             obj.save()
#         # now we will handle repeating task
#         self.add_repeating_tasks(request)

#     #  function for adding tasks that are to be repeated today 
#     def add_repeating_tasks(self, request):
#         today = date.today() # getting todays date
#         weekday_name = today.strftime('%A') #getting the name of today
#         repeating_tasks = Task.objects.filter(user=request.user).exclude(Q(repeat= 'once') | Q(task_date=today) )
        
#         # we need to check all task that requires to be repeated
#         # and if any of the is to be repeated topday we add it to todays task 
#         for task in repeating_tasks:
#             # those that are set today 
#             if task.repeat == 'daily':
#                 task.task_date = today
#                 task.done= False
#                 task.save()
#             elif task.repeat == 'weekly' and weekday_name in [day for day in task.days_to_repeat]:
#                 task.task_date = today
#                 task.done= False
#                 task.save()
#             elif task.repeat == 'monthly' and task.task_date.day == today.day:
#                 task.task_date = today
#                 task.done= False
#                 task.save()
#             elif task.repeat == 'yearly' and task.task_date.month == today.month and task.task_date.day == today.day:
#                 task.task_date = today
#                 task.done= False
#                 task.save()

#     def get_queryset(self, request):
#         # default queryset
#         qs=super().get_queryset(request)
#         # if user is superuser return full queryset
#         if request.user.is_superuser:
#             return qs
#         else:
#             return qs.filter(user=request.user)
    
                
# admin.site.register(Task, TaskAdmin)

class DailyRoutineTemplateAdmin(admin.ModelAdmin):
    list_display = ['staff', 'month', 'date_updated']
    list_filter = ['date_created', 'date_updated', 'month']
    search_fields = ['month', 'staff__name', 'staff__phone_number', 'date_created']
    list_display_links= ['staff', 'month', 'date_updated']
    exclude=['user']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.staff = staff
        # Save the tenant with the modified object
        super().save_model(request, obj, form, change)   

    def get_queryset(self, request):
        # Default queryset
        qs = super().get_queryset(request)
        
        # Check if the user is associated with a client
        client = Client.objects.filter(user=request.user).first()
        staff = Staff.objects.filter(user=request.user).first()
        if client:
            return qs.filter(staff__client=client)
        elif staff:
            return qs.filter(staff=staff)
        else:
        # If neither client nor staff is found, return an empty queryset
            return qs.none()
        
admin.site.register(DailyRoutineTemplate,  DailyRoutineTemplateAdmin)


class JournalAdmin(admin.ModelAdmin):
    list_display = ['journal_name', 'Journal_summary' ,'date_updated']
    list_filter = ['date_updated', 'date_created']
    search_fields = ['Journal_summary', 'journal_name', 'staff__name', 'staff__phone_number', 'date_created', 'date_updated' ]
    list_display_links= ['Journal_summary', 'journal_name']
    exclude=['user']    

    def save_model(self, request, obj, form, change):
        staff = Staff.objects.filter(user=request.user).first()
        if staff:
            obj.staff = staff
        # Save the tenant with the modified object
        super().save_model(request, obj, form, change)   

    def get_queryset(self, request):
        # Default queryset
        qs = super().get_queryset(request)
        
        # Check if the user is associated with a client
        client = Client.objects.filter(user=request.user).first()
        staff = Staff.objects.filter(user=request.user).first()
        if client:
            return qs.filter(staff__client=client)
        elif staff:
            return qs.filter(staff=staff)
        else:
        # If neither client nor staff is found, return an empty queryset
            return qs.none()

        
admin.site.register(Journal,  JournalAdmin)