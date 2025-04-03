from django import forms 
from clients.models import Client, Staff
from customers.models import Customer, Interaction
from ai.models import TaskPipeline, Escalation
from django.db.models import  Q
class AddCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('name', 'phone_number', 'email', 'niche', 'funnel_stage',  'description', 'last_interaction_summary', 'refferal_source')
        widgets = {
            'name' : forms.TextInput(attrs={'class': "form-control",  'id': 'name', 'placeholder':"Customer Full names"}),
            'phone_number' : forms.NumberInput(attrs={'class': "form-control",  'id': 'phone_number', 'placeholder':"use this format ex. 254740562740"}),
            'email' : forms.EmailInput(attrs={'class': "form-control",  'id': 'email', 'placeholder':"(optional) cutomer email"}), 
            'niche': forms.Select(attrs={'class': "form-control",  'id': 'niche', 'placeholder':"(optional) Customer Niche Segment"} ),
            'funnel_stage': forms.Select(attrs={'class': "form-control",  'id': 'funnel_stage', 'placeholder':"Customer funnel Stage"}  ),  
            'description' : forms.Textarea(attrs={'class': "form-control",  'id': 'description', 'placeholder':"(optional) describe your customer"}),
            'last_interaction_summary' : forms.Textarea(attrs={'class': "form-control",  'id': 'last_interaction_summary', 'placeholder':"(optional) summary of your last interaction if had one"}),  
            'refferal_source': forms.Select(attrs={'class': "form-control",  'id': 'refferal_source', 'placeholder':"refferal source"} ),
			
			}
    

class AddInteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = (
            'customer',
            'interaction_place',
            'customer_sales_funnel_stage',
            'conversation_summary',
            'next_step',
            'next_step_date',
        )
        widgets = {
            'interaction_place': forms.Select(attrs={'class': "form-control", 'id': 'interaction_place'}),
            'customer_sales_funnel_stage': forms.Select(attrs={'class': "form-control", 'id': 'customer_sales_funnel_stage'}),
            'conversation_summary': forms.Textarea(attrs={'class': "form-control", 'id': 'conversation_summary'}),
            'next_step': forms.TextInput(attrs={'class': "form-control", 'id': 'next_step'}),
            'next_step_date': forms.DateInput(attrs={'class': "form-control", 'id': 'next_step_date', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Retrieve custom arguments
        customer = kwargs.pop('customer', None)
        # request = kwargs.pop('request', None)
        
        # Call the parent constructor once
        super().__init__(*args, **kwargs)

        # Limit the customer queryset based on the request user
        # if request:
        #     staff = Staff.objects.filter(user=request.user).first()
        #     if staff:
        #         self.fields['customer'].queryset = Customer.objects.filter(client=staff.client)
        
        # Set initial value for the customer field if provided
        if customer:
            self.fields['customer'].initial = customer
            self.fields['customer'].widget.attrs['disabled'] = True  # Disable the dropdown
            self.fields['customer'].widget.attrs['class'] = "form-control"

    

class AddTaskPipelineForm(forms.ModelForm):
    class Meta:
        model = TaskPipeline
        fields = ('customer', 'task', 'follow_up_date', 'follow_up_time')
        widgets = {
            'task': forms.Textarea(attrs={'class': "form-control",  'id': 'task'} ), 
            'follow_up_date' : forms.DateInput(attrs={'class': "form-control",  'id': 'follow_up_date', 'type': 'date'}), 
            'follow_up_time' : forms.TimeInput(attrs={'class': "form-control",  'id': 'follow_up_time', 'type': 'time'})
			
			}
        
    def __init__(self, *args, **kwargs):
        # retrieve customer passed in an argument
        customer = kwargs.pop('customer', None)
        super(AddTaskPipelineForm, self).__init__( *args, **kwargs)
        
        # if customer exists
        if customer:
            self.fields['customer'].initial = customer
            self.fields['customer'].widget.attrs['readonly'] = True
        
class EditEscaltion(forms.ModelForm):
    class Meta:
        model = Escalation
        fields = ('customer', 'reasons',  'done')
        widgets = {
            'customer': forms.TextInput(attrs={'class': "form-control",  'id': 'customer'}),
            'reasons': forms.Textarea(attrs={'class': "form-control",  'id': 'reasons'} ), 
            # 'date' : forms.DateInput(attrs={'class': "form-control",  'id': 'date'}),
            'done' : forms.CheckboxInput(attrs={'id': 'one'})
			
			}
        def __init__(self, *args, **kwargs):
            super(EditEscaltion, self).__init__(*args, **kwargs)
            # Make the 'date' field read-only
            self.fields['customer'].widget.attrs['readonly'] = True
            # self.fields['date'].widget.attrs['readonly'] = True
    