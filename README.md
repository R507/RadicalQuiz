# README #

## Radical Quiz


**Note**: this is a somewhat basic project and might be not the one
you're looking for.

This is a django based web service which provides a functionality
to create and participate in various quizzes.

Functionality is provided only to registered users.
Any registered user have all existing quizzes available to participate in.
After answering all the questions results window shows amount of successful
and failed questions and allow to try again.

#### Contents:
* quiz - main platform
* quiz.apps.exam - app which provides quizzes functionality
* quiz.apps.rt_auth - custom auth app, which is basically existing django/django
  registration functionality mapped on templates

#### How to use it:
Deploy wherever, or just try with debug config:
* install requirements - 'pip install -r requirements.txt'
* configure settings.py/settings_local.py as needed, if needed
* migrate - 'python manage.py migrate'
* create admin user - 'python manage.py createsuperuser'
* run with debug config - 'python manage.py runserver'
* go to web ui, figure out the rest from there
