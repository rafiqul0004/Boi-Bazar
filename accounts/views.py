from django.shortcuts import render,get_object_or_404
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm,DepositForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.views.generic import CreateView
from .models import UserAccount
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from books.models import Book
from borrow.models import Borrow
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

#Sending Email Function
def send_transaction_email(user,subject,template,amount):
    message=render_to_string(template,{
        'user': user,
        'amount':amount,
    })
    send_mail=EmailMultiAlternatives(subject, '',to=[user.email])
    send_mail.attach_alternative(message,"text/html")
    send_mail.send()

def send_book_email(user,subject,template,amount,book):
    message=render_to_string(template,{
        'user': user,
        'amount':amount,
        'book':book,
    })
    send_mail=EmailMultiAlternatives(subject, '',to=[user.email])
    send_mail.attach_alternative(message,"text/html")
    send_mail.send()

@login_required
def profile(request):
    books=Borrow.objects.filter(user=request.user)
    return render(request,'profile.html',{'books':books})

class UserRegistrationView(FormView):
    template_name = 'form.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self,form):
        # print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        # print(user)
        return super().form_valid(form) # form_valid function call hobe jodi sob thik thake
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['type'] = 'Signup'
        return context
    

class UserLoginView(LoginView):
    template_name='form.html'
    def get_success_url(self):
        return reverse_lazy('homepage')
    def form_valid(self, form):
        messages.success(self.request,'Login successful')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.warning(self.request,'Login Information Invalid')
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['type']='login'
        return context
    
@login_required
def user_logout(request):
    logout(request)
    return redirect('homepage')


class UserUpdateView(LoginRequiredMixin,View):
    template_name = 'form.html'
    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form,'type':'Update'})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form,'type':'update'})
    
class DepositMoneyView(LoginRequiredMixin, FormView):
    template_name = 'form.html'
    form_class = DepositForm
    success_url = reverse_lazy('profile')  # Adjust the URL name if needed

    def form_valid(self, form):
        user_account = UserAccount.objects.get(user=self.request.user)
        amount = form.cleaned_data['balance']

        if amount > 0:
            user_account.balance += amount
            user_account.save()

            messages.success(self.request, f'Successfully deposited {amount} taka into your account.')
            send_transaction_email(self.request.user,"Deposite Message","deposit_email.html",amount)
        else:
            messages.error(self.request, 'Please enter a valid amount to deposit.')

        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['type']='Deposit'
        return context
    
@login_required
def borrow(request, id):
    book=Book.objects.get(pk=id) 
    user_account=UserAccount.objects.get(user=request.user)
    if user_account.balance>book.borrowing_price:
        user_account.balance-=book.borrowing_price
        user_account.save()
        Borrow.objects.create(
                user=request.user,
                book=book,
                balance_after_borrow=user_account.balance
            )

        messages.success(request, f'Successfully borrowed {book.title}. Balance: {user_account.balance} taka.')
        send_book_email(request.user,"Borrow Book","borrow_book.html",book.borrowing_price,book.title)
    else:
        messages.error(request, 'Insufficient balance. Please deposit money before borrowing.')

    return redirect('profile') 

def return_book(request, id):
    borrow = get_object_or_404(Borrow, id=id)

    if not borrow.is_returned:
        user_account = UserAccount.objects.get(user=request.user)
        user_account.balance += borrow.book.borrowing_price
        user_account.save()
        send_book_email(request.user,"Return Book","return_book.html",borrow.book.borrowing_price,borrow.book.title)

        borrow.is_returned = True
        borrow.delete()

    return redirect('profile')