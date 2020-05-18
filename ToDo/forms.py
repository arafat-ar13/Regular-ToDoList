from django import forms
from django.contrib.auth.models import User

from .models import Attachments


class NewTaskListForm(forms.Form):
    title = forms.CharField(
        help_text="eg. Shopping, Movies to watch, Homework")


class NewTaskForm(forms.Form):
    title = forms.CharField(
        help_text="We'll get there, add a task for now", max_length=70)
    title.widget = forms.TextInput(attrs={'id': 'input-todo'})


class DueDateForm(forms.Form):
    due_date = forms.CharField(
        max_length=20, help_text="eg. 'tomorrow', 'today', yesterday, next week, 5")
    due_date.widget = forms.TextInput(attrs={"id": "input-due-date"})


class SubTaskForm(forms.Form):
    sub_task = forms.CharField(max_length=70)
    sub_task.widget = forms.TextInput(attrs={"id": "input-subtask"})


class ToDoNotesForm(forms.Form):
    task_notes = forms.CharField(widget=forms.Textarea(
        attrs={"id": "input-notes"}), help_text="Add anything that's important to the task", strip=False)


class SearchForm(forms.Form):
    query = forms.CharField(max_length=65, help_text="Search everything")


class TaskAttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachments
        fields = ["content"]


class ContactMeForm(forms.Form):
    CONTACT_CHOICES = (
        ("0", "Choose one"),
        ("1", "Account deletion"),
        ("2", "Feature request"),
        ("3", "Contribute"),
        ("4", "Say thanks")
    )

    your_email = forms.CharField(max_length=100)
    your_question_subject = forms.ChoiceField(choices=CONTACT_CHOICES)
    your_message = forms.CharField(widget=forms.Textarea)
