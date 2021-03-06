from django import forms
from clamopener.clamusers.models import CLAMUsers, PendingUsers
from django.core.validators import validate_email
from clamopener import settings

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

def pwhash(user, password):
    #computes a password hash for a given user and plaintext password
    if not isinstance(user, bytes):
        user = user.encode('utf-8')
    if not isinstance(password, bytes):
        password = password.encode('utf-8')
    return md5(user + b':' + settings.REALM.encode('utf-8') + b':' + password).hexdigest()

class RegisterForm(forms.ModelForm):
    mail = forms.EmailField( label='E-Mail',max_length = 255 ,required=True)
    password2 = forms.CharField(label="Password (again)",  widget=forms.PasswordInput, max_length = 60, required=True )

    class Meta:
        model = PendingUsers
        fields = ('username', 'fullname', 'institution','mail','password')
        widgets = {
            'password': forms.PasswordInput,
            'password2': forms.PasswordInput,
        }



    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        username = cleaned_data['username']

        for c in (' ','&','?','<','>','/',';','`','\\','\t','\n','\r','\b'):
            if c in username:
                raise forms.ValidationError("Username contains illegal character (" + c + ")" )

        if password != password2:
            raise forms.ValidationError("Passwords don't match")

        #hash the passwords
        cleaned_data['password'] = pwhash(username,password)

        # Always return the full collection of cleaned data.
        return cleaned_data


#class RegisterForm(forms.Form):
    #username = forms.CharField(label="Username", max_length = 60, required=True)
    #password = forms.CharField(label="Password", widget=forms.PasswordInput, max_length = 60, required=True )
    #password2 = forms.CharField(label="Password (again)",  widget=forms.PasswordInput, max_length = 60, required=True )
    #fullname = forms.CharField(label="Full name" max_length = 255, required=True )
    #institution = forms.CharField(label="Institution", max_length = 255 )
    #mail = forms.EmailField(label="E-mail", max_length = 255, required=True )
