import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import (ContactMeForm, DueDateForm, NewTaskForm, NewTaskListForm,
                    SearchForm, SubTaskForm, ToDoNotesForm)
from .models import Notes, SubTask, TaskList, ToDo


# Handling error views
def handler500(request, *args):
    return render(request, 'ToDo/Error Pages/500.html', status=500)


def handler404(request, *args):
    return render(request, 'ToDo/Error Pages/500.html', status=404)


@login_required
def search(request):
    results = []

    if request.method == "POST":
        search_form = SearchForm(request.POST)

        if search_form.is_valid():
            search_query = search_form.cleaned_data.get("query")
            user_todos = ToDo.objects.filter(creator=request.user)

            matching_tasks = ToDo.objects.filter(
                title__icontains=search_query, creator=request.user)
            matching_lists = TaskList.objects.filter(
                title__icontains=search_query, owner=request.user)

            matching_subtasks = []
            for subtask in SubTask.objects.filter(title__icontains=search_query):
                if subtask.parent_task in user_todos:
                    matching_subtasks.append(subtask)

            matching_notes = []
            for note in Notes.objects.filter(content__icontains=search_query):
                if note.parent_task in user_todos:
                    matching_notes.append(note)

            results = {
                "matching_tasks": matching_tasks,
                "matching_lists": matching_lists,
                "matching_subtasks": matching_subtasks,
                "matching_notes": matching_notes
            }

            if len(matching_tasks) == 0 and len(matching_subtasks) == 0 and len(matching_lists) == 0 and len(matching_notes) == 0:
                results = "got nothing"

    else:
        search_form = SearchForm()

    context = {
        "search_form": search_form,
        "title": "Search",
        "results": results
    }

    return render(request, "ToDo/search_page.html", context=context)


@login_required
def todo_detail(request, title, pk):
    try:
        todo = ToDo.objects.get(title=title, creator=request.user, pk=pk)
    except:
        return render(request, "ToDo/restrict_access.html")

    subtasks = SubTask.objects.filter(parent_task=todo)

    try:
        note = Notes.objects.get(parent_task=todo)
    except:
        note = Notes()

    if request.method == "POST":
        note_form = ToDoNotesForm(request.POST)
        subtask_form = SubTaskForm(request.POST)
        due_form = DueDateForm(request.POST)

        if note_form.is_valid():
            task_notes = note_form.cleaned_data.get("task_notes")

            new_note = Notes(content=task_notes)
            new_note.parent_task = todo
            new_note.save()

            todo.has_notes = True
            todo.save()

            messages.success(request, "Your notes are saved")

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        elif subtask_form.is_valid():
            subtask_title = subtask_form.cleaned_data.get("sub_task")

            subtask = SubTask(title=subtask_title)
            subtask.parent_task = todo

            subtask.parent_task.num_of_subtasks += 1
            subtask.parent_task.save()

            subtask.save()

            messages.success(request, "Subtask added")

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        elif due_form.is_valid():
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

            todo.due_date = due_date
            todo.save()

            messages.success(request, "Due Date added to task")

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:
        note_form = ToDoNotesForm()
        subtask_form = SubTaskForm()
        due_form = DueDateForm()

    # Task progress percentage
    percentage = 0
    if subtasks:
        subtasks_completed = subtasks.filter(done=True).count()
        percentage = int((subtasks_completed/subtasks.count()) * 100)

    context = {
        "todo": todo,
        "note_form": note_form,
        "note": note,
        "subtask_form": subtask_form,
        "subtasks": subtasks,
        "due_form": due_form,
        "title": todo.title,
        "percentage": percentage
    }

    return render(request, "ToDo/detailed_view.html", context=context)


@login_required
def remove_due_date(request, pk):
    try:
        todo = ToDo.objects.get(pk=pk, creator=request.user)
    except:
        return render(request, "ToDo/restrict_access.html")

    todo.due_date = None
    todo.due_date_color = None

    todo.save()
    messages.info(request, "Due Date removed")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def about(request):
    if request.method == "POST":
        contact_form = ContactMeForm(request.POST)

        if contact_form.is_valid():
            user_email = contact_form.cleaned_data.get("your_email")
            user_choice = contact_form.cleaned_data.get(
                "your_question_subject")
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

                    messages.info(
                        request, "Since you are logged in, you must only use your own email address")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            else:
                try:
                    username = User.objects.get(
                        email=user_email).username + " (not logged in)"
                except:
                    username = "Anonymous"

            user_message += f"\n\nThe following is the user info:\nSent from: {user_email} \nUsername: {username}"
            send_mail(subject=f"{user_choice}", message=user_message,
                      from_email=user_email, recipient_list=["arafat33k@outlook.com"])

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
def view_taskslists(request):
    user_lists = TaskList.objects.filter(owner=request.user)

    if request.method == "POST":
        list_form = NewTaskListForm(request.POST)

        if list_form.is_valid():
            list_title = list_form.cleaned_data.get("title")

            if list_title == "Tasks" or list_title == "tasks":
                messages.info(request, "Sorry, this is a reserved name")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            new_list = TaskList(title=list_title)
            new_list.owner = request.user
            new_list.save()

            messages.success(
                request, "Your shiny new list is ready to be used")
            return redirect("tasklist-single-view", list_title, new_list.pk)

    else:
        list_form = NewTaskListForm()

    context = {
        "user_lists": user_lists,
        "list_form": list_form,
    }

    return render(request, "ToDo/tasklists_overview.html", context=context)


