from django import forms

class NewTaskForm(forms.Form):
    title = forms.CharField(max_length=150)


class DueDateForm(forms.Form):
    due_date = forms.CharField(max_length=150, help_text="eg. 'tomorrow', 'today', yesterday, next week, 5")


class SubTaskForm(forms.Form):
    sub_task = forms.CharField(max_length=150)


class ToDoNotesForm(forms.Form):
    task_notes = forms.CharField(widget=forms.Textarea, help_text="Add anything that's important to the task", strip=False)