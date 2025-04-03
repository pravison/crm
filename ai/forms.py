from django import forms 
from customers.models import Customer, Interaction
from ai.models import TaskPipeline, Escalation, KnowledgeBase 

class AddTaskPipelineForm(forms.ModelForm):
    class Meta:
        model = TaskPipeline
        fields = ('task', 'follow_up_date', 'follow_up_time', 'for_ai_to_do',  'done')
        widgets = {
            'task' : forms.TextInput(attrs={'class': "form-control",  'id': 'task', 'placeholder':"task"}),
            'follow_up_date' : forms.DateInput(attrs={'class': "form-control", 'type':'date',  'id': 'follow_up_date', 'placeholder':"Date to be done"}),
            'follow_up_time' : forms.TimeInput(attrs={'class': "form-control", 'type':'time',  'id': 'follow_up_time', 'placeholder':"time to be done "}), 
            'for_ai_to_do': forms.CheckboxInput(attrs={'id': 'for_ai_to_do', 'placeholder':"uncheck if you dont want AI to do the task "} ),
            'done': forms.CheckboxInput(attrs={'id': 'done', 'placeholder':"check if task is already commpleted"}  ),
			
			}
        
class AddKnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBase
        fields = ('title', 'web_url', 'api_url', 'api_token', 'file', 'description')
        widgets = {
            'title' : forms.TextInput(attrs={'class': "form-control",  'id': 'title', 'placeholder':"title helps"}),
            'web_url' : forms.URLInput(attrs={'class': "form-control", 'type':'url',  'id': 'web_url', 'placeholder':"(optional) enter website url if exist"}),
            'api_url' : forms.URLInput(attrs={'class': "form-control", 'type':'url',  'id': 'api_url', 'placeholder':"(optional) if you want us to access your data through API write here  "}), 
            'api_token': forms.TextInput(attrs={'class': "form-control", 'id': 'api_token', 'placeholder':"(optional) provide auth token if your API require one to access data "} ),
            'file': forms.FileInput(attrs={'class': "form-control", 'id': 'file', 'placeholder':"(optional) provide pdf or documents  "}  ),
            'description' : forms.Textarea(attrs={'class': "form-control",  'id': 'description', 'placeholder':"write a summary description of the provided information"}),
			
			}