import random

from exam.models import Question


def get_random_questions(num_questions, exam_id):
    questions = list(Question.objects.filter(is_active=True, exam_id=exam_id))
    random.shuffle(questions)
    return questions[:num_questions]


def get_random_questions_count(exam_id):
    questions = list(Question.objects.filter(is_active=True, exam_id=exam_id))
    return len(questions)
