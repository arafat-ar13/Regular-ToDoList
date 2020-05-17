function toggleImportant(pk, type) {
    $.ajax({
        url: important_toggle_url, // the endpoint
        type: "POST", // http method
        data: { "pk": pk }, // data sent with the get request

        // handle a successful response
        success: function (json) {
            console.log("success"); // another sanity check
        },
    });

    let important = document.getElementById(`todo-important-${pk}`)
    if (type == "unmark") {
        important.className = "btn btn-secondary"
        important.setAttribute("onClick", `toggleImportant('${pk}', 'mark')`)
    }
    else {
        important.className = "btn btn-warning"
        important.setAttribute("onClick", `toggleImportant('${pk}', 'unmark')`)
    }
}

function changeTheme(theme) {
    $.ajax({
        url: theme_toggle_url, // the endpoint
        type: "POST", // http method
        data: { "theme": theme }, // data sent with the get request

        // handle a successful response
        success: function (json) {
            console.log("success"); // another sanity check
        },
    });

    var stylesheet = document.getElementById("css_changer");
    let toggler = document.getElementById("theme-toggler")
    if (theme == "dark") {
        stylesheet.setAttribute('href', dark_theme);
        toggler.className = "nav-item nav-link fas fa-sun"
        toggler.setAttribute("onClick", `changeTheme('light')`)
    }
    else {
        stylesheet.setAttribute('href', light_theme);
        toggler.className = "nav-item nav-link fas fa-moon"
        toggler.setAttribute("onClick", `changeTheme('dark')`)
    }


}

