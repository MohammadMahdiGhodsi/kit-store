from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import ProductComment


class CommentForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, '') for i in range(1, 6)],
        widget=forms.HiddenInput(),
        required=True,
        label='امتیاز شما'
    )

    class Meta:
        model = ProductComment
        fields = ['user_name', 'user_email', 'text', 'rating']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'comment-input',
                'placeholder': 'نام و نام خانوادگی *'
            }),
            'user_email': forms.EmailInput(attrs={
                'class': 'comment-input',
                'placeholder': 'ایمیل شما *'
            }),
            'text': forms.Textarea(attrs={
                'class': 'comment-textarea',
                'placeholder': 'نظر خود را بنویسید...',
                'rows': 4
            })
        }

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')
        if not user_name or len(user_name) < 3:
            raise ValidationError('نام باید حداقل 3 کاراکتر باشد')
        return user_name

    def clean_user_email(self):
        email = self.cleaned_data.get('user_email')
        if not email:
            raise ValidationError('ایمیل الزامی است')
        if '@' not in email and '.' not in email:
            raise ValidationError('ایمیل معتبر وارد کنید')
        return email

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text or text.strip() == '':
            raise ValidationError('متن دیدگاه نمی‌تواند خالی باشد')
        return text.strip()
