from django.db import models
# from multiselectfield import MultiSelectField
# from customers.models import Customer
from clients.models import  Staff
from tinymce.models import HTMLField

# Create your models here.
# class Task(models.Model):
#     client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL, related_name='tasks')
#     staff = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL, related_name='tasks')
#     task = models.TextField(max_length=500)
#     task_stage = models.CharField(max_length=100,  blank=True, null=True, choices=(('lead capturing', 'lead capturing'), ('finding out more', 'finding out more'),('training', 'training'), ('reaching out', 'reaching out'), ('follow-up', 'follow-up'), ('sales presentation', 'sales presentation'), ('sales closing', 'sales closing'), ('upsell', 'upsell')))
#     customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, blank=True)
#     repeat = models.CharField(max_length=100,  default='once', choices=(('once', 'once'), ('daily', 'daily'), ('weekly', 'weekly'), ('monthly', 'monthly'), ('yearly', 'yearly')))
#     days_to_repeat = MultiSelectField(blank=True, null=True, choices=(('Monday', 'Monday'), ('Tuesday', 'Tuesday'),('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')))
#     task_outcome_summary = HTMLField(blank=True)
#     task_date = models.DateField(help_text='if selected repeat choose start date')
#     done = models.BooleanField(default=False)

#     def __str__(self):
#         return self.task

        
class FollowUp(models.Model):
    staff = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL, related_name='follow_ups')
    last_updated = models.DateField(auto_now=True)

    def __str__(self): 
        return str(self.last_updated)

class DailyRoutineTemplate(models.Model):
    staff = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL, related_name='routines')
    month = models.CharField(max_length=100, choices=(('january', 'january'), ('february', 'february'),('march', 'march'), ('april', 'april'), ('may', 'may'), ('june', 'june'), ('july', 'july'),('august', 'august'), ('september', 'september'), ('october', 'october'), ('november', 'november'), ('december', 'december')))
    daily_routine_template = HTMLField(max_length=2000)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.month
    
class Journal(models.Model):
    staff = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL, related_name='journals')
    journal_name = models.CharField(max_length=100, blank=True, null=True)
    Journal_summary = HTMLField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Journal_summary[:100] +('...' if len(self.Journal_summary) > 100 else '')