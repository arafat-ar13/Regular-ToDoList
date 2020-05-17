import calendar
import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import (HttpResponse, HttpResponseRedirect, redirect,
                              render)
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

    if request.method == "GET":
        search_form = SearchForm(request.GET)

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

    # Task progress percentage
    percentage = 0
    if subtasks:
        subtasks_completed = subtasks.filter(done=True).count()
        percentage = int((subtasks_completed/subtasks.count()) * 100)

    # if request.method == "POST":
    #     attachment_form = TaskAttachmentForm(request.POST, request.FILES)

    #     print(request.FILES)
    #     print(request.POST)

    #     if attachment_form.is_valid():
    #         attachment_form.instance.creator = request.user
    #         attachment_form.save()
        
    # else:
    #     attachment_form = TaskAttachmentForm()

    context = {
        "todo": todo,
        "note_form": ToDoNotesForm(),
        "note": note,
        "subtask_form": SubTaskForm(),
        "subtasks": subtasks,
        "due_form": DueDateForm(),
        "title": todo.title,
        "percentage": percentage
    }

    return render(request, "ToDo/detailed_view.html", context=context)


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

            if list_title in ["Tasks", "tasks", "Important", "important"]:
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

    # Passing 'yes' if there should be an Insights highlight
    insights_highlight = False
    today = datetime.datetime.now(datetime.timezone.utc).date()
    if (today - request.user.profile.last_insights_date).days >= 7:
        insights_highlight = True

    context = {
        "user_lists": user_lists,
        "list_form": list_form,
        "insights_highlight": insights_highlight,
        "today_name": calendar.day_name[datetime.datetime.today().weekday()]
    }

    return render(request, "ToDo/tasklists_overview.html", context=context)


@login_required
def tasklist_single_view(request, title, pk=None, **kwargs):
    if title == "tasks":
        todos = ToDo.objects.filter(
            creator=request.user, parent_list=None)
        tasklist = "Tasks"

    else:
        try:
            tasklist = TaskList.objects.get(
                title=title, pk=pk, owner=request.user)
        except:
            return render(request, "ToDo/restrict_access.html")
        todos = ToDo.objects.filter(
            parent_list=tasklist, creator=request.user)

    completed_todos = todos.filter(is_checked=True).order_by("-date_completed")
    todos = todos.filter(is_checked=False).order_by("-date_created")

    context = {
        "tasklist": tasklist,
        "todos": todos,
        "completed_todos": completed_todos,
        "add_form": NewTaskForm(),
        "title": title
    }

    return render(request, "ToDo/tasklist_single_view.html", context=context)


