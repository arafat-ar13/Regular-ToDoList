from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from .models import ToDo, SubTask, Notes
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse, reverse_lazy
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .forms import NewTaskForm, DueDateForm, SubTaskForm, ToDoNotesForm, ContactMeForm

import datetime
import calendar

def home(request):
    if request.method == "POST":
        due_form = DueDateForm(request.POST)
        add_form = NewTaskForm(request.POST)

        if due_form.is_valid():
            days = due_form.cleaned_data.get("due_date").lower()

            if days == "today":
                days = 0
            elif days == "tomorrow":
                days = 1
            elif days == "next week":
                days = 7
            elif days == "yesterday":
                days = -1
            elif days == "last week":
                days = -7
            else:
                days = int(days)

            today = datetime.datetime.today()
            due_date = today + datetime.timedelta(days=days)


            todo = ToDo.objects.get(pk=int(request.POST.get("title", "")))
            todo.due_date = due_date
            todo.save()

            messages.success(request, "Due Date added to task")

            return redirect("todo-home")


        elif add_form.is_valid():
            title = add_form.cleaned_data.get("title")
            todo = ToDo(title=title)
            todo.creator = request.user
            todo.save()

            user = User.objects.get(username=request.user.username)
            user.profile.todos += 1
            user.profile.total_todos += 1
            user.save()
            messages.success(request, "Your new task has been added")

            return redirect("todo-home")

    else:
        add_form = NewTaskForm()
        due_form = DueDateForm()


    # Checking today's date and comparing colors of due dates
    today = datetime.datetime.now(datetime.timezone.utc)
    todo_objects = ToDo.objects.all()

    for todo in todo_objects:
        if todo.due_date is not None:
            if todo.due_date.day == today.day:
                todo.due_date_color = "blue"
            elif todo.due_date > today:
                todo.due_date_color = "green"
            elif todo.due_date < today:
                todo.due_date_color = "red"

            todo.save()

    todos = todo_objects

    # Handling how the user's tasks should be sorted
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        if user.profile.sort_todos_by == "date_added":

            # The code below handles how the tasks should be filtered when they are sorted by "date_added"
            if user.profile.filter_todos_by == "important_todos":
                todos = ToDo.objects.filter(important=True).order_by("-date_posted")

            elif user.profile.filter_todos_by == "due_date_todos":
                todos = []
                for todo in ToDo.objects.all():
                    if todo.due_date is not None:
                        todos.append(todo)

                todos.reverse()


            elif user.profile.filter_todos_by == "all_todos":
                todos = ToDo.objects.all().order_by("-date_posted")

        elif user.profile.sort_todos_by == "due_date":
            due_todos = []
            normal_todos = []

            for todo in ToDo.objects.all().order_by("due_date"):
                if todo.due_date is not None:
                    due_todos.append(todo)

            for todo in ToDo.objects.all().order_by("-date_posted"):
                if todo.due_date is None:
                    normal_todos.append(todo)

            todos = due_todos + normal_todos
            filtered_todos = []

            if user.profile.filter_todos_by == "important_todos":
                for todo in todos:
                    if todo.important:
                        filtered_todos.append(todo)

                todos = filtered_todos

            elif user.profile.filter_todos_by == "due_date_todos":
                todos = due_todos

        # Enabling user's Insights Page
        if not user.profile.insights_enabled:
            if (today.date() - user.date_joined.date()).days >= 7:
                user.profile.insights_enabled = True
                previous_monday = (today - datetime.timedelta(days=today.weekday())) - datetime.timedelta(days=7)
                user.profile.last_insights_date = previous_monday.date()
                user.save()

        # Allowing users to have their Insights Page this week if they haven't already
        if user.profile.insights_enabled:
            if (today.date() - user.profile.last_insights_date).days >= 7:
                user.profile.generated_insights_this_week = False
                user.save()


    context = {
        "todos": todos,
        "add_form": add_form,
        "due_form": due_form
    }

    return render(request, "ToDo/home.html", context=context)


def remove_due_date(request, pk):
    todo = ToDo.objects.get(pk=pk)
    todo.due_date = None
    todo.due_date_color = None

    todo.save()
    messages.info(request, "Due Date removed")

    return redirect("todo-home")


