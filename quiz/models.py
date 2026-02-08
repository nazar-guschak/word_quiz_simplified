from django.db import models
from django.db.models import F, ExpressionWrapper, FloatField
from django.contrib.auth.models import User

class WordManager(models.Manager):
    def new_quiz_words(self, user, limit=10):
        return self.filter(owner=user).annotate(
            priority=ExpressionWrapper(
                (F('failed_attempts') + 1) / (F('attempts') + 1),
                output_field=FloatField()
            )
        ).order_by('-priority')[:limit]

class Word(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'Англійська'),
        ('uk', 'Українська'),
        ('pl', 'Польська'),
        ('de', 'Німецька'),
    ]

    word = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    source_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    attempts = models.PositiveIntegerField(default=0)
    failed_attempts = models.PositiveIntegerField(default=0)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = WordManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'word', 'translation'],
                name='unique_word_per_user'
            )
        ]

    def __str__(self):
        return self.word

