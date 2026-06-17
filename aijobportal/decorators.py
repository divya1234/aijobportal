from django.shortcuts import redirect
from django.contrib import messages

def wrapper(view_func):
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/admin/')
        return view_func(request, *args, **kwargs)

    return inner
def company_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'company':
            return view_func(request, *args, **kwargs)

        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    return wrapper


def jobseeker_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'jobseeker':
            return view_func(request, *args, **kwargs)

        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'admin':
            return view_func(request, *args, **kwargs)

        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    return wrapper