function toggleTodo(pk, opType, fromView) { // opType = Operation Type
    $.ajax({
        url: todo_toggle_url, // the endpoint
        type: "POST", // http method
        data: { "pk": pk }, // data sent with the get request
        dataType: 'json',

        // handle a successful response
        success: function (json) {
            console.log("successful operation"); // another sanity check
            console.log(json.show_hidden_completed_tasks)

            if (fromView == "single-view") {

                if (opType == "check") {
                    document.getElementById(`todo-item-${pk}`).style.display = "none"

                    $("#todo-list-completed").prepend(
                        `
                    <li id="todo-item-${pk}-completed" class="list-group-item dark-mode-assist-section big-list-item">
                        <button style="float:left" onclick="toggleTodo('${pk}', 'uncheck', 'single-view')"
                            class="btn btn-success"><i class="fa fa-check"></i> </button>
                        <a style="margin-left: 7px; color:inherit; text-decoration: none; font-size: 2.5ch;"
                            href="/todo/${json.todo_title}/${json.todo_pk}"> <s>${json.todo_title}</s></a>
                        <br><b style="color:chocolate">On:${json.todo_date_completed}</b>
                    </li>
                    `
                    )
                }

                else if (opType == "uncheck") {
                    document.getElementById("todo-list").style.display = "block"
                    document.getElementById(`todo-item-${pk}-completed`).style.display = "none"
                    $("#todo-list").prepend(
                        `
                    <li id="todo-item-${pk}" class="list-group-item dark-mode-assist-section big-list-item">
                        <button style="float:left" onclick="toggleTodo(${pk}, 'check', 'single-view')"
                            class="btn btn-outline-success"><i class="fa fa-check"></i> </button>
                        <a style="margin-left: 7px; color:inherit; text-decoration: none; font-size: 2.5ch;"
                            href="/todo/${json.todo_title}/${json.todo_pk}">${json.todo_title}</a>
                        <button data-toggle="modal" data-target="#exampleModalCenter${pk}" style="float: right;"
                            class="btn btn-outline-danger"><i class="fas fa-trash"></i></button>
                        <button id="todo-important-${pk}" onclick="toggleImportant(${pk}, '${json.important_op}')"
                            style="float: right; margin-right:3px" class="${json.important_class}"><i class="fas fa-star"></i>
                        </button>
                    </li>
                    <div class="modal fade" id="exampleModalCenter${pk}" tabindex="-1" role="dialog"
                        aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
                        <div class="modal-dialog modal-dialog-centered" role="document">
                            <div class="modal-content dark-mode-assist-section">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="exampleModalLongTitle">Confirm the deletion</h5>
                                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                </div>
                                <div class="modal-body">
                                    Are you sure you want to delete this task permanently?
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                                    <button data-dismiss="modal" onclick="deleteItem('todo', ${pk})" type="submit"
                                        class="btn btn-danger">Yes, I am sure</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    `
                    )
                }

                if (json.show_hidden_completed_tasks == true) {
                    console.log("Hidden completed tasks now shown")
                    document.getElementById("completed-tasks").style.display = "block"
                }
                else if (json.show_hidden_completed_tasks == false) {
                    console.log("Hiding completed tasks")
                    document.getElementById("completed-tasks").style.display = "none"
                }

                if (json.show_tasks == false) {
                    document.getElementById("todo-list").style.display = "none"
                }
            }

            else if (fromView == "detail-view") {
                let todoBtn = document.getElementById(`todo-btn-${pk}`)
                let todoTitle = document.getElementById(`todo-title-${pk}`)

                if (opType == "check") {
                    todoBtn.className = "btn btn-success"
                    todoBtn.setAttribute("onClick", `toggleTodo('${pk}', 'uncheck', 'detail-view')`)
                    document.getElementById("completed-small-text-hidden").style.display = "block"
                    document.getElementById("completed-small-text-hidden").innerHTML =
                    `
                    Completed on: ${json.todo_date_completed}
                    `
                    todoTitle.innerHTML =
                    `
                    <s>${json.todo_title}</s>
                    `
                }

                else if (opType == "uncheck") {
                    todoBtn.className = "btn btn-outline-success"
                    todoBtn.setAttribute("onClick", `toggleTodo('${pk}', 'check', 'detail-view')`)
                    todoTitle.innerHTML =
                    `
                    ${json.todo_title}
                    `
                    document.getElementById("completed-small-text-hidden").style.display = "none"
                    document.getElementById("completed-small-text").style.display = "none"
                }
            }

            else if (fromView == "other") {
                // "other" could be two places: from Important view for Next-Up view
                // our logic will be same for both
                document.getElementById(`todo-title-${pk}`).innerHTML = `<s>${json.todo_title}</s>`
                document.getElementById(`todo-item-${pk}`).style.display = "none"
            }
        },
    });
}

function toggleSubtask(pk, opType) { // opType = Operation Type
    $.ajax({
        url: subtask_toggle_url, // the endpoint
        type: "POST", // http method
        data: { "pk": pk }, // data sent with the get request
        dataType: 'json',

        // handle a successful response
        success: function (json) {
            console.log("successful operation"); // another sanity check
            let percentage = json.percentage
            console.log(percentage)

            if (json.percentage == 0) {
                document.getElementById("progress").style.display = "none"
                document.getElementById("percentage").style.display = "none"
            }

            else {
                document.getElementById("progress").style.display = "block"
                document.getElementById("percentage").style.display = "block"
                document.getElementById("percentage").innerHTML = percentage + "%"
            }

        },
    });

    let subtaskBtn = document.getElementById(`subtask-btn-${pk}`)
    let subtaskTitle = document.getElementById(`subtask-title-${pk}`)
    if (opType == "check") {
        subtaskBtn.className = "btn btn-success"
        subtaskBtn.setAttribute("onClick", `toggleSubtask(${pk}, 'uncheck')`)
        subtaskTitle.style.textDecoration = "line-through"
    }
    else {
        subtaskBtn.className = "btn btn-outline-success"
        subtaskBtn.setAttribute("onClick", `toggleSubtask(${pk}, 'check')`)
        subtaskTitle.style.textDecoration = "none"
    }

}

