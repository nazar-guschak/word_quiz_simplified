from django import forms
from django.forms import modelformset_factory, RadioSelect
from .models import Word


class AddWordForm(forms.ModelForm):
    class Meta:
     model = Word
     fields = ['word', 'translation']

     widgets = {
         'word': forms.TextInput(attrs={
             'placeholder': 'Оригінал',
             'class': 'input-field'
         }),
         'translation': forms.TextInput(attrs={
             'placeholder': 'Переклад',
             'class': 'input-field'
         }),
     }

WordFormSet = modelformset_factory(Word, form=AddWordForm, extra=10)


class QuizForm(forms.Form):

    def __init__(self, *args, words=None, choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.question_choices = {}

        for i, word in enumerate(words):
            self.fields[f"word_{word.id}"] = forms.ChoiceField(
                choices = choices[i],
                widget=forms.RadioSelect,
                label=word.word
            )

            self.question_choices[f"word_{word.id}"] = [c[0] for c in choices[i]]


