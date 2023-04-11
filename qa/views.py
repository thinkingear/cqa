from django.shortcuts import redirect, render
from .forms import QuestionForm, AnswerForm
from .models import Question

# Create your views here.


def question_create_page(request):
    if request.method == 'POST':
        Question.objects.create(
            title=request.POST.get('title') + '?',
            poster=request.user,
        )
        return redirect('core:home')

    return render(request, 'qa/question_create.html')


def answer_create_page(request, pk):
    question = Question.objects.get(id=pk)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        answer = form.save(commit=False)
        answer.question = question
        answer.poster = request.user
        answer.save()
        return redirect('core:home')

    form = AnswerForm()
    context = {'question': question, 'form': form}
    return render(request, 'qa/answer_create.html', context)


def question_detial(request, pk):
    question = Question.objects.get(id=pk)
    answers = question.answers.all()
    context = {'question': question, 'answers': answers}
    return render(request, 'qa/question.html', context)
