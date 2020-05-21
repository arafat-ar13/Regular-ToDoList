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


import calendar
import datetime
import os

import seaborn as sns
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from matplotlib import pyplot as plt

from .models import ToDo


def draw_bar_graph(user_todos_this_week, user):
    day_completions = {
        "Monday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
        "Thursday": 0,
        "Friday": 0,
        "Saturday": 0,
        "Sunday": 0
    }

    if user.profile.theme == "dark":
        plt.style.use("dark_background")

    # Checking if this user's 'insights_graphs' dir exists or not
    if not os.path.exists(f"media/users/{user}_{user.pk}/insights_graphs/"):
        # If it doesn't, then we'll create one for them
        os.mkdir(f"media/users/{user}_{user.pk}/insights_graphs/")

    path = f"media/users/{user}_{user.pk}/insights_graphs/graph_this_week.png"

    for todo in user_todos_this_week:
        day_completions[calendar.day_name[todo.date_completed.weekday()]] += 1

    # We'll only proceed to drawing the graph if they user had completed at least one task over the week
    draw = False
    for val in day_completions.values():
        if val > 0:
            draw = True

    if draw:
        day_completions = {
            "days": list(day_completions.keys()),
            "tasks": list(day_completions.values())
        }

        # Starting the plot
        sns.barplot(x="days", y="tasks", data=day_completions)
        plt.title(f"Weekly overview of {user.username}")
        plt.xlabel("Days")
        plt.ylabel("Tasks completed")

        plt.savefig(path)


@login_required
def render_insights(request):
    today = datetime.datetime.today()
    user = User.objects.get(username=request.user.username)
    user_todos = ToDo.objects.filter(creator=user)

    user_total_todos = user_todos.count()
    user_active_todos = ToDo.objects.filter(
        creator=user, is_checked=False).count()

    # Enabling user's Insights Page
    if not user.profile.insights_enabled:
        if (today.date() - user.date_joined.date()).days >= 7:
            user.profile.insights_enabled = True
            previous_monday = (
                today - datetime.timedelta(days=today.weekday())) - datetime.timedelta(days=7)
            user.profile.last_insights_date = previous_monday.date()
            user.save()

    # Allowing users to have their Insights Page this week if they haven't already
    if user.profile.insights_enabled:
        if (today.date() - user.profile.last_insights_date).days >= 7:
            user.profile.generated_insights_this_week = False
            user.save()

    # Creating a ordinal indicator function
    def determine_ordinal(date):
        if (date >= 4 and date <= 20) or (date >= 24 and date <= 30):
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
                    date_ranger = (
                        today - datetime.timedelta(days=today.weekday())).date()

                if (date_ranger - todo.date_created.date()).days <= 7:
                    todos_created_this_week.append(todo)
                    if todo.is_checked:
                        todos_completed_this_week.append(todo)

            user.profile.todos_created_this_week = len(todos_created_this_week)
            user.profile.todos_completed_this_week = len(
                todos_completed_this_week)
            user.save()

            # Calculating user efficiency this week and if possible comparing with last week's
            efficiency_change = False
            if user.profile.efficiency_this_week != 0:
                # If we access user efficiency now, it'll still be the efficiency of last week's because we didn't modify it yet
                efficiency_last_week = user.profile.efficiency_this_week
                efficiency_change = True

            try:
                user.profile.efficiency_this_week = int(
                    (user.profile.todos_completed_this_week / user.profile.todos_created_this_week) * 100)
            except ZeroDivisionError:
                user.profile.efficiency_this_week = 0
            user.save()

            # So if an efficiency change exists, we'll see if this is an improvement or not
            if efficiency_change:
                if user.profile.efficiency_this_week > efficiency_last_week:
                    efficiency = (
                        "Positive", user.profile.efficiency_this_week - efficiency_last_week)

                elif user.profile.efficiency_this_week == efficiency_last_week:
                    efficiency = ("Same", None)

                else:
                    efficiency = ("Negative", efficiency_last_week -
                                  user.profile.efficiency_this_week)

                user.profile.efficiency_change = efficiency[1]
                user.profile.efficiency_change_type = efficiency[0]
                user.save()

            # Second, how many tasks they added this week and completed ON TIME (by due date), IF their tasks had at least one due date
            # Also, we'll be calculating how many tasks they completed after the due date
            todos_with_due_dates = [
                todo for todo in todos_completed_this_week if todo.due_date is not None]
            if todos_with_due_dates:
                todos_completed_on_time = 0
                for todo in todos_with_due_dates:
                    if todo.date_completed.date() <= todo.due_date.date():
                        todos_completed_on_time += 1

                user.profile.todos_completed_on_time = todos_completed_on_time

            else:
                user.profile.todos_completed_on_time = 0

            todos_completed_after_due_date = 0
            # Looping over all user tasks that had due dates
            for todo in [todo for todo in user_todos if todo.due_date is not None]:
                if todo.is_checked:
                    if (date_ranger - todo.date_completed.date()).days <= 7:
                        if todo.date_completed.date() >= todo.due_date.date():
                            todos_completed_after_due_date += 1

            user.profile.todos_completed_after_due_date = todos_completed_after_due_date
            user.save()

            # We also want to calculate how many tasks they completed this week that they created long before this week
            todos_completed_but_created_long_ago = 0
            for todo in user_todos:
                if todo.date_completed is not None:
                    if (date_ranger - todo.date_completed.date()).days <= 7 and todo not in todos_created_this_week:
                        todos_completed_but_created_long_ago += 1

            user.profile.todos_completed_created_long_ago = todos_completed_but_created_long_ago
            user.save()

            # Fourth, we want to show how many important task they completed over the week
            important_todos_completed = 0
            for todo in todos_completed_this_week:
                if todo.important:
                    important_todos_completed += 1

            user.profile.important_tasks_completed_this_week = important_todos_completed
            user.save()

            todos_missed = len(
                [todo for todo in todos_created_this_week if todo not in todos_completed_this_week])
            user.profile.missed_tasks_this_week = todos_missed
            user.save()

            user.profile.last_insights_date = date_ranger
            user.profile.generated_insights_this_week = True
            user.save()

            # Drawing the bar graph
            user_todos_this_week = []
            # We'll only send todos that were completed this week (regardless of when they were created)
            for todo in user_todos:
                if todo.is_checked:
                    if (date_ranger - todo.date_completed.date()).days <= 7:
                        user_todos_this_week.append(todo)

            draw_bar_graph(user_todos_this_week, user)

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

    img_exists = False
    if os.path.isfile(f"media/users/{user}_{user.pk}/insights_graphs/graph_this_week.png"):
        img_exists = True

    context = {
        "ready": ready,
        "title": "Insights",
        "week_range": week_range,
        "img_exists": img_exists,
        "user_total_todos": user_total_todos,
        "user_active_todos": user_active_todos
    }

    return render(request, "ToDo/insights.html", context=context)
