from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Image, Comment, UserProfile
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
            self.fields['bio'].initial = self.user.profile.bio

        # Update avatar field with better validation
        self.fields['avatar'] = forms.ImageField(
            required=False,
            widget=forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/gif'
            }),
            validators=[
                FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
            ]
        )

    def clean(self):
        cleaned_data = super().clean()
        
        # Handle avatar validation
        avatar = self.files.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:  # 5MB limit
                self.add_error('avatar', _('File size must be under 5MB.'))
            
            # Check content type
            content_type = avatar.content_type
            if content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                self.add_error('avatar', _('File must be a valid image (JPG, PNG, or GIF).'))

        # Handle password change
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if any([current_password, new_password, confirm_password]):
            if not all([current_password, new_password, confirm_password]):
                self.add_error(None, _('All password fields must be filled to change password.'))
            elif not self.user.check_password(current_password):
                self.add_error('current_password', _('Current password is incorrect.'))
            elif new_password != confirm_password:
                self.add_error('confirm_password', _('New passwords do not match.'))
            elif len(new_password) < 8:
                self.add_error('new_password', _('Password must be at least 8 characters long.'))

        return cleaned_data

    def save(self, commit=True):
        # Get the user profile instance
        profile = self.user.profile
        
        # Update user information
        self.user.username = self.cleaned_data['username']
        self.user.email = self.cleaned_data['email']
        
        if self.cleaned_data.get('new_password'):
            self.user.set_password(self.cleaned_data['new_password'])
        
        self.user.save()
        
        # Update profile information
        profile.bio = self.cleaned_data.get('bio', '')
        
        # Handle avatar upload
        if 'avatar' in self.files:
            profile.avatar = self.files['avatar']
        
        if commit:
            profile.save()
        
        return profile

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        } 