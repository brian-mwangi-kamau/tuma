from django import  forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
class SignupForm(UserCreationForm):
    email = forms.EmailField()

    class Meta():
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

class MoneyTransferForm(forms.Form):
    account_number = forms.CharField(max_length=8)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

class ListCharity(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    photo = forms.ImageField()
    goal_amount = forms.IntegerField(initial=0)