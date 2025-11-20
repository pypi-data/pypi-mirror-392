from django import forms
from django.utils.translation import gettext_lazy as _


class AdminTrapForm(forms.Form):
    """
    Fake admin login form - no validation, always fails
    """

    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control"}),
        label=_("Username"),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label=_("Password"),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        # Always raise validation error to mimic failed login
        raise forms.ValidationError(
            _(
                "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
            ),
            code="invalid_login",
        )
