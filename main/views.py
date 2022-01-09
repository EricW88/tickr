from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Portfolio, Stock, StockItem

import pandas as pd
import numpy as np
import requests as stock_request
import multitasking
import yfinance as yf

from decimal import *

# Create your views here.


def homeRedirect(request):
    return redirect("/login")


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data["username"]
            new_user = User.objects.get(username=name)
            new_portfolio = Portfolio(user=new_user, balance=10000, assets=0)
            new_portfolio.save()
            new_user.portfolio.add(new_portfolio)
            return redirect("/login")

    context = {'form':form}
    return render(request, 'main/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('homePage')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homePage')

    context = {}
    return render(request, 'main/login.html', context)


@login_required(login_url='login')
def homePage(request):
    pf = Portfolio.objects.get(user=request.user)
    context = {'pf':pf}

    # Calculate balance upon page loading
    pf.assets = 0
    for stock_item in pf.stocks.all():
        ticker = yf.Ticker(stock_item.stock.name)
        ticker_hist = ticker.history(period="1d", interval="1m")
        open_price = ticker_hist['Close'][0]
        cur_price = ticker_hist.tail(1)['Close'][0]
        stock_item.stock.open_price = open_price
        stock_item.stock.current_price = cur_price        
        stock_item.value = Decimal(cur_price) * stock_item.quantity

        pf.assets += stock_item.value
        stock_item.save()
        stock_item.stock.save()

    pf.assets = round(pf.assets, 2)
    pf.save()

    if request.method == 'POST':
        if 'logout' in request.POST:
            logout(request)
            return redirect('loginPage')
        elif 'purchase' in request.POST:
            is_bought = request.POST.get('buy-select') == '1'
            name = request.POST.get('abbr').lower()
            amount = float(request.POST.get('amount'))

            # check if buy amount is valid
            if is_bought and amount > pf.balance:
                print("Can't buy that much")
                render(request, "main/home.html", context)

            # check if ticker is valid
            ticker = yf.Ticker(name)
            ticker_hist = ticker.history(period="1d", interval="1m")
            if (ticker_hist.empty):
                render(request, "main/home.html", context)

            open_price = ticker_hist['Close'][0]
            cur_price = ticker_hist.tail(1)['Close'][0]


            stock = Stock.objects.filter(name=name)
            if not stock.exists():
                stock = Stock(name=name, open_price=open_price, current_price=cur_price)
            else:
                stock = stock.get()

            stock_item = StockItem.objects.filter(stock=stock, portfolio=pf)

            quantity = amount / cur_price
            
            # buy/sell stock
            if is_bought:
                if not stock_item.exists():
                    stock_item = StockItem(stock=stock, portfolio=pf, quantity=0, value=0)
                else:
                    stock_item = stock_item.get()
                stock_item.value += Decimal(amount)
                stock_item.quantity += Decimal(quantity)
                pf.balance -= Decimal(amount)
            else:
                if not stock_item.exists() or amount > stock_item.get().value:
                    print(round(Decimal(amount), 2) > round(stock_item.get().value, 2))
                    print(amount)
                    print(stock_item.get().value)
                    print("Can't sell that much")
                    return render(request, "main/home.html", context)
                else:
                    stock_item = stock_item.get()
                stock_item.value -= Decimal(amount)
                stock_item.quantity -= Decimal(quantity)
                pf.balance += Decimal(amount)
                print(stock_item.value)
                if stock_item.value == 0:
                    stock_item.delete()

            stock.open_price = open_price
            stock.cur_price = cur_price
            stock.save()
            stock_item.save()
            pf.save()

            return redirect('homePage')

    return render(request, "main/home.html", context)