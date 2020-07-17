#! /usr/bin/python3
# -*- coding:utf-8
# __author__ = '__Levvl__'

from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, DetailView

from zanhu.helpers import ajax_required
from zanhu.qa.models import Question, Answer
from zanhu.qa.forms import QuestionForm


class QuestionListView(LoginRequiredMixin, ListView):
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa/question_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['popular_tags'] = Question.objects.get_counted_tags()
        context['active'] = "all"
        return context


class AnsweredQuestionListView(QuestionListView):
    def get_queryset(self):
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['active'] = "answered"
        return context


class UnAnsweredQuestionListView(QuestionListView):
    def get_queryset(self):
        return Question.objects.get_ununswered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['active'] = "unanswered"
        return context

class QuestionCreateView(LoginRequiredMixin,CreateView):
    form_class = QuestionForm
    template_name = 'qa/question_form.html'
    message = "问题已提交"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('qa:unanswered_q')

class QuestionDetailView(LoginRequiredMixin,DetailView):
    model = Question
    context_object_name = 'question'
    template_name = 'qa/question_detail.html'


class AnswerCreateView(LoginRequiredMixin,CreateView):
    """回答问题"""
    model = Answer
    fields = ['content',]
    message = '你的问题已提交'
    template_name = 'qa/answer_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs['question_id']
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('qa:question_detail',kwargs={"pk":self.kwargs['question_id']})

@login_required
@ajax_required
@require_http_methods(['POST'])
def question_vote(request):
    question_id = request.POST['question']
    value = True if request.POST['value'] == 'U' else False
    question = Question.objects.get(pk=question_id)
    users = question.votes.values_list('user', flat=True)

    if request.user.pk in users and (question.votes.get(user=request.user).value == value):
        question.votes.get(user=request.user).delete()
    else:
        question.votes.update_or_create(user=request.user, defaults={"value":value})

    return JsonResponse({"votes": question.total_votes()})

@login_required
@ajax_required
@require_http_methods(['POST'])
def answer_vote(request):
    answer_id = request.POST['answer']
    value = True if request.POST['value'] == 'U' else False
    answer = Answer.objects.get(uuid_id=answer_id)
    users = answer.votes.values_list('user', flat=True)

    if request.user.pk in users and (answer.votes.get(user=request.user).value == value):
        answer.votes.get(user=request.user).delete()
    else:
        answer.votes.update_or_create(user=request.user, defaults={"value":value})

    return JsonResponse({"votes": answer.total_votes()})

@login_required
@ajax_required
@require_http_methods(['POST'])
def accept_answer(request):
    answer_id = request.POST['answer']
    answer = Answer.objects.get(uuid_id=answer_id)

    if answer.question.user.username != request.user.username:
        raise PermissionDenied

    answer.accept_answer()
    return JsonResponse({"status":"true"})














