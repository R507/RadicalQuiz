"""Exam app admin"""

# pylint: disable = missing-docstring
# pylint: disable = no-member
# pylint: disable = too-few-public-methods

import nested_admin
from django.contrib import admin

from .models import Quiz, Question, Option


class OptionInLine(nested_admin.NestedTabularInline):
    model = Option
    extra = 2


class QuestionInLine(nested_admin.NestedStackedInline):
    model = Question
    inlines = [OptionInLine]
    extra = 1


class QuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInLine]


admin.site.register(Quiz, QuizAdmin)
