from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

INPUT_CLASSES = (
    'w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 '
    'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 '
    'placeholder-gray-400 dark:placeholder-gray-500 '
    'focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent '
    'transition text-sm'
)


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name',
            'class': INPUT_CLASSES,
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': INPUT_CLASSES,
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'class': INPUT_CLASSES,
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': INPUT_CLASSES,
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # use email as username
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': INPUT_CLASSES,
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': INPUT_CLASSES,
        })
    )


class ProfileSetupForm(forms.ModelForm):
    """
    Shown after registration to complete the profile.
    """
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': INPUT_CLASSES,
        })
    )

    class Meta:
        model = User
        fields = [
            'date_of_birth', 'sex', 'weight_kg',
            'height_cm', 'activity_level', 'goal',
            'has_diabetes', 'has_hypertension',
            'has_obesity', 'is_pregnant',
        ]
        widgets = {
            'sex': forms.Select(attrs={'class': INPUT_CLASSES}),
            'weight_kg': forms.NumberInput(attrs={
                'placeholder': 'e.g. 70',
                'class': INPUT_CLASSES,
                'step': '0.1',
            }),
            'height_cm': forms.NumberInput(attrs={
                'placeholder': 'e.g. 170',
                'class': INPUT_CLASSES,
            }),
            'activity_level': forms.Select(attrs={'class': INPUT_CLASSES}),
            'goal': forms.Select(attrs={'class': INPUT_CLASSES}),
        }