@login_required
def tasklist_single_view(request, title, pk=None, **kwargs):
    if title == "tasks":
        todos = ToDo.objects.filter(
            creator=request.user, parent_list=None).order_by("-date_created")
        tasklist = "Tasks"

    else:
        try:
            tasklist = TaskList.objects.get(
                title=title, pk=pk, owner=request.user)
        except:
            return render(request, "ToDo/restrict_access.html")
        todos = ToDo.objects.filter(
            parent_list=tasklist, creator=request.user).order_by("-date_created")

    no_todos = False
    if len([todo for todo in todos if not todo.is_checked]) == 0:
        no_todos = True

    show_completed = True
    if len([todo for todo in todos if todo.is_checked]) == 0:
        show_completed = False

    if request.method == "POST":
        add_form = NewTaskForm(request.POST)

        if add_form.is_valid():
            task_title = add_form.cleaned_data.get("title")
            todo = ToDo(title=task_title)

            todo.creator = request.user

            if title != "tasks":
                todo.parent_list = TaskList.objects.get(
                    title=title, owner=request.user)
                todo.parent_list.num_of_tasks += 1
                todo.parent_list.save()

            todo.save()

            messages.success(request, "Your new task has been added")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:
        add_form = NewTaskForm()

    context = {
        "tasklist": tasklist,
        "todos": todos,
        "add_form": add_form,
        "no_todos": no_todos,
        "show_completed": show_completed,
        "title": title
    }

    return render(request, "ToDo/tasklist_single_view.html", context=context)


@login_required
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


@login_required()
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


