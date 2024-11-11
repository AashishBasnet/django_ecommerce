from .models import Inquiry
from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms
from .models import Profile, Inquiry


class UserInfoForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=10,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ],
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Phone'})
    )
    address1 = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Address Line 1'})
    )
    address2 = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Address Line 2'})
    )
    city = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    state = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'State'})
    )
    zipcode = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Zip Code'})
    )
    country = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Country'})
    )

    class Meta:
        model = Profile
        fields = ('phone', 'address1', 'address2',
                  'city', 'state', 'zipcode', 'country')


class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'New Password'
        self.fields['new_password1'].label = ''
        self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['new_password2'].label = ''
        self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class UpdateUserForm(UserChangeForm):
    # Hide password error
    password = None
    # other stuff
    email = forms.EmailField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email Address'}), required=False)
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}), required=False)
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}), required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email address", widget=forms.EmailInput(
        attrs={'class': 'form-control', 'id': 'email', 'required': True}))
    first_name = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'firstName', 'required': True}))
    last_name = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control',  'id': 'lastName', 'required': True}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',

            'id': 'username',
            'required': True,

        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',

            'id': 'password',
            'required': True,
            'minlength': '8'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',

            'id': 'confirmPassword',
            'required': True
        })


class InquiryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s]+$',
                message="Name can only contain letters and spaces."
            ),
            MinLengthValidator(2, "Name should be at least 2 characters long.")
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control ps-3 me-3 mb-3',
            'placeholder': 'Write Your Name Here'
        })
    )

    email = forms.EmailField(
        validators=[EmailValidator(message="Enter a valid email address.")],
        widget=forms.EmailInput(attrs={
            'class': 'form-control ps-3 mb-3',
            'placeholder': 'Write Your Email Here'
        })
    )

    phone_number = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control ps-3',
            'placeholder': 'Phone Number'
        })
    )

    subject = forms.CharField(
        max_length=150,
        validators=[MinLengthValidator(
            5, "Subject should be at least 5 characters long.")],
        widget=forms.TextInput(attrs={
            'class': 'form-control ps-3',
            'placeholder': 'Write Your Subject Here'
        })
    )

    message = forms.CharField(
        validators=[MinLengthValidator(
            10, "Message should be at least 10 characters long.")],
        widget=forms.Textarea(attrs={
            'class': 'form-control ps-3',
            'placeholder': 'Write Your Message Here',
            'style': 'height:150px;'
        })
    )

    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'phone_number', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get user from view
        super().__init__(*args, **kwargs)

        # Prepopulate fields if user is authenticated
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email
            # Prepopulate phone number if available in user profile
            if hasattr(user, 'profile') and user.profile.phone:
                self.fields['phone_number'].initial = user.profile.phone
