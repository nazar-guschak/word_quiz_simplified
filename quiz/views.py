from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import random
from .models import Word
from .forms import WordFormSet, AddWordForm, QuizForm
from django.db.models import Case, When


@login_required
def index(request):

    words = Word.objects.filter(owner=request.user)
    context = {'words':words}

    return render(request, 'quiz/index.html', context)


@login_required
def add(request):
    if request.method == 'POST':
        formset = WordFormSet(data=request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)

            added = 0
            skipped = 0

            for instance in instances:
                instance.owner = request.user

                try:
                    instance.save()
                    added += 1
                except IntegrityError:
                    skipped += 1

            if added:
                messages.success(request, f"{added} слів додано в словник.")
            if skipped:
                messages.warning(request, f"{skipped} слів вже існували і були пропущені.")

            return redirect('quiz:index')
    else:
        formset = WordFormSet(queryset=Word.objects.none())

    return render(request, 'quiz/add.html', {'formset': formset})


@login_required
def edit(request, word_id):
    word = get_object_or_404(Word, id=word_id, owner=request.user)

    if request.method == 'POST':
        form = AddWordForm(instance=word, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, message=f'Пара {word.word} - {word.translation} змінена.')
            return redirect('quiz:index')
    else:
        form = AddWordForm(instance=word)

    context = {'word': word, 'form':form}
    return render(request, 'quiz/edit.html', context)


@login_required
@require_POST
def delete(request, word_id):
    word = get_object_or_404(Word, id=word_id, owner=request.user)
    word.delete()

    messages.success(request, message=f'Пара {word.word} - {word.translation} видалена.')
    return redirect("quiz:index")


@login_required
def run_quiz(request):
    results = []
    if request.method == "POST":
        quiz_ids = request.session.get("quiz_word_ids", [])
        quiz_choices = request.session.get("choices", [])

        result_choices = [[list(c)[0] for c in inner] for inner in quiz_choices]
        quiz_choices = [[tuple(c) for c in inner] for inner in quiz_choices]

        # Restore Word queryset order to match the original GET order
        # so field choices align correctly during form validation
        quiz = list(
            Word.objects.filter(id__in=quiz_ids).order_by(
                Case(*[When(id=id, then=pos) for pos, id in enumerate(quiz_ids)])
            )
        )

        form = QuizForm(request.POST, words=quiz, choices=quiz_choices)

        if form.is_valid():
            for i, word in enumerate(quiz):
                answer = form.cleaned_data[f'word_{word.id}']

                results.append({
                    "word": word.word,
                    "options": result_choices[i],
                    "correct": word.translation,
                    "selected": answer,
                    "is_true": word.translation == answer,
                })

                word.attempts += 1
                word.save()

                if answer != word.translation:
                    word.failed_attempts += 1
                    word.save()
        else:
            print(form.errors)

        return render(request, 'quiz/quiz_results.html', {'results': results})

    else:
        quiz = list(Word.objects.new_quiz_words(user=request.user))
        all_translation = list(
            Word.objects.values_list("translation", flat=True)
        )
        random.shuffle(quiz)
        request.session["quiz_word_ids"] = [w.id for w in quiz]

        many_choices = []

        for word in quiz:
            wrong = random.sample(
                [t for t in all_translation if t != word.translation], 3
            )

            choices = [(word.translation, word.translation)]
            choices += [(w, w) for w in wrong]
            random.shuffle(choices)

            many_choices.append(choices)

        request.session["choices"] = many_choices
        form = QuizForm(request.POST, words=quiz, choices=many_choices)

        return render(request, "quiz/quiz.html", {"form": form})