@login_required
def delete(request, item_type, pk):
    """
    Universal view function to delete any object from the database
    """
    if item_type == "todo":
        try:
            todo = ToDo.objects.get(pk=pk, creator=request.user)
        except:
            return render(request, "ToDo/restrict_access.html")

        todo.delete()

    elif item_type == "subtask":
        subtask = SubTask.objects.get(pk=pk)

        # Security check
        if subtask.parent_task.creator != request.user:
            return render(request, "ToDo/restrict_access.html")

        subtask.parent_task.num_of_subtasks -= 1
        subtask.parent_task.save()

        subtask.delete()

    elif item_type == "notes":
        notes = Notes.objects.get(pk=pk)

        # Security check
        if notes.parent_task.creator != request.user:
            return render(request, "ToDo/restrict_access.html")

        notes.parent_task.has_notes = False
        notes.parent_task.save()
        notes.delete()

    elif item_type == "tasklist":
        try:
            tasklist = TaskList.objects.get(pk=pk, owner=request.user)
        except:
            return render(request, "ToDo/restrict_access.html")

        # Delete child todos from the database
        for todo in ToDo.objects.filter(parent_list=tasklist):
            todo.delete()

        tasklist.delete()

    messages.info(request, f"Your {item_type} was deleted")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def toggle_todo(request, pk):
    try:
        todo = ToDo.objects.get(pk=pk, creator=request.user)
    except:
        return render(request, "ToDo/restrict_access.html")

    if todo.is_checked:
        todo.is_checked = False
        todo.date_completed = None
    else:
        todo.is_checked = True
        todo.date_completed = datetime.datetime.now()

    todo.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def toggle_subtask(request, pk):
    try:
        subtask = SubTask.objects.get(pk=pk)
        # Security check
        if subtask.parent_task.creator != request.user:
            return render(request, "ToDo/restrict_access.html")
    except:
        return render(request, "ToDo/restrict_access.html")

    if subtask.done:
        subtask.done = False
        subtask.save()

        messages.info(request, "Okay, take your time!")

    else:

        subtask.done = True
        subtask.save()

        messages.info(request, "Awesome!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class TodoImportantView(LoginRequiredMixin, ListView):
    model = ToDo
    template_name = "ToDo/important_tasks.html"
    context_object_name = "todos"
    ordering = ["-date_created"]

    def get_queryset(self):
        query_set = ToDo.objects.filter(
            creator=self.request.user, important=True, is_checked=False)

        return query_set


class ToDoNextUpView(LoginRequiredMixin, ListView):
    model = ToDo
    template_name = "ToDo/Next-Up Pages/next_up.html"
    ordering = ["-due_date"]
    context_object_name = "todos"

    def get_queryset(self):
        query_set = []
        for todo in ToDo.objects.filter(creator=self.request.user, is_checked=False):
            if todo.due_date is not None:
                query_set.append(todo)

        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.datetime.now(datetime.timezone.utc)
        tomorrow = today + datetime.timedelta(days=1)

        todos_earlier = []
        todos_today = []
        todos_tomorrow = []
        todos_later = []

        for todo in ToDo.objects.filter(creator=self.request.user, is_checked=False):
            if todo.due_date is not None:
                if todo.due_date.day == today.day and todo.due_date.month == today.month and todo.due_date.year == today.year:
                    todos_today.append(todo)
                elif todo.due_date.day == tomorrow.day and todo.due_date.month == tomorrow.month and todo.due_date.year == tomorrow.year:
                    todos_tomorrow.append(todo)
                elif todo.due_date < today:
                    todos_earlier.append(todo)
                elif todo.due_date > tomorrow:
                    todos_later.append(todo)

        context["todos_earlier"] = todos_earlier
        context["todos_today"] = todos_today
        context["todos_tomorrow"] = todos_tomorrow
        context["todos_later"] = todos_later

        return context


class TodoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ToDo
    fields = ["title"]
    template_name = "ToDo/Form Pages/todo_form.html"

    # Checking if the correct user is accessing their tasks
    def test_func(self):
        try:
            todo = ToDo.objects.get(pk=self.kwargs.get("pk"))
            return True if todo.creator == self.request.user else False
        except:
            return False

    def handle_no_permission(self):
        return render(self.request, "ToDo/restrict_access.html")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your task has been edited")
        return super().form_valid(form)

    def get_success_url(self):
        todo = ToDo.objects.get(pk=self.kwargs.get("pk"))

        return reverse("todo-detailed", kwargs={'title': todo.title, 'pk': todo.pk})


class SubtaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SubTask
    fields = ["title"]
    success_url = reverse_lazy("todo-home")
    template_name = "ToDo/Form Pages/subtask_form.html"

    # Checking if the correct user is accessing their tasks
    def test_func(self):
        try:
            subtask = SubTask.objects.get(pk=self.kwargs.get("pk"))
            return True if subtask.parent_task.creator == self.request.user else False
        except:
            return False

    def handle_no_permission(self):
        return render(self.request, "ToDo/restrict_access.html")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your subtask has been edited")

        return super().form_valid(form)

    def get_success_url(self):
        subtask = SubTask.objects.get(pk=self.kwargs.get("pk"))

        return reverse("todo-detailed", kwargs={'title': subtask.parent_task.title, 'pk': subtask.parent_task.pk})


class ToDoNotesUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Notes
    fields = ["content"]
    success_url = reverse_lazy("todo-home")
    template_name = "ToDo/Form Pages/notes_form.html"

    # Checking if the correct user is accessing their tasks
    def test_func(self):
        try:
            note = Notes.objects.get(pk=self.kwargs.get("pk"))
            return True if note.parent_task.creator == self.request.user else False
        except:
            return False

    def handle_no_permission(self):
        return render(self.request, "ToDo/restrict_access.html")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.info(self.request, "Your notes have been edited")

        return super().form_valid(form)

    def get_success_url(self):
        note = Notes.objects.get(pk=self.kwargs.get("pk"))

        return reverse("todo-detailed", kwargs={'title': note.parent_task.title, 'pk': note.parent_task.pk})


class TaskListUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TaskList
    fields = ["title"]
    template_name = "ToDo/Form Pages/tasklist_form.html"

    # Checking for security
    def test_func(self):
        try:
            tasklist = TaskList.objects.get(pk=self.kwargs.get("pk"))
            return True if tasklist.owner == self.request.user else False
        except:
            False

    def handle_no_permission(self):
        return render(self.request, "ToDo/restrict_access.html")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.info(self.request, "Your task list was updated")

        return super().form_valid(form)

    def get_success_url(self):
        tasklist = TaskList.objects.get(pk=self.kwargs.get("pk"))

        return reverse("tasklist-single-view", kwargs={'title': tasklist.title, 'pk': tasklist.pk})