function deleteItem(item_type, pk) {
    $.ajax({
        url: delete_url, // the endpoint
        type: "POST", // http method
        data: {
            pk: pk,
            item_type: item_type
        }, // data sent with the get request

        // handle a successful response
        success: function (json) {
            console.log("success"); // another sanity check
            if (json.hide_heading == "yes") {
                document.getElementById("subtask-heading").style.display = "none"
            }
        },
    });

    if (item_type == "subtask") {
        let subtaskList = document.getElementById(`subtask-items-${pk}`)
        subtaskList.style.display = "none"
    }

    else if (item_type == "notes") {
        document.getElementById("notes").style.display = "none"
        document.getElementById("notes-input").style.display = "block"
    }

    else if (item_type == "todo") {
        document.getElementById(`todo-item-${pk}`).style.display = "none"
    }

    else if (item_type == "tasklist") {
        document.getElementById(`tasklist-item-${pk}`).style.display = "none"
    }

    else if (item_type == "due_date") {
        document.getElementById("due-date-input").style.display = "block"
        document.getElementById("due-date-content").style.display = "none"
    }
}


// Following functions will handle async form submission with AJAX
// Starts
function createTask() {
    $.ajax({
        url: create_url, // the endpoint
        type: "POST", // http method
        data: {
            title: $('#input-todo').val(),
            parent_list: document.getElementById("hidden-parent-list").innerHTML,
            item_type: "todo"
        }, // data sent with the post request
        dataType: 'json',

        // handle a successful response
        success: function (json) {
            $('#input-todo').val(''); // remove the value from the input
            console.log("success"); // another sanity check
            document.getElementById("todo-list").style.display = "block"
            $('#todo-list').prepend(
                `
                <li id="todo-item-${json.todo_pk}" class="list-group-item dark-mode-assist-section big-list-item">
                <button style="float:left" onclick="toggleTodo('${json.todo_pk}', 'check', 'single-view')"
                class="btn btn-outline-success">
                    <i class="fa fa-check"></i>
                </button>
                <a style="margin-left: 7px; color:inherit; text-decoration: none; font-size: 2.5ch;"
                href="/todo/${json.todo_title}/${json.todo_pk}"> 
                    ${json.todo_title}
                </a>
                <button onclick="deleteItem('todo', ${json.todo_pk})" style="float: right;"
                class="btn btn-outline-danger">
                    <i class="fas fa-trash"></i>
                </button>
                <button id="todo-important-${json.todo_pk}" onclick="toggleImportant('${json.todo_pk}', 'mark')"
                style="float: right; margin-right:3px" class="btn btn-secondary">
                    <i class="fas fa-star"></i>
                </button>
                `
            )
        },
    });
}

function createSubtask() {
    $.ajax({
        url: create_url, // the endpoint
        type: "POST", // http method
        data: {
            title: $("#input-subtask").val(),
            parent_task_pk: document.getElementById("hidden-parent-task-pk").innerHTML,
            item_type: "subtask"
        }, // data sent with the get request
        dataType: "json",

        // handle a successful response+
        success: function (json) {
            $("#input-subtask").val('') // remove the value from the input
            console.log("success"); // another sanity check
            document.getElementById("subtask-list").style.display = "block"
            document.getElementById("subtask-heading").style.display = "block"
            document.getElementById("subtask-heading").innerHTML = "Subtasks for this task"
            $('#subtask-list').append(
                `
                <li class="content-section" id="subtask-items-${json.subtask_pk}" style="font-size: 23px;">
                    <button id="subtask-btn-${json.subtask_pk}" onclick="toggleSubtask('${json.subtask_pk}', 'check')"
                        class="btn btn-outline-success">
                        <i class="fa fa-check"></i>
                    </button>
                    <a id="subtask-title-${json.subtask_pk}" style="color:inherit; text-decoration: none;" href="/todo/edit_subtask/${json.subtask_pk}">
                        ${json.subtask_title}
                    </a>
                    <button onclick="deleteItem('subtask', '${json.subtask_pk}')" type="submit" 
                        style="float: right;" class="btn btn-outline-danger"><i class="fas fa-trash"></i>
                    </button>
                </li>
                `
            )
        },
    });
}

