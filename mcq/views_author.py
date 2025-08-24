# mcq/views_author.py (authoring)
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MCQForm, ChoiceFormSet, validate_single_correct

def create_mcq(request):
    if request.method == "POST":
        form = MCQForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            validate_single_correct(formset)
            mcq = form.save()
            formset.instance = mcq
            formset.save()
            messages.success(request, "MCQ saved.")
            return redirect("create_mcq")
        else:
            form = MCQForm()
            formset = ChoiceFormSet()
        return render(request, "create_mcq.html", {"form": form, "formset": formset})