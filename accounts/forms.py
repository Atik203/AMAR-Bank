from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .constants import ACCOUNT_TYPE, GENDER_TYPE
from .models import UserAddress, UserBankAccount


class RegistrationForm(UserCreationForm):
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE,widget=forms.Select(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE,widget=forms.Select(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
    
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['password1'].help_text=None
      self.fields['password2'].help_text=None
      for field in self.fields:
                self.fields[field].widget.attrs.update({
                    'class': (
                        'appearance-none block w-full bg-gray-200 '
                        'text-gray-700 border border-gray-200 rounded '
                        'py-3 px-4 leading-tight focus:outline-none '
                        'focus:bg-white focus:border-gray-500'
                    ) 
                })
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email','account_type','birthday','gender','city','state','country','zip_code','address']
        
        help_texts = {
            'username': None,
        }
        
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=True)
        
        if commit:
            user.save()
            account_type = self.cleaned_data.get('account_type')
            birthday = self.cleaned_data.get('birthday')
            gender = self.cleaned_data.get('gender')
            city = self.cleaned_data.get('city')
            state = self.cleaned_data.get('state')
            country = self.cleaned_data.get('country')
            zip_code = self.cleaned_data.get('zip_code')
            address = self.cleaned_data.get('address')
            account_number = 10000+user.id
            
            UserAddress.objects.create(user=user,address=address,city=city,state=state,country=country,zip_code=zip_code)
            UserBankAccount.objects.create(user=user,account_type=account_type,birthday=birthday,account_number=account_number,gender = gender)
            
        return user



class UserUpdateForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE,widget=forms.Select(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE,widget=forms.Select(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
                  
    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email']
        
        help_texts = {
            'username': None,
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    'class': (
                        'appearance-none block w-full bg-gray-200 '
                        'text-gray-700 border border-gray-200 rounded '
                        'py-3 px-4 leading-tight focus:outline-none '
                        'focus:bg-white focus:border-gray-500'
                    ) 
                })
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address   
            except:
                user_account = None
                user_address = None
            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['birthday'].initial = user_account.birthday
                self.fields['gender'].initial   = user_account.gender
                self.fields['birthday'].initial = user_account.birthday
                self.fields['city'].initial = user_address.city
                self.fields['state'].initial = user_address.state
                self.fields['country'].initial = user_address.country
                self.fields['zip_code'].initial = user_address.zip_code
                self.fields['address'].initial = user_address.address              
  
        
    def save(self, commit=True):
        user = super().save(commit=True)
        
        if commit:
            user.save()
            user_account, created = UserBankAccount.objects.get_or_create(user=user)
            user_address, created = UserAddress.objects.get_or_create(user=user)
            
            user_account.account_type = self.cleaned_data.get('account_type')
            user_account.birthday = self.cleaned_data.get('birthday')
            user_account.gender = self.cleaned_data.get('gender')
            user_account.save()
            
            user_address.city = self.cleaned_data.get('city')
            user_address.state = self.cleaned_data.get('state')
            user_address.country = self.cleaned_data.get('country')
            user_address.zip_code = self.cleaned_data.get('zip_code')
            user_address.address = self.cleaned_data.get('address')
            user_address.save()
            
        return user