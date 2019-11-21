from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView
from .models import ArticlePost, ArticleColumn
from .forms import ArticlePostForm
from comment.models import Comment


import markdown
# Create your views here.


# class ArticleListView(ListView):
#     context_object_name = 'articles'
#     template_name = 'article/list.html'
#     paginate_by = 3
#
#     def get_queryset(self):
#         queryset = ArticlePost.objects.all()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['order'] = 'total_views'
#         return context


def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    article_list = ArticlePost.objects.all()
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list, 10)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.toc',
        ])
    for art in articles:
        art.body = md.convert(art.body)

    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }
    return render(request, 'article/list.html', context)

def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)

    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])
    article.body = md.convert(article.body)

    context = {'article': article, 'comments': comments, 'toc': md.toc}
    return render(request, 'article/detail.html', context)

@login_required(login_url='/userprofile/login/')
def article_create(request):
    if not request.user.is_superuser:
        return HttpResponse("无权限")
    if request.method == 'POST':
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            article_post_form.save_m2m()
            return redirect("/article/")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns':columns}
        return render(request, 'article/create.html', context)

@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if article.author_id == request.user.id:
            article.delete()
            return redirect("/article/")
        else:
            return HttpResponse("无权限")
    else:
        return HttpResponse("仅允许post请求")

@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
    if article.author_id == request.user.id:
        if request.method == 'POST':
            article_post_form = ArticlePostForm(data=request.POST)
            if article_post_form.is_valid():
                article.title = request.POST['title']
                article.body = request.POST['body']
                if request.POST['column'] != 'none':
                    article.column = ArticleColumn.objects.get(id=request.POST['column'])
                else:
                    article.column = None
                article.save()
                return redirect("article:article_detail", id=id)
            else:
                return HttpResponse("表单内容有误，请重新填写。")
        else:
            article_post_form = ArticlePostForm(),
            columns = ArticleColumn.objects.all()
            context = {'article': article, 'article_post_form': article_post_form, 'columns': columns}
            return render(request, 'article/update.html', context)
    else:
        return HttpResponse("无权限")
