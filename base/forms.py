from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserCreationForm(UserCreationForm):
    class Meta:
        model = Investor
        fields = ['identity_fin', 'contact_num', 'full_name', 'username', 'password1', 'password2']