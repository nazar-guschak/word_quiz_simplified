from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('edit/<int:word_id>', views.edit, name='edit'),
    path('delete/<int:word_id>', views.delete, name='delete'),
    path('quiz/', views.run_quiz, name='quiz'),
]