from django import forms

class NewTaskForm(forms.Form):
    title = forms.CharField(max_length=150)