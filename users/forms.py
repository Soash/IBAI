from django import forms
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'email', 'phone_number', 'user_type',
            'designation', 'university_name', 'session',
            'bio', 'profile_picture', 'facebook_link', 'linkedin_link', 'website'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add CSS classes to all fields
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'common__login__input'



