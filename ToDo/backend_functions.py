def calculate_todo_due_date_color(all_todos, today):
    for todo in all_todos:
        if todo.due_date is not None:
            if todo.due_date.day == today.day:
                todo.due_date_color = "blue"
            elif todo.due_date > today:
                todo.due_date_color = "green"
            elif todo.due_date < today:
                todo.due_date_color = "red"

            todo.save()


def sorting_ai(user, todo_model_obj):
    if user.is_authenticated:
        if user.profile.sort_todos_by == "date_added":

            # The code below handles how the tasks should be filtered when they are sorted by "date_added"
            if user.profile.filter_todos_by == "important_todos":
                todos = todo_model_obj.objects.filter(important=True).order_by("-date_posted")

            elif user.profile.filter_todos_by == "due_date_todos":
                todos = []
                for todo in todo_model_obj.objects.all():
                    if todo.due_date is not None:
                        todos.append(todo)

                todos.reverse()


            elif user.profile.filter_todos_by == "all_todos":
                todos = todo_model_obj.objects.all().order_by("-date_posted")

        elif user.profile.sort_todos_by == "due_date":
            due_todos = []
            normal_todos = []

            for todo in todo_model_obj.objects.all().order_by("due_date"):
                if todo.due_date is not None:
                    due_todos.append(todo)

            for todo in todo_model_obj.objects.all().order_by("-date_posted"):
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

            
    return todos