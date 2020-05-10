import calendar
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from .models import ToDo


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
    user_todos = ToDo.objects.filter(creator=user)

    user_total_todos = user_todos.count()
    user_active_todos = ToDo.objects.filter(creator=user, is_checked=False).count()

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
                    date_ranger = (today - datetime.timedelta(days=today.weekday())).date()

                if (date_ranger - todo.date_created.date()).days <= 7:
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
        "week_range": week_range,
        "user_total_todos": user_total_todos,
        "user_active_todos": user_active_todos
    }

    return render(request, "ToDo/insights.html", context=context)
