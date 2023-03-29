import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)
        
    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
        
    def create_question(question_text, days):
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)
    
    class QuestionIndexViewTests(TestCase):
        def test_no_questions(self):
            """
            만약 질문 내역이 없다면 적절한 메세지가 표시되어야한다.
            """
            response = self.client.get(reverse('polls:index'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "No polls are available.")
            self.assertQuerysetEqual(response.context['latest_question_list'], [])
            
        def test_past_question(self):
            """
            과거에 pub_date가 있는 질문은 다음 페이지에 표시됩니다
            """
            question = create_question(qustion_text="Past question.", days=-30)
            response = self.client.get(reverse('polls:index'))
            self.assertQuerysetEqual(
                response.context['latest_question_list'],
                [question],
            )
        
        def test_future_question(self):
            """
            이후 pub_date가 있는 질문은 인덱스 페이지에 표시되지 않습니다.
            """
            create_question(question_text="Future question.", days=30)
            response = self.client.get(reverse('polls:index'))
            self.assertContains(response, "No polls are available.")
            self.assertQuerysetEqual(response.context['latest_question_list'], [])
        
        def test_future_question_and_past_question(self):
            """
            과거 질문과 미래 질문이 모두 있는 경우에도 과거 질문만 표시됩니다.
            """
            question = create_question(question_text="Past question.", days=-30)
            create_question(question_text="Future question.", days=30)
            response = self.client.get(reverse('polls:index'))
            self.assertQuerysetEqual(
                response.context['latest_question_list'],
                [question]
            )
        
        def test_two_past_questions(self):
            """
            질문 페이지에 여러개의 질문이 표시되었을 확인하는 코드입니다.
            """
            
