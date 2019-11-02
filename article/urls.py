from django.urls import path
from . import views

app_name = 'article'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('<int:id>/', views.article_detail, name='article_detail'),
    path('article_create/', views.article_create, name='article_create'),
    path(
        'article_safe_delete/<int:id>/',
        views.article_safe_delete,
        name="article_safe_delete"
        ),
    path('article_update/<int:id>/', views.article_update, name="article_update"),

    # path('list_view/', views.ArticleListView.as_view(), name='list_view'),

]
