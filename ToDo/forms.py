from django import forms

class NewTaskForm(forms.Form):
    title = forms.CharField(max_length=150)


class DueDateForm(forms.Form):
    due_date = forms.CharField(max_length=150, help_text="eg. 'tomorrow', 'today', 5, 13")