from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm
User = get_user_model()
class RegisterForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2",]
class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
