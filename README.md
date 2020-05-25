# The 2.0 version of this app is now fully alive and developed with <3

This is the repo of the 2.0 version of my to-do list app. The app was taken down from PythonAnywhere servers and I developed it locally. In the previous version, the app was
really simple and had several security holes. I have re-written the infrastructure of the app and every part of the app was
re-developed. It is now a not-so-simple app with some decently awesome features and all those security vulnerabilities were 
patched.

![A demo image of the ToDo App Home Page](/project_images/app_glance.png)

## Awesome features of the app

* Access your tasks anywhere, even on mobile.
* Create Lists
* In those Lists, create ToDos
* Those ToDos can contain
  * Subtasks
  * Notes
  * Due Dates
  * Attachments
* Powerful Search feature to look for anything.
* Smart Pages like "Important", "Next Up" and "Your Files".
* App has a feature called Insights, which is really powerful and every week gives the user a report of how productive they were. It also uses Matplotlib to plot graphs to show the user. Neat!
* The app has Dark Mode which looks stunning!
* Bootstrap CSS has been used to make the app look and feel Premium and Beautiful.
* The app has AJAX support baked in so that almost all the operations in the app is now Asynchronous, no reloads ever!
* The app has native support for all Timezones across the world so anyone from anywhere can use the app in their local time so that it works best for all users.
* Security checks on every operation to restrict unauthorized usage.
* Hosted on PythonAnywhere cloud servers (huge thanks)

## Dependencies used

My to-do list app uses these amazing reusable and awesome apps/dependencies to power some backend operations

* [Django](https://github.com/django/django)
* [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms)
* [django-user_agents](https://github.com/selwin/django-user_agents)
* [django-timezone-field](https://github.com/mfogel/django-timezone-field)
* [django-cleanup](https://github.com/un1t/django-cleanup)
* [Pillow](https://github.com/python-pillow/Pillow)
* [Matplotlib](https://github.com/matplotlib/matplotlib)
* [Seaborn](https://github.com/mwaskom/seaborn)
* [Numpy](https://github.com/numpy/numpy) *Required by Matplotlib*
* [Pandas](https://github.com/pandas-dev/pandas) *Required by Seaborn*
* [Awesome code snippet that handles AJAX Post form submissions](https://github.com/realpython/django-form-fun/blob/master/part1/main.js)

On the front end, the app uses these technologies

* HTML, CSS
* JavaScript
* AJAX
* [Bootstrap CSS](https://github.com/twbs/bootstrap)
* [Google Fonts](https://github.com/google/fonts)
* [Font-Awesome](https://github.com/FortAwesome/Font-Awesome)

Production dependencies used on PythonAnywhere

* [python-dotenv](https://github.com/theskumar/python-dotenv)

******************************************************************************************************************************

***The 1.0 version of this app is still available as legacy code here: [1.0 version](https://github.com/arafat-ar13/Regular-ToDoList-legacy-code-1.0)***

***I have not put the SQLite database and the "media" directory which contains all sensitive user items like profile pictures and task attachments under source control/git for obvious security reasons. They are hosted directly on PythonAnywhere servers***