def about(request):
    if request.method == "POST":
        contact_form = ContactMeForm(request.POST)

        if contact_form.is_valid():
            user_email = contact_form.cleaned_data.get("your_email")
            user_choice = contact_form.cleaned_data.get("your_question_subject")
            choice_options = {
                "0": "Choose one",
                "1": "Account deletion",
                "2": "Feature request",
                "3": "Contribute",
                "4": "Say thanks"
            }
            user_choice = choice_options[user_choice]
            user_message = contact_form.cleaned_data.get("your_message")

            if request.user.is_authenticated:
                user = User.objects.get(username=request.user.username)
                user_real_email = user.email
                username = user.username

                if user_real_email != user_email:

                    messages.info(request, "Since you are logged in, you must only use your own email address")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            else:
                try:
                    username = User.objects.get(email=user_email).username + " (not logged in)"
                except:
                    username = "Anonymous"


            user_message += f"\n\nThe following is the user info:\nSent from: {user_email} \nUsername: {username}"
            send_mail(subject=f"{user_choice}", message=user_message, from_email=user_email, recipient_list=["arafat33k@outlook.com"])

            messages.success(request, "Your support message was sent!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:
        contact_form = ContactMeForm()

    context = {
        "contact_form": contact_form,
        "title": "About the App"
    }

    return render(request, "ToDo/about.html", context=context)


@login_required
def render_insights(request):
    """
    This is a function that will analyze the user behavior and calculate how well they are managing their tasks
    In this function, we are going to convert all the DateTime objects to Date objects just for the sake for
    better comparision.
    Although DateTime objects offer better precision as they also have time but for this function to properly analyze how many
    tasks are being created and completed, just comparing the dates is more precise since DateTime objects will not show a whole new
    day unless the hour of the day matches too. For this function, it must be called as soon as it is Monday and it's past 7 days
    since the user's previous insights date. Also, todos created and completed on the last minute will also be considered by the AI
    if we use only dates.
    """

    today = datetime.datetime.now(datetime.timezone.utc)
    user = User.objects.get(username=request.user.username)
    user_todos = ToDo.objects.filter(creator=request.user)

    # Creating a ordinal indicator function
    def determine_ordinal(date):
        if date >= 4 and date <= 20:
            ordinal = "th"
        elif date == 1 or (date % 10) == 1:
            ordinal = "st"
        elif date == 2 or (date % 10) == 2:
            ordinal = "nd"
        elif date == 3 or (date % 10) == 3:
            ordinal = "rd"

        num_with_ordinal = str(date) + ordinal
        return num_with_ordinal

    if user.profile.insights_enabled:
        # We'll determine if a whole week has passed since the user got their previous insights page
        if (today.date() - user.profile.last_insights_date).days >= 7 and not user.profile.generated_insights_this_week:
            # First, how many tasks they added this week and how many they actually completed
            todos_created_this_week = []
            todos_completed_this_week = []

            for todo in user_todos:
                # The user can visit the Insights Page even after Monday, so we need to make sure that the function works as planned
                if calendar.day_name[today.weekday()] == "Monday":
                    date_ranger = today.date()
                else:
                    # If today is not a Monday (that means that the user has visited the place after Monday), we'll analyze todos till the last Monday
                    date_ranger = (today - datetime.timedelta(days=today.weekday())).date()

                if (date_ranger - todo.date_posted.date()).days <= 7:
                    todos_created_this_week.append(todo)
                    if todo.is_checked:
                        todos_completed_this_week.append(todo)

            user.profile.todos_created_this_week = len(todos_created_this_week)
            user.profile.todos_completed_this_week = len(todos_completed_this_week)
            user.save()

            # Calculating user efficiency this week and if possible comparing with last week's
            efficiency_change = False
            if user.profile.efficiency_this_week != 0:
                # If we access user efficiency now, it'll still be the efficiency of last week's because we didn't modify it yet
                efficiency_last_week = user.profile.efficiency_this_week
                efficiency_change = True

            try:
                user.profile.efficiency_this_week = int((user.profile.todos_completed_this_week / user.profile.todos_created_this_week) * 100)
            except ZeroDivisionError:
                user.profile.efficiency_this_week = 0
            user.save()

            # So if an efficiency change exists, we'll see if this is an improvement or not
            if efficiency_change:
                if user.profile.efficiency_this_week > efficiency_last_week:
                    efficiency = ("Positive", user.profile.efficiency_this_week - efficiency_last_week)

                elif user.profile.efficiency_this_week == efficiency_last_week:
                    efficiency = ("Same", None)

                else:
                    efficiency = ("Negative", efficiency_last_week - user.profile.efficiency_this_week)

                user.profile.efficiency_change = efficiency[1]
                user.profile.efficiency_change_type = efficiency[0]
                user.save()

            # Second, how many tasks they added this week and completed ON TIME (by due date), IF their tasks had at least one due date
            todos_with_due_dates = [todo for todo in todos_completed_this_week if todo.due_date is not None]
            if todos_with_due_dates:
                todos_completed_on_time = []
                for todo in todos_with_due_dates:
                    if todo.date_completed.date() <= todo.due_date.date():
                        todos_completed_on_time.append(todo)

                user.profile.todos_completed_on_time = len(todos_completed_on_time)

            else:
                user.profile.todos_completed_on_time = 0

            # We also want to calculate how many tasks they completed this week that they created long before this week
            todos_completed_but_created_long_ago = []
            for todo in user_todos:
                if todo.date_completed is not None:
                    if (date_ranger - todo.date_completed.date()).days <= 7 and todo not in todos_created_this_week:
                        todos_completed_but_created_long_ago.append(todo)

            user.profile.todos_completed_created_long_ago = len(todos_completed_but_created_long_ago)

            user.profile.last_insights_date = date_ranger
            user.profile.generated_insights_this_week = True
            user.save()

            ready = "show content"

        else:
            ready = "show content"

        week_range = f"""
        This is your data from {determine_ordinal((user.profile.last_insights_date-datetime.timedelta(days=7)).day)}
        {calendar.month_name[(user.profile.last_insights_date-datetime.timedelta(days=7)).month]} till
        {determine_ordinal(user.profile.last_insights_date.day)} {calendar.month_name[user.profile.last_insights_date.month]}
        """

    else:
        ready = "AI is still learning"

    context = {
        "ready": ready,
        "title": "Insights",
        "week_range": week_range
    }

    return render(request, "ToDo/insights.html", context=context)


def add_todo_note(request, pk):
    todo = ToDo.objects.get(pk=pk)
    try:
        note = Notes.objects.get(parent_task=todo.title)
    except:
        note = Notes()

    if request.method == "POST":
        note_form = ToDoNotesForm(request.POST)

        if note_form.is_valid():
            task_notes = note_form.cleaned_data.get("task_notes")

            new_note = Notes(content=task_notes)
            new_note.parent_task = todo.title
            new_note.identification_id = todo.pk
            new_note.save()

            todo.notes = True
            todo.save()

            messages.success(request, "Your notes are saved")

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:
        note_form = ToDoNotesForm()

    context = {
        "todo": todo,
        "note_form": note_form,
        "note": note
    }

    return render(request, "ToDo/task_notes.html", context=context)


def delete_notes(request, pk):
    note = Notes.objects.get(pk=pk)

    todo = ToDo.objects.get(pk=note.identification_id)
    todo.notes = False
    todo.save()

    note.delete()

    messages.info(request, "Your notes are deleted")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def toggle_important_task(request, pk):
    todo = ToDo.objects.get(pk=pk)

    if todo.important:
        todo.important = False
        message = "The task is not important anymore"
    else:
        todo.important = True
        message = "Okay, the task is important. Get working!"

    todo.save()

    messages.success(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def toggle_user_sort(request):
    user = User.objects.get(username=request.user.username)
    if user.profile.sort_todos_by == "date_added":
        user.profile.sort_todos_by = "due_date"
    else:
        user.profile.sort_todos_by = "date_added"

    user.save()

    messages.success(request, "Your sort order altered")

    return redirect("todo-home")


def filter_by_important(request):
    user = User.objects.get(username=request.user.username)

    user.profile.filter_todos_by = "important_todos"
    user.save()

    messages.success(request, "You are viewing only important todos")

    return redirect("todo-home")

def filter_by_due_dates(request):
    user = User.objects.get(username=request.user.username)

    user.profile.filter_todos_by = "due_date_todos"
    user.save()

    messages.success(request, "You are only viewing tasks with due dates")

    return redirect("todo-home")

def filter_normal(request):
    user = User.objects.get(username=request.user.username)

    user.profile.filter_todos_by = "all_todos"
    user.save()

    messages.success(request, "You are viewing all your todos")

    return redirect("todo-home")


def toggle_dark_mode(request):
    user = User.objects.get(username=request.user.username)

    if user.profile.has_dark_mode:
        user.profile.has_dark_mode = False
        message = "Dark Mode disabled"
    else:
        user.profile.has_dark_mode = True
        message = "Welcome to the Dark Side"

    user.save()

    messages.success(request, message)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def delete(request, pk):
    todo = ToDo.objects.get(pk=pk)

    if not todo.is_checked:
        user = User.objects.get(username=request.user.username)
        user.profile.todos -= 1
        user.profile.total_todos -= 1
        user.save()

    todo.delete()
    messages.info(request, "Item removed!!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def check_todo(request, pk):
    todo = ToDo.objects.get(pk=pk)
    todo.is_checked = True
    todo.date_completed = datetime.datetime.now()
    todo.save()
    messages.success(request, "Sweeet! Congrats!!")

    user = User.objects.get(username=request.user.username)
    user.profile.todos -= 1
    user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def uncheck_todo(request, pk):
    todo = ToDo.objects.get(pk=pk)
    todo.is_checked = False
    todo.date_completed = None
    todo.save()

    user = User.objects.get(username=request.user.username)
    user.profile.todos += 1
    user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def add_subtask(request, pk):
    todo = ToDo.objects.get(pk=pk)
    subtasks = SubTask.objects.filter(parent_task=todo.title)

    if request.method == "POST":
        subtask_form = SubTaskForm(request.POST)

        if subtask_form.is_valid():
            subtask_title = subtask_form.cleaned_data.get("sub_task")

            subtask = SubTask(title=subtask_title)
            subtask.parent_task = todo.title
            subtask.identification_id = todo.pk

            todo.num_of_subtasks += 1
            todo.save()

            subtask.save()

            messages.success(request, "Subtask added")

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:
        subtask_form = SubTaskForm()


    context = {
        "todo": todo,
        "subtask_form": subtask_form,
        "subtasks": subtasks
    }

    return render(request, "ToDo/subtasks.html", context=context)


def delete_subtask(request, pk):
    subtask = SubTask.objects.get(pk=int(pk))

    parent_todo = ToDo.objects.get(pk=subtask.identification_id)
    parent_todo.num_of_subtasks -= 1
    parent_todo.save()

    subtask.delete()

    messages.info(request, "Item removed!!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def toggle_subtask(request, pk):
    subtask = SubTask.objects.get(pk=int(pk))

    if subtask.done:
        subtask.done = False
        subtask.save()

        messages.info(request, "Okay, take your time!")

    else:

        subtask.done = True
        subtask.save()

        messages.info(request, "Awesome!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class TodoCompletedView(ListView):
    model = ToDo
    template_name = "ToDo/completed.html"
    context_object_name = "todos"
    ordering = ["-date_posted"]


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = ToDo
    fields = ["title"]
    success_url = reverse_lazy("todo-home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your task has been edited")
        return super().form_valid(form)


class SubtaskUpdateView(LoginRequiredMixin, UpdateView):
    model = SubTask
    fields = ["title"]
    success_url = reverse_lazy("todo-home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your subtask has been edited")


        return super().form_valid(form)


class ToDoNotesUpdateView(LoginRequiredMixin, UpdateView):
    model = Notes
    fields = ["content"]
    success_url = reverse_lazy("todo-home")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your notes have been edited")

        return super().form_valid(form)