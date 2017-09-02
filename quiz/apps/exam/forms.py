"""Exam app forms"""

from django import forms

from .models import Option


class RadioQuestionForm(forms.Form):
    """Form for question with radio options"""

    RADIO_OPTIONS = 'radio_options'

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)

        options = tuple(
            (option.id, option.option_text)
            for option in question.get_options()
        )

        self.fields[self.RADIO_OPTIONS] = forms.ChoiceField(
            label=question.question_text,
            widget=forms.RadioSelect,
            choices=options,
        )

    def get_chosen_option(self):
        """Get chosen option object"""
        answer = self.cleaned_data[self.RADIO_OPTIONS]
        # AFAIU there should not be a KeyError
        answer = Option.objects.get(pk=answer)  # might make sense to hide
        # all django orm related stuff in models
        return answer
