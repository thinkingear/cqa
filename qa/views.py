from django.shortcuts import redirect, render
from .forms import AnswerForm
from .models import Question, QuestionTag
from core.views import content_follow, tags_handler
from django.views.decorators.csrf import csrf_exempt
import re
import openai
from django.conf import settings
from django.http import JsonResponse
import json

# Create your views here.


def question_create_page(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if not title.endswith('?'):
            title += '?'
        title = re.sub(r'\?+$', '?', title)

        Question.objects.create(
            title=title,
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


@csrf_exempt
def question_follow(request):
    # check the questionfollower does exist
    return content_follow(request, 'question', 'questionfollower')


@csrf_exempt
def answer_follow(request):
    return content_follow(request, 'answer', 'answerfollower')


@csrf_exempt
def question_tags_handler(request):
    return tags_handler(request, Question, QuestionTag)


def _generate_answer(prompt):
    openai.api_key = settings.OPENAI_API_KEY

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\".\n\nQ: What is human life expectancy in the United States?\nA: Human life expectancy in the United States is 78 years.\n\nQ: Who was president of the United States in 1955?\nA: Dwight D. Eisenhower was president of the United States in 1955.\n\nQ: Which party did he belong to?\nA: He belonged to the Republican Party.\n\nQ: What is the square root of banana?\nA: Unknown\n\nQ: How does a telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n\nQ: Where were the 1992 Olympics held?\nA: The 1992 Olympics were held in Barcelona, Spain.\n\nQ: How many squigs are in a bonk?\nA: Unknown\n\nQ: {prompt}\nA:",
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"]
    )

    answer = response.choices[0].text.strip()
    return answer


def contains_profanity(text):
    for profanity in settings.PROFANITY_LIST:
        if re.search(profanity, text, re.IGNORECASE):
            return True
    return False


@csrf_exempt
def generate_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data['question']
        if contains_profanity(question):
            return JsonResponse({
                'status': 'success',
                'answer': 'Unknown',
            })

        answer = _generate_answer(question)
        if contains_profanity(answer):
            return JsonResponse({
                'status': 'success',
                'answer': 'Unknown',
            })
        return JsonResponse({
            'status': 'success',
            'answer': answer,
        })

