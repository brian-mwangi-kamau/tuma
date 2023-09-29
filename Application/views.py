from django.shortcuts import render, redirect
from .models import CustomUser, PlatformAccount, Transaction, CharityList
from .forms import SignupForm, LoginForm, ListCharity, MoneyTransferForm
from django.contrib.auth.decorators import login_required
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q


# Create your views here.

def homepage(request):
        return render(request, 'homepage.html')


def profile_settings(request):
    return render(request, 'profile.html')

def trading(request):
    return render(request, 'trades.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.account_number = generate_unique_account_number()
            user.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def generate_unique_account_number():
    while True:
        account_number = ''.join(random.choice('0123456789') for _ in range(8))
        if not CustomUser.objects.filter(account_number=account_number).exists():
            return account_number


@receiver(post_save, sender=CustomUser)
def generate_user_account_number(sender, instance, created, **kwargs):
    if created:
        instance.account_number = generate_unique_account_number()
        instance.save()



@login_required
def dashboard(request):
    first_name = request.user.first_name
    last_name = request.user.last_name
    account_number = request.user.account_number
    balance = request.user.balance
    points = request.user.points
    user=request.user
    user_transactions = Transaction.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')
    available_charities = CharityList.objects.all()

    context = {
        'user': user,
        'first_name': first_name,
        'last_name': last_name,
        'account_number': account_number,
        'balance_cash': balance,
        'points': points,
        'user_transactions': user_transactions,
        'available_charities': available_charities,
    }
    return render(request, 'dashboard.html', context)



@login_required
def money_transfer(request):
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST)
        if form.is_valid():
            logged_in_user = request.user

            recipient_account_number = form.cleaned_data['account_number']

            if logged_in_user.account_number == recipient_account_number:
                form.add_error('account_number', 'You cannot send money to yourself!!')
            else:
                try:
                    recipient = CustomUser.objects.get(account_number=recipient_account_number)

                    amount = form.cleaned_data['amount']
                    points_to_earn = amount // 10   # The points the sender will earn. That will be one point for every 10 shillings sent.
                    platform_income = Decimal(amount) * Decimal('0.02')   # The funds that the platform will charge per transaction. Which is 2%

                    if logged_in_user.balance < platform_income:
                        form.add_error('amount', "Insufficient balance to cover the transaction fee.")
                    else:
                        logged_in_user.balance -= platform_income

                    if logged_in_user.balance > amount:
                        logged_in_user.balance -= amount
                        logged_in_user.points += points_to_earn
                        logged_in_user.save()

                        recipient.balance += amount
                        recipient.save()

                        Transaction.objects.create(
                            sender=logged_in_user,
                            transaction_type='send',
                            amount=amount,
                            recipient=recipient,
                        )

                        Transaction.objects.create(
                            recipient=recipient,
                            transaction_type='receive',
                            amount=amount,
                            sender=logged_in_user,
                        )

                        total_amount_on_platform = CustomUser.objects.aggregate(Sum('balance'))['balance__sum']
                        platform_account = PlatformAccount.objects.first()
                        platform_account.total_amount_on_platform = total_amount_on_platform
                        platform_account.income += platform_income
                        platform_account.save()
                        return redirect('dashboard')
                    else:
                        form.add_error(None, 'Insufficient balance.')
                except CustomUser.DoesNotExist:
                    form.add_error('account_number', 'Recipient account number not found.')
    else:
        form = MoneyTransferForm()
    return render(request, 'money_transfer.html', {'form': form})


@login_required
def list_charity(request):
    lister = request.user
    if lister.is_admin == False:
        return HttpResponse('You cannot perform this action!')
    if request.method == 'POST':
        form = ListCharity(request.POST, request.FILES)
        if form.is_valid():
            charities = CharityList(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                photo=form.cleaned_data['photo'],
                goal_amount=form.cleaned_data['goal_amount']
            )
            charities.save()
            return redirect('dashboard')
    else:
        form = ListCharity()
    return render(request, 'list_donation.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, f'You have been logged out')
    return redirect('login')