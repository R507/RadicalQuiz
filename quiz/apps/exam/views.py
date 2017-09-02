"""Exam app views"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import RadioQuestionForm
from .models import Quiz, Take, Answer


class GenericQuizView(LoginRequiredMixin, View):
    """Generic quiz view, containing common quiz specific stuff

    Intended to be used for every quiz related view"""
    TEMPLATE_INDEX = 'exam/index.html'
    TEMPLATE_RESULTS = 'exam/results.html'
    TEMPLATE_QUESTION = 'exam/question.html'
    LINK_QUIZ = 'exam:quiz'

    @staticmethod
    def get_take(request, quiz_id):
        """Returns take for current user, current quiz"""
        user = request.user
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        take = Take.get_or_create(user=user, quiz=quiz)
        return take


class IndexView(GenericQuizView):
    """Simply displays list of links to all available quizzes"""
    # might make sense to make it a generic list view
    def get(self, request):
        """Process get request"""
        quizzes = Quiz.objects.order_by('-pk')
        context = {
            'quizzes': quizzes,
        }
        return render(request, self.TEMPLATE_INDEX, context)


class QuizView(GenericQuizView):
    """Displays unanswered question, if any left, results otherwise.

    Handles GET/POST for questions and shows results for specified quiz.
    User should not have an ability to skip questions and see results only
    when answered all the questions, so it makes sense to deny the user
    the ability to access questions and results by ids/names in url.
    """

    @classmethod
    def process_question_render(cls, request, quiz_id, current_question):
        """Collect context and process question page render"""
        # might make sense to check if question has no options
        form = RadioQuestionForm(current_question)
        context = {
            'quiz_id': quiz_id,
            'form': form,
        }
        retval = render(request, cls.TEMPLATE_QUESTION, context)
        return retval

    @classmethod
    def process_results_render(cls, request, quiz_id, take):
        """Collect context and process results page render"""
        (
            total_questions_amount,
            correct_questions_amount,
            incorrect_questions_amount,
            percentage_correct,
        ) = take.get_quiz_results()
        context = {
            'right_answers': correct_questions_amount,
            'wrong_answers': incorrect_questions_amount,
            'right_percentage': percentage_correct,
            'total_questions': total_questions_amount,
            'quiz_id': quiz_id,
        }
        retval = render(request, cls.TEMPLATE_RESULTS, context)
        return retval

    def get(self, request, quiz_id):
        """Process get request"""
        take = self.get_take(request, quiz_id)

        current_question = take.get_current_question()

        if current_question:
            retval = self.process_question_render(
                request, quiz_id, current_question)
        else:
            retval = self.process_results_render(request, quiz_id, take)
        return retval

    def post(self, request, quiz_id):
        """Process post request"""
        take = self.get_take(request, quiz_id)

        current_question = take.get_current_question()
        if not current_question:
            # this should not happen, unless somebody doing some hacking
            return redirect(self.LINK_QUIZ, quiz_id=quiz_id)

        form = RadioQuestionForm(current_question, request.POST)
        if form.is_valid():
            chosen_option = form.get_chosen_option()
            answer = Answer(
                take=take,
                question=current_question,
                chosen_option=chosen_option,
            )
            answer.save()
            retval = redirect(self.LINK_QUIZ, quiz_id=quiz_id)
        else:
            context = {
                'quiz_id': quiz_id,
                'form': form,
            }
            retval = render(request, self.TEMPLATE_QUESTION, context)
        return retval


class ClearAnswersView(GenericQuizView):
    """Clear results/info about answered questions

    Wipes info about already answered questions, allowing to take quiz again"""
    def get(self, request, quiz_id):
        """Process get request"""
        take = self.get_take(request, quiz_id)
        take.delete()
        retval = redirect(self.LINK_QUIZ, quiz_id=quiz_id)
        return retval
