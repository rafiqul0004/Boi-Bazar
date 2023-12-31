# Create your views here.
from django.shortcuts import render, redirect
from .import models
from .import forms
from django.views.generic import DetailView
from django.contrib import messages
from borrow.models import Borrow

# Create your views here.
class DetailBookView(DetailView):
    model = models.Book
    template_name = 'detail.html'
    pk_url_kwarg = 'id'

    def post(self, request, *args, **kwargs):
        comment_form = forms.CommentForm(self.request.POST)
        book = self.get_object()

        if Borrow.objects.filter(user=request.user, book=book, is_returned=False).exists():
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.book = book
                new_comment.user = request.user
                new_comment.save()

                # Redirect after a successful comment submission
                return redirect('detail_books', id=book.id)
            else:
                # If the form is not valid, render the page with the error messages
                messages.error(request, 'Invalid comment. Please check your input.')
        else:
            # User has not borrowed the book
            messages.error(request, 'You can only comment on books you have borrowed.')

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object

        # Accessing reviews through the related name 'reviews'
        reviews = book.reviews.all()

        comment_form = forms.CommentForm()
        context['reviews'] = reviews
        context['comment_form'] = comment_form
        return context