@login_required
def create(request):
    """
    Universal function to create ToDos, Subtasks and Notes. It can also be used to create Due Dates
    with AJAX support for asynchronous operation
    Having a single function will make sure to have only one URL for creating objects
    """

    # Setting up dummy variables to avoid any UnboundLocal Errors
    title = ""
    content = ""
    days = ""
    parent_list = ""
    parent_task = ""
    response_data = {}

    if request.method == "POST":
        item_type = request.POST.get("item_type")

        if item_type == "due_date":
            days = request.POST.get("due_date").lower()
        elif item_type != "notes":
            title = request.POST.get("title")
        else:
            content = request.POST.get("content")

        if item_type != "todo":
            parent_task = ToDo.objects.get(
                pk=int(request.POST.get("parent_task_pk")), creator=request.user)
        else:
            if request.POST.get("parent_list") != "Tasks":
                parent_list = TaskList.objects.get(
                    title=request.POST.get("parent_list"))
            else:
                parent_list = "Tasks"

        if item_type == "todo":
            new_todo = ToDo(title=title)
            new_todo.creator = request.user

            # Setting up parent list
            if parent_list != "Tasks":
                new_todo.parent_list = parent_list
                new_todo.parent_list.num_of_tasks += 1
                new_todo.parent_list.save()
            else:
                parent_list = None
                new_todo.parent_list = parent_list

            new_todo.save()

            response_data["todo_pk"] = new_todo.pk
            response_data["todo_title"] = new_todo.title

        elif item_type == "subtask":
            new_subtask = SubTask(title=title)

            # Setting up parent task
            new_subtask.parent_task = parent_task
            new_subtask.parent_task.num_of_subtasks += 1
            new_subtask.parent_task.save()

            new_subtask.save()

            response_data = {}
            response_data["subtask_pk"] = new_subtask.pk
            response_data["subtask_title"] = new_subtask.title

        elif item_type == "notes":
            new_note = Notes(content=content)

            # Setting up parent_task
            new_note.parent_task = parent_task
            new_note.parent_task.has_notes = True
            new_note.parent_task.save()

            new_note.save()

            response_data = {}
            response_data["note_content"] = new_note.content
            response_data["note_pk"] = new_note.pk
            response_data["note_created"] = new_note.date_added.strftime(
                "%b %d, %Y")

        elif item_type == "due_date":
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

            parent_task.due_date = due_date

            if today.date() == due_date.date():
                parent_task.due_date_color = "blue"
            elif today.date() > due_date.date():
                parent_task.due_date_color = "red"
            elif today.date() < due_date.date():
                parent_task.due_date_color = "green"

            parent_task.save()

            response_data["due_date"] = due_date.strftime("%b %d")
            response_data["due_date_color"] = parent_task.due_date_color
            response_data["parent_task_pk"] = parent_task.pk

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@login_required
def delete(request):
    """
    Universal view function to delete any object from the database.
    It has AJAX support for asynchronous deletion and removal of items
    """
    response_data = {}
    if request.method == "POST":
        item_type = request.POST.get("item_type")
        pk = int(request.POST.get("pk"))

        if item_type == "todo":
            todo = ToDo.objects.get(pk=pk)
            todo.delete()

        elif item_type == "subtask":
            subtask = SubTask.objects.get(pk=pk)

            subtask.parent_task.num_of_subtasks -= 1
            subtask.parent_task.save()

            response_data["hide_heading"] = "no"
            if subtask.parent_task.num_of_subtasks == 0:
                response_data["hide_heading"] = "yes"

            subtask.delete()

        elif item_type == "notes":
            notes = Notes.objects.get(pk=pk)

            notes.parent_task.has_notes = False
            notes.parent_task.save()
            notes.delete()

        elif item_type == "tasklist":
            tasklist = TaskList.objects.get(pk=pk)

            # Delete child todos from the database
            for todo in ToDo.objects.filter(parent_list=tasklist):
                todo.delete()

            tasklist.delete()

        elif item_type == "due_date":
            parent_task = ToDo.objects.get(pk=pk)
            parent_task.due_date = None
            parent_task.due_date_color = None
            parent_task.save()

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@login_required
def toggle_important_task(request):

    if request.method == "POST":
        pk = int(request.POST.get("pk"))

        todo = ToDo.objects.get(pk=pk)

        if todo.important:
            todo.important = False
        else:
            todo.important = True

        todo.save()

        response_data = "success!"

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@login_required()
def toggle_theme(request):
    user = User.objects.get(username=request.user.username)

    if request.method == "POST":
        theme = request.POST.get("theme")
        print(theme)

        user.profile.theme = theme
        user.save()

        response_data = "success!"

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@login_required
def toggle_todo(request):

    if request.method == "POST":
        pk = int(request.POST.get("pk"))
        todo = ToDo.objects.get(pk=pk)

        completed_tasks_before = ToDo.objects.filter(
            parent_list=todo.parent_list, is_checked=True).count()

        if todo.is_checked:
            todo.is_checked = False
            todo.date_completed = None
        else:
            todo.is_checked = True
            todo.date_completed = datetime.datetime.now()

        todo.save()

        response_data = {}
        response_data["todo_title"] = todo.title
        response_data["todo_pk"] = todo.pk
        try:
            response_data["todo_date_completed"] = todo.date_completed.strftime(
                "%b %d")
        except:
            response_data["todo_date_completed"] = ""

        # Checking if the todo was important or not
        if todo.important:
            response_data["important_op"] = "mark"
            response_data["important_class"] = "btn btn-warning"
        else:
            response_data["important_op"] = "unmark"
            response_data["important_class"] = "btn btn-secondary"

        # Checking if we should display "Completed Tasks"
        if (ToDo.objects.filter(parent_list=todo.parent_list, is_checked=True).count() - completed_tasks_before == 1) and completed_tasks_before != 1:
            show_hidden_completed_tasks = True
        elif ToDo.objects.filter(parent_list=todo.parent_list, is_checked=True).count() == 0:
            show_hidden_completed_tasks = False
        else:
            show_hidden_completed_tasks = None

        response_data["show_hidden_completed_tasks"] = show_hidden_completed_tasks

        show_tasks = True
        if ToDo.objects.filter(parent_list=todo.parent_list, is_checked=False).count() == 0:
            show_tasks = False

        response_data["show_tasks"] = show_tasks

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@login_required
def toggle_subtask(request):

    if request.method == "POST":
        subtask = SubTask.objects.get(pk=int(request.POST.get("pk")))

        if subtask.done:
            subtask.done = False
        else:
            subtask.done = True

        subtask.save()

        response_data = {}

        try:
            all_subtasks = SubTask.objects.filter(parent_task=subtask.parent_task)
            completed_tasks = SubTask.objects.filter(parent_task=subtask.parent_task).filter(done=True).count()
            percentage = int((completed_tasks/all_subtasks.count()) * 100)
            print(percentage)

        except ZeroDivisionError:
            percentage = 0

        response_data["percentage"] = percentage

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


class TodoImportantView(LoginRequiredMixin, ListView):
    model = ToDo
    template_name = "ToDo/important_tasks.html"
    context_object_name = "todos"

    def get_queryset(self):
        query_set = ToDo.objects.filter(
            creator=self.request.user, important=True, is_checked=False).order_by("-date_created")

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
        today = datetime.datetime.now()
        tomorrow = today + datetime.timedelta(days=1)

        todos_earlier = []
        todos_today = []
        todos_tomorrow = []
        todos_later = []

        for todo in ToDo.objects.filter(creator=self.request.user, is_checked=False):
            if todo.due_date is not None:
                if todo.due_date.date() == today.date():
                    todos_today.append(todo)
                elif todo.due_date.date() == tomorrow.date():
                    todos_tomorrow.append(todo)
                elif todo.due_date.date() < today.date():
                    todos_earlier.append(todo)
                elif todo.due_date.date() > tomorrow.date():
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
