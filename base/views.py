from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import UserCreationForm

@login_required(login_url='/login/')
def home(request):
    user_azn_balance = InvestorWallet.objects.get(investor=request.user, curr='AZN').balance
    user_usd_balance = InvestorWallet.objects.get(investor=request.user, curr='USD').balance
    user_eur_balance = InvestorWallet.objects.get(investor=request.user, curr='EUR').balance
    available_offers = Offer.objects.filter(available__gt=0).order_by('-updated')[:4]
    your_investments = Investment.objects.filter(investor=request.user)
    return render(request, 'index.html', {'user_azn_balance': user_azn_balance, 'user_usd_balance': user_usd_balance, 'user_eur_balance': user_eur_balance, 'available_offers': available_offers, 'inv': your_investments})

def handler404(request, *args, **kwargs):
    return render(request, '404.html')

def login_investor(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username:
            try:
                user = Investor.objects.get(username=username)
            except:
                messages.error(request, 'User does not exist !')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Incorrect username or password!')
    return render(request, 'login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'register.html', {'form': form})

@login_required(login_url='/login/')
def profile(request):
    return render(request, 'pages-profile.html')

@login_required(login_url='/login/')
def offer(request, pk):
    offer = get_object_or_404(Offer, id=pk)
    if request.method == 'POST':
        user = request.user
        summ = float(request.POST.get('amount'))
        curr = request.POST.get('currency')
        offer = Offer.objects.get(id=pk)
        user.invest(startup=offer.startup, summ=summ, offer=offer, curr=curr)
        return redirect('offer', pk=pk)
    return render(request, 'offer-detail.html', {'offer': offer})

@login_required(login_url='/login/')
def offers(request):
    offers = Offer.objects.all()
    return render(request, 'offers.html', {'offers': offers})
