from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Redirect based on role
            if user.role == 'storesman':
                return redirect('storesman_dashboard')

            elif user.role == 'procurement':
                return redirect('inventory_list')

            elif user.role == 'accounts':
                return redirect('accounts_dashboard')

            elif user.role == 'principal':
                return redirect('principal_dashboard')

            elif user.role == 'it':
                return redirect('/admin/')

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html')


def logout_view(request):

    logout(request)

    return redirect('login')