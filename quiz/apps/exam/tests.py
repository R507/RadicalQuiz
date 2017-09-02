"""Exam app tests"""
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from . import forms
from . import models
from . import views


# pylint: disable = no-self-use


class QuestionModelTests(TestCase):
    """Question model tests"""

    def test_get_options(self):
        """Test that get options returns all options for the question"""
        quiz = models.Quiz.objects.create(name='quiz')
        question = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        option_1 = models.Option.objects.create(
            option_text='option_text 1',
            is_correct=True,
            question=question,
        )
        option_2 = models.Option.objects.create(
            option_text='option_text 2',
            is_correct=False,
            question=question,
        )

        options = set(question.get_options())
        expected_optinos = {option_1, option_2}
        assert options == expected_optinos


class TakeModelTests(TestCase):
    """Take model tests"""

    def test_get_or_create(self):
        """On first call take should be created, on next returned the same"""
        user = User.objects.create_user(
            username='whatever',
            email='whatever@whatever.org',
            password='whatever_very_secure_pass',
        )
        quiz = models.Quiz.objects.create(name='quiz')

        take_1 = models.Take.get_or_create(user=user, quiz=quiz)

        take_2 = models.Take.get_or_create(user=user, quiz=quiz)

        assert take_1.pk == take_2.pk

    def test_get_current_question(self):
        """Test get current question

        Should return yet unanswered questions, in whatever order, and None
        if none left"""
        user = User.objects.create_user(
            username='whatever',
            email='whatever@whatever.org',
            password='whatever_very_secure_pass',
        )
        quiz = models.Quiz.objects.create(name='quiz')
        question_1 = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        models.Option.objects.create(
            option_text='option_text',
            is_correct=True,
            question=question_1,
        )
        question_2 = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        models.Option.objects.create(
            option_text='option_text',
            is_correct=True,
            question=question_2,
        )
        question_3 = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        models.Option.objects.create(
            option_text='option_text',
            is_correct=True,
            question=question_3,
        )
        expected_questions = {question_1, question_2, question_3}
        take = models.Take.get_or_create(user=user, quiz=quiz)
        while True:
            current_question = take.get_current_question()
            if current_question is None:
                break
            assert current_question in expected_questions
            models.Answer.objects.create(
                take=take,
                question=current_question,
                chosen_option=current_question.option_set.first(),
            )
            expected_questions.remove(current_question)
        assert not expected_questions

    def test_get_quiz_results(self):
        """Test get quiz results

        Get quiz results method returns:
        Total questions amount (in quiz)
        Correct answers amount
        Incorrect answers amount
        Percentage of correct answers - compared to total questions,
            0 if no asnwers
        """
        user = User.objects.create_user(
            username='whatever',
            email='whatever@whatever.org',
            password='whatever_very_secure_pass',
        )
        quiz = models.Quiz.objects.create(name='quiz')
        take = models.Take.get_or_create(user=user, quiz=quiz)
        # should work even if there a no questions in quiz
        results = take.get_quiz_results()
        assert results == (0, 0, 0, 0)

        # add a question
        question_1 = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        models.Option.objects.create(
            option_text='option_text',
            is_correct=True,
            question=question_1,
        )

        results = take.get_quiz_results()
        assert results == (1, 0, 0, 0)

        # add correct answer to added question
        models.Answer.objects.create(
            take=take,
            question=question_1,
            chosen_option=question_1.option_set.first(),
        )

        results = take.get_quiz_results()
        assert results == (1, 1, 0, 100)

        # add a question
        question_2 = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        models.Option.objects.create(
            option_text='option_text',
            is_correct=False,
            question=question_2,
        )

        results = take.get_quiz_results()
        assert results == (2, 1, 0, 50)

        # add incorrect answer to added question
        models.Answer.objects.create(
            take=take,
            question=question_2,
            chosen_option=question_2.option_set.first(),
        )

        results = take.get_quiz_results()
        assert results == (2, 1, 1, 50)


class AnswerModelTests(TestCase):
    """Answer model tests"""

    def test_is_correct(self):
        """Check that is correct returns correct values"""
        user = User.objects.create_user(
            username='whatever',
            email='whatever@whatever.org',
            password='whatever_very_secure_pass',
        )
        quiz = models.Quiz.objects.create(name='quiz')
        question = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        correct_option = models.Option.objects.create(
            option_text='option_text',
            is_correct=True,
            question=question,
        )
        incorrect_option = models.Option.objects.create(
            option_text='option_text',
            is_correct=False,
            question=question,
        )
        take = models.Take.get_or_create(user=user, quiz=quiz)
        correct_answer = models.Answer(
            take=take,
            question=question,
            chosen_option=correct_option,
        )
        assert correct_answer.is_correct() is True

        incorrect_answer = models.Answer(
            take=take,
            question=question,
            chosen_option=incorrect_option,
        )
        assert incorrect_answer.is_correct() is False


