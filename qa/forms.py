from django.forms import ModelForm
from .models import Question, Answer


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        exclude = ['questioner']


class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ['feed']
