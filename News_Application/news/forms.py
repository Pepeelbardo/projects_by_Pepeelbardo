"""Forms for the news app."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Newsletter, User


class SignUpForm(UserCreationForm):
    """Public registration form. Users may sign up as a Reader or a Journalist."""

    email = forms.EmailField(required=True)
    ALLOWED_SIGNUP_ROLES = [
        (User.Role.READER, "Reader"),
        (User.Role.JOURNALIST, "Journalist"),
    ]
    role = forms.ChoiceField(choices=ALLOWED_SIGNUP_ROLES, initial=User.Role.READER)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "role"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


class ArticleForm(forms.ModelForm):
    """Form for journalists to create or edit an article."""

    class Meta:
        model = Article
        fields = ["title", "content", "publisher"]
        widgets = {"content": forms.Textarea(attrs={"rows": 10})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["publisher"].required = False
        if user is not None:
            self.fields["publisher"].queryset = user.journalist_publishers.all()


class NewsletterForm(forms.ModelForm):
    """Form for journalists/editors to create or edit a newsletter."""

    class Meta:
        model = Newsletter
        fields = ["title", "description", "articles"]
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["articles"].queryset = Article.objects.filter(approved=True)


class EmailUpdateForm(forms.ModelForm):
    """Lets a user update their own email address."""

    class Meta:
        model = User
        fields = ["email"]