class RadioQuestionFormTests(TestCase):
    """Radio Question form tests"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_chosen_option(self):
        """Test that get options returns all options for the question"""
        quiz = models.Quiz.objects.create(name='quiz')
        question = models.Question.objects.create(
            question_text='question_text',
            quiz=quiz,
        )
        option = models.Option.objects.create(
            option_text='option_text 1',
            is_correct=True,
            question=question,
        )
        models.Option.objects.create(
            option_text='option_text 2',
            is_correct=False,
            question=question,
        )
        quiz_link = reverse('exam:quiz', kwargs={'quiz_id': quiz.pk})
        request = self.factory.post(
            quiz_link,
            {forms.RadioQuestionForm.RADIO_OPTIONS: [str(option.pk)]},
        )
        forms.RadioQuestionForm(question)
        # probably there is a better way to get proper POST structure
        form = forms.RadioQuestionForm(question, request.POST)
        assert form.is_valid()
        chosen_option = form.get_chosen_option()
        assert chosen_option == option


class ViewsBehaviorTests(TestCase):
    """Views tests"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='whatever',
            email='whatever@whatever.org',
            password='whatever_very_secure_pass',
        )
        quiz_1 = models.Quiz.objects.create(name='quiz_1')
        question_11 = models.Question.objects.create(
            question_text='question_text1',
            quiz=quiz_1,
        )
        models.Option.objects.create(
            option_text='option_text1',
            is_correct=True,
            question=question_11,
        )
        models.Option.objects.create(
            option_text='option_text2',
            is_correct=False,
            question=question_11,
        )
        question_12 = models.Question.objects.create(
            question_text='question_text2',
            quiz=quiz_1,
        )
        models.Option.objects.create(
            option_text='option_text3',
            is_correct=True,
            question=question_12,
        )
        models.Option.objects.create(
            option_text='option_text4',
            is_correct=False,
            question=question_12,
        )
        quiz_2 = models.Quiz.objects.create(name='quiz_2')
        question_21 = models.Question.objects.create(
            question_text='question_text3',
            quiz=quiz_2,
        )
        models.Option.objects.create(
            option_text='option_text5',
            is_correct=True,
            question=question_21,
        )
        models.Option.objects.create(
            option_text='option_text6',
            is_correct=False,
            question=question_21,
        )

    def test_index(self):
        """Test index view, it should display links to all available quizzes"""
        request = self.factory.get(reverse('exam:index'))
        request.user = self.user
        response = views.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        # content should contain links for each quiz
        for quiz in models.Quiz.objects.all():
            name = quiz.name
            url = reverse('exam:quiz', kwargs={'quiz_id': quiz.id})
            link = '<li><a href="{url}">{name}</a></li>'.format(
                url=url,
                name=name,
            )
            self.assertContains(response, link)

    def test_quiz(self):
        """Test quiz view

        On get it displays current question if any, results otherwise.
        On set it saves chosen option and redirects to quiz get.
        """
        # there's probably a room for improvement in this test
        quiz_id = 1
        quiz_link = reverse('exam:quiz', kwargs={'quiz_id': quiz_id})
        request = self.factory.get(quiz_link)
        request.user = self.user
        response = views.QuizView.as_view()(request, quiz_id)
        self.assertEqual(response.status_code, 200)
        request = self.factory.post(
            quiz_link, {forms.RadioQuestionForm.RADIO_OPTIONS: ['1']})
        request.user = self.user
        response = views.QuizView.as_view()(request, quiz_id)
        self.assertEqual(response.status_code, 302)
        request = self.factory.post(
            quiz_link, {forms.RadioQuestionForm.RADIO_OPTIONS: ['999']})
        # non-existent option, in case this happens somehow
        request.user = self.user
        response = views.QuizView.as_view()(request, quiz_id)
        self.assertEqual(response.status_code, 200)
        request = self.factory.post(
            quiz_link, {forms.RadioQuestionForm.RADIO_OPTIONS: ['3']})
        # a bit of a dirty hack, but second question contains options with
        # id 3 and 4
        request.user = self.user
        response = views.QuizView.as_view()(request, quiz_id)
        self.assertEqual(response.status_code, 302)
        # all questions answered, view should return results
        request = self.factory.get(quiz_link)
        request.user = self.user
        response = views.QuizView.as_view()(request, quiz_id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quiz results:')

    def test_clear(self):
        """Test clear view

        On get it clears saved quiz answers and redirects to quiz"""
        # there's probably a room for improvement in this test too
        quiz_id = 2
        clear_link = reverse('exam:clear', kwargs={'quiz_id': quiz_id})
        request = self.factory.get(clear_link)
        request.user = self.user
        response = views.ClearAnswersView.as_view()(request, quiz_id)
        self.assertEqual(response.status_code, 302)
        # makes sense to add take for quiz and check that it is indeed deleted


class LoginRequiredTests(TestCase):
    """Tests for certain views which require login"""

    def _get_login_url(self, initial_url=None):
        """Get expected redirect login url"""
        login_url = settings.LOGIN_URL  # not sure if it's a correct way
        # to get the default login url
        retval = (
            '{}?next={}'.format(login_url, initial_url)
            if initial_url
            else login_url
        )
        return retval

    def _test_login_required(self, url):
        """Parametrized helper test"""
        response = self.client.get(url)
        expected_url = self._get_login_url(url)
        self.assertRedirects(
            response=response,
            expected_url=expected_url,
            status_code=302,
            target_status_code=200)

    def test_login_required(self):
        """Test that views which require login, can't be accessed without it"""
        self._test_login_required(reverse('exam:index'))
        self._test_login_required(reverse('exam:quiz', kwargs={'quiz_id': 1}))
        self._test_login_required(reverse('exam:clear', kwargs={'quiz_id': 1}))
