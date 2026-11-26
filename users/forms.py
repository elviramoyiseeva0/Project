from django import forms

def valide_password(val):
    if len(val) < 8:
        raise forms.ValidationError("passwd must be more than 8 char")
    
    if not any(ch.isdigit() for ch in val):
        raise forms.ValidationError("passwd must have ...")
    
    if not any(ch in "!_?" for ch in val):
        raise forms.ValidationError("use ! _ or ?")


class RegisterForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=15, required=True, label="Name")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[valide_password],
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "don't match password")
        return cleaned_data


class LoginForm(forms.Form):
    login = forms.CharField(required=True, label="Name or Email")
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "don't match password")
        return cleaned_data