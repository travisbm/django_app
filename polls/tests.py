import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from .models import Question

class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return false for questions
        whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return false for questions
        whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return true for questions
        whose pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)

def create_question(question_text, days, choice):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    if choice:
        question.choice_set.create(choice_text="Sample text.", votes=0)
    return question

class QuestionViewTests(TestCase):

    def test_index_view_with_no_question(self):
        """
        If no questions exist an appropriate message should be diplayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Future question.", days=30, choice=True)
        create_question(question_text="Past question.", days=-30, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30, choice=True)
        create_question(question_text="Past question 2.", days=-30, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_index_with_question_that_has_no_choices(self):
        """
        Questions from the past, with no choices, should not be displayed.
        """
        create_question(question_text="Question with no choices.", days=-3, choice=False)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_with_question_with_choice_and_question_without_choice(self):
        """
        Questions from the past, with choices, should be displayed.
        """
        create_question(question_text="Question with a choice.", days=-3, choice=True)
        create_question(question_text="Question with no choices.", days=-3, choice=False)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Question with a choice.>']
        )

class QuestionDetailIndexTest(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5, choice=True)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text="Past question.", days=-5, choice=True)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionResultsIndexTest(TestCase):
    def test_results_view_with_a_future_question(self):
        """
        The results view of a question with a pub_date in the future should
        return a 404 not found
        """
        future_question = create_question(question_text="Future question.", days=5, choice=True)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        """
        The results view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text="Past question.", days=-5, choice=True)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
