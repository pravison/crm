from django.db import models
from tinymce.models import HTMLField
from customers.models import Customer
from clients.models import Client, Staff

# Create your models here.

    
class AI_Agent(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='agents')
    agent_name = models.CharField(max_length=100)
    response_message = models.TextField(max_length=300, blank=True, help_text='this is a message send to a customer immediately is added to the database')
    follow_up_notification = models.BooleanField(default=True, help_text='will be notified everytime ai follows up with a customer')
    respond_notification = models.BooleanField(default=True, help_text='will be notified everytime ai responds to a customer')
    escalation_notification = models.BooleanField(default=True, help_text='will be notified everytime ai escalates a customers issue')
    midday_report_notification = models.BooleanField(default=True, help_text='Ai will notify you about its work everyday before midday')
    evening_report_notification = models.BooleanField(default=True, help_text='Ai will notify you about its work everyday evening')
    staff_to_notify = models.ManyToManyField(Staff, blank=True, related_name='agents', help_text='these are the staff that will be receiving notifications only two allowed')
   

    def __str__(self):
        return self.agent_name


class Whatsapp(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='whatsapps')
    whatsapp_number = models.CharField(max_length=20)
    whatsapp_phone_number_id= models.CharField(max_length=100)
    whatsapp_verify_token = models.CharField(max_length=200)
    whatsapp_auth_token = models.CharField(max_length=500)
    
    def __str__(self):
        return self.whatsapp_number


    
class KnowledgeBase(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='knowledgebases')
    title = models.CharField(max_length=299)
    web_url = models.URLField(null=True, blank=True)
    description = HTMLField(blank=True)
    api_url = models.URLField(null=True, blank=True)
    api_token =models.CharField(max_length=700, null=True, blank=True)
    file = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.title[:150]


class SalesFunnelStageInstruction(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='instructions')
    funnel_stage = models.CharField(max_length=50, choices=(('awareness', 'awareness'), ('interest', 'interest'),('decision', 'decision'), ('purchase', 'purchase'), ('active', 'active'), ('dormant', 'dormant')))
    days_to_follow_up = models.IntegerField(null=True, blank=True, help_text='follow up after how many days from the last interaction')
    instructions = HTMLField(max_length=500, help_text="write you sales SOP'S depending on the funnel stage you choose. provide instructions to all the above stages")   
    def __str__(self):
        return self.funnel_stage
    
class TaskPipeline(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='pipelines')
    staff = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL, related_name='pipelines')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    task = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_time = models.TimeField(blank=True, null=True)
    for_ai_to_do = models.BooleanField(default=True, help_text="if false human will have to do the task and not ai and vice versa")
    done = models.BooleanField(default=False)
    def __str__(self):
        return self.customer.phone_number
    
class Escalation(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='escalations')
    staff = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL, related_name='escalations')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    reasons = HTMLField(blank=True, null=True)
    date = models.DateField(auto_now_add=True, editable=True)
    done = models.BooleanField(default=False)
    def __str__(self):
        return self.customer.phone_number
    
class AiReport(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')
    ai = models.ForeignKey(AI_Agent, null=True, blank=True, on_delete=models.SET_NULL)
    send = models.BooleanField(default=False)
    last_updated = models.DateField(auto_now=True)

    def __str__(self): 
        return str(self.last_updated)