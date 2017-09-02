"""Exam app urls"""
from django.conf.urls import url

from quiz.apps.exam import views


app_name = 'exam'  # pylint: disable = invalid-name

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<quiz_id>\d+)/$',
        views.QuizView.as_view(), name='quiz'),
    url(r'^(?P<quiz_id>\d+)/clear/$',
        views.ClearAnswersView.as_view(), name='clear'),
]
