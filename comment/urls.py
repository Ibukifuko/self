from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
    path('comment_list/<int:article_id>/', views.comment_list, name='comment_list'),
]
