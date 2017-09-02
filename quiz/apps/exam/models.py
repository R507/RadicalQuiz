"""Exam app models"""

from django.contrib.auth.models import User
from django.db import models


class Quiz(models.Model):
    """Quiz model contains questions"""
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    """Radio question model contains options"""
    # might make sense to make this model resemble generic question,
    # and have one to one relation to question details, which would
    # differ by types, i.e. radio choice, multiple choice, etc.
    # in case if different question types would be needed
    question_text = models.CharField(max_length=500)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text

    def get_options(self):
        """Get question options"""
        return self.option_set.all()


class Option(models.Model):
    """Option of a question"""
    option_text = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.option_text


class Take(models.Model):
    """Entity containing answers for a quiz

    Used to track user progress in a quiz and for results calculation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'quiz',)

    @classmethod
    def get_or_create(cls, user, quiz):
        """Get or create take by user and quiz"""
        take = cls.objects.get_or_create(user=user, quiz=quiz)
        return take[0]  # was object created or not is not relevant

    def get_current_question(self):
        """Returns first unanswered question sorted by id, if any, else None"""
        all_questions = set(self.quiz.question_set.all())
        answers = self.answer_set.all()
        answered_questions = {answer.question for answer in answers}
        unanswered_questions = all_questions - answered_questions
        current_question = (
            sorted(unanswered_questions, key=lambda q: q.id)[0]
            if unanswered_questions
            else None
        )
        return current_question

    def get_quiz_results(self):
        """Returns results for quiz"""
        total_questions_amount = self.quiz.question_set.count()
        answers = self.answer_set.all()
        correct_questions_amount = sum(
            answer.is_correct()
            for answer in answers
        )
        incorrect_questions_amount = sum(
            not answer.is_correct()
            for answer in answers
        )
        percentage_correct = int(
            correct_questions_amount * 100 / total_questions_amount
            if total_questions_amount  # No zero division on my watch
            else 0
        )
        return (
            total_questions_amount,
            correct_questions_amount,
            incorrect_questions_amount,
            percentage_correct,
        )


class Answer(models.Model):
    """Answer for a radio question"""
    take = models.ForeignKey(Take, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_option = models.ForeignKey(Option, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('take', 'question',)

    def is_correct(self):
        """Is this answer correct"""
        return self.chosen_option.is_correct
