from django import forms

from .models import Board


class BoardForm(forms.ModelForm):
    """Form for creating and editing a Board."""

    class Meta:
        model = Board
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Например: Идеи для дизайна",
                    "maxlength": 120,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "placeholder": "О чём эта доска? (необязательно)",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "title": "Название доски",
            "description": "Описание",
        }


class SavePinToBoardForm(forms.Form):
    """Form for saving a Pin to one of the user's or guest's boards."""

    board = forms.ModelChoiceField(
        queryset=Board.objects.none(),
        label="Выберите доску",
        empty_label="— Выберите доску —",
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    def __init__(self, *args, boards_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if boards_queryset is not None:
            self.fields["board"].queryset = boards_queryset