function createNote() {
    $.ajax({
        url: create_url, // the endpoint
        type: "POST", // http method
        data: {
            content: $("#input-notes").val(),
            parent_task_pk: document.getElementById("hidden-parent-task-pk").innerHTML,
            item_type: "notes"
        }, // data sent with the get request

        // handle a successful response
        success: function (json) {
            console.log("notes are added: " + $("#input-notes").val().toString()); // another sanity check
            $("#input-notes").val('') // remove the value from the input
            document.getElementById("notes-input").style.display = "none"
            document.getElementById("notes").style.display = "block"
            document.getElementById("notes-content").innerHTML =
                `
            <br>
            <div style="font-family:Candara">${json.note_content}</div>
            <br>
            <button style="font-size: 2ch" class="btn btn-outline-danger" type="submit"
                onclick="deleteItem('notes', '${json.note_pk}')"><i class="fas fa-trash"></i></button>
            <button style="font-size: 2ch" class="btn btn-outline-info" type="submit"
                onclick="location.href='/todo/edit_notes/${json.note_pk}'">
                <i class="fas fa-pencil-alt"></i>
            </button>
            `
            document.getElementById("notes-metadata").innerHTML =
                `
            <br>
            Notes added on: <b>${json.note_created}</b>
            `
        },
    });
}

function createDueDate() {
    $.ajax({
        url: create_url, // the endpoint
        type: "POST", // http method
        data: {
            due_date: $("#input-due-date").val(),
            parent_task_pk: document.getElementById("hidden-parent-task-pk").innerHTML,
            item_type: "due_date"
        }, // data sent with the get request

        // handle a successful response
        success: function (json) {
            console.log("due date added: " + $("#input-due-date").val().toString()); // another sanity check
            $("#input-notes").val('') // remove the value from the input
            document.getElementById("due-date-content").style.display = "block"
            document.getElementById("due-date-content").style.color = json.due_date_color
            document.getElementById("due-date-content").innerHTML =
                `
            Due on: ${json.due_date}
            <button onclick="deleteItem('due_date', ${json.parent_task_pk})" class="btn btn-outline-danger">
                <i class="fa fa-trash">
                </i>
            </button>
            `
            document.getElementById("due-date-input").style.display = "none"
        },
    });
}

$('#todo-add-form').on('submit', function (event) {
    event.preventDefault();
    console.log("ToDo form submitted")  // sanity check
    console.log(document.getElementById("hidden-parent-list").innerHTML)
    createTask();
});

$('#subtask-add-form').on('submit', function (event) {
    event.preventDefault();
    console.log("SubTask form submitted")  // sanity check
    console.log(document.getElementById("hidden-parent-task-pk").innerHTML)
    createSubtask();
});

$('#notes-add-form').on('submit', function (event) {
    event.preventDefault();
    console.log("Notes form submitted")  // sanity check
    console.log(document.getElementById("hidden-parent-task-pk").innerHTML)
    createNote();
});

$('#due-date-add-form').on('submit', function (event) {
    event.preventDefault();
    console.log("Due Date submitted")  // sanity check
    console.log(document.getElementById("hidden-parent-task-pk").innerHTML)
    createDueDate();
});


// Ends

function subtract(val1, val2, htmlElementId) {
    let ans = val1 - val2
    document.getElementById(htmlElementId).innerHTML = ans;
}

function animateValue(id, start, end, duration) {
    var range = end - start;
    var current = start;
    var increment = end > start ? 1 : -1;
    var stepTime = Math.abs(Math.floor(duration / range));
    var obj = document.getElementById(id);
    var timer = setInterval(function () {
        current += increment;
        obj.innerHTML = current;
        if (current == end) {
            clearInterval(timer);
        }
    }, stepTime);
}

// JS code from https://github.com/realpython/django-form-fun/blob/master/part1/main.js for handling backend CSRF security tokens

$(function () {

    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
