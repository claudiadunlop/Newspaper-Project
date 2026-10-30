from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ArticleForm, CommentForm
from .models import Article


class HomePageView(ListView):
    model = Article
    template_name = "home.html"
    context_object_name = "articles"


class ArticleDetailView(DetailView):
    model = Article
    template_name = "pages/article_detail.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "pages/article_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "pages/article_form.html"

    def test_func(self):
        article = self.get_object()
        return self.request.user.is_staff or article.author_id == self.request.user.pk


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = "pages/article_confirm_delete.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        article = self.get_object()
        return self.request.user.is_staff or article.author_id == self.request.user.pk


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    http_method_names = ["post"]

    def get_article(self):
        return get_object_or_404(Article, pk=self.kwargs["article_pk"])

    def form_valid(self, form):
        article = self.get_article()
        form.instance.article = article
        form.instance.author = self.request.user
        form.save()
        return redirect(article)

    def form_invalid(self, form):
        return render(
            self.request,
            "pages/article_detail.html",
            {"article": self.get_article(), "comment_form": form},
            status=400,
        )
