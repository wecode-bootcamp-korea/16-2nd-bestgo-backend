import os
import django
import csv
import sys

from django.core.wsgi       import get_wsgi_application
application = get_wsgi_application()

from services.models import Question, QuestionChoice

os.environ.setdefault("DJANGO_SETTINGS_MODULE","bestgo.settings")
django.setup()


CSV_PATH_QUESTIONS = './questions.csv'

with open(CSV_PATH_QUESTIONS) as in_file:
    data_reader = csv.reader(in_file)
    next(data_reader,None)
    for row in data_reader:
        which_question = row[0]
        if not Question.objects.filter(name=which_question).exists():
            Question.objects.create(name =which_question)
        from_question = Question.objects.get(name=row[0])
        QuestionChoice.objects.create(question=from_question, choice=row[1])
