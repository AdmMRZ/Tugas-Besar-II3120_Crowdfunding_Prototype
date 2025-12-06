from django import forms
from .models import Campaign, Donation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'category', 'description', 'target_amount', 'deadline', 'image_url']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select bg-light'}),
        }

class CampaignEditForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'category', 'description', 'image_url', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'title': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control-plaintext fw-bold'}),
            'category': forms.Select(attrs={'class': 'form-select bg-light'}),
        }

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount', 'message']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 1000}),
        }
        
class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
            super(RegisterForm, self).__init__(*args, **kwargs)
            for visible in self.visible_fields():
                visible.field.widget.attrs['class'] = 'form-control bg-light border-0'
                
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-light'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-light'}),
        }