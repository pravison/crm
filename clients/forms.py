from django import forms 
from .models import Staff

class AddStaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ('name', 'role', 'phone_number')
        widgets = {
            'name' : forms.TextInput(attrs={'class': "form-control",  'id': 'name', 'placeholder':"staff Full Name"}),
            'role' : forms.TextInput(attrs={'class': "form-control", 'type':'text',  'id': 'role', 'placeholder':"staff role"}),
            'phone_number' : forms.NumberInput(attrs={'class': "form-control", 'id': 'phone_number', 'placeholder':"staff phone number"}),
			
			}