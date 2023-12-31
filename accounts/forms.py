from django import forms
from django.contrib.auth.models import User
from .constants import GENDER_TYPE
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import UserAccount

class UserRegistrationForm(UserCreationForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'id': 'required'}))
    last_name=forms.CharField(widget=forms.TextInput(attrs={'id': 'required'}))
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    class Meta:
        model=User
        fields=['username','first_name', 'last_name','email','birth_date', 'gender']

    def save(self, commit=True):
        our_user = super().save(commit=False) # ami database e data save korbo na ekhn
        if commit == True:
            our_user.save() # user model e data save korlam
            gender = self.cleaned_data.get('gender')
            birth_date = self.cleaned_data.get('birth_date')
 
            UserAccount.objects.create(
                user = our_user,
                gender = gender,
                birth_date =birth_date,
            )
        return our_user

class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # jodi user er account thake 
        if self.instance:
            try:
                user_account = self.instance.account
            except UserAccount.DoesNotExist:
                user_account = None


            if user_account:
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserAccount.objects.get_or_create(user=user) # jodi account thake taile seta jabe user_account ar jodi account na thake taile create hobe ar seta created er moddhe jabe


            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

        return user

class DepositForm(forms.ModelForm):
    # amount = forms.DecimalField(min_value=100, required=True, widget=forms.NumberInput())
    class Meta:
        model=UserAccount
        fields=['balance']