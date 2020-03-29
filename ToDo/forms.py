from django import forms
from django.contrib.auth.models import User

class NewTaskForm(forms.Form):
    title = forms.CharField(max_length=150)


class DueDateForm(forms.Form):
    due_date = forms.CharField(max_length=150, help_text="eg. 'tomorrow', 'today', yesterday, next week, 5")


class SubTaskForm(forms.Form):
    sub_task = forms.CharField(max_length=150)


class ToDoNotesForm(forms.Form):
    task_notes = forms.CharField(widget=forms.Textarea, help_text="Add anything that's important to the task", strip=False)


class ContactMeForm(forms.Form):
    CONTACT_CHOICES = (
        ("0", "Choose one"),
        ("1", "Account deletion"),
        ("2", "Feature request"),
        ("3", "Contribute"),
        ("4", "Say thanks")
    )

    your_email = forms.CharField(max_length=200)
    your_question_subject = forms.ChoiceField(choices=CONTACT_CHOICES)
    your_message = forms.CharField(widget=forms.Textarea)

