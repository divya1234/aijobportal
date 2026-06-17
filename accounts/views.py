from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from employer.models import Company
from jobseeker.models import JobSeeker
from job.models import Job,JobApplication
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from aijobportal.decorators import company_required,jobseeker_required
from django.shortcuts import get_object_or_404

User = get_user_model()
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)        

        if user is None:
            messages.error(request, "Invalid username or password")
            return render(request, "accounts/login.html")

        login(request, user)
        if user is not None and user.is_superuser:
            return redirect('/superadmin_dashboard')
        if user.user_type == "company":
            company = Company.objects.get(user=user)
            request.session['company_id'] = company.id
            request.session['user_type'] = 'company'
            return redirect("company_dashboard")

        elif user.user_type == "jobseeker":
            profile = JobSeeker.objects.filter(user=user).first()
            if profile:
                request.session['jobseeker_id'] = profile.id
                request.session['user_type'] = 'jobseeker'
                return redirect("/jobs")
            else:
                messages.error(request, "Job seeker profile not found.")
                return render(request, "accounts/login.html")
    return render(request, "accounts/login.html")
    


@login_required
def company_dashboard(request):
    company_id = request.session.get('company_id')
    if not company_id:
        return redirect('/accounts/login')

    company = Company.objects.get(id=company_id)
    total_jobs = Job.objects.filter(company=company).count()
    jobs = Job.objects.filter(company=company).order_by('-id')
    print(jobs)
    active_jobs = Job.objects.filter(
        company=company,
        application_deadline__gte=timezone.now().date()
    ).count()

    expired_jobs = Job.objects.filter(
        company=company,
        application_deadline__lt=timezone.now().date()
    ).count()

    total_applications = JobApplication.objects.filter(
        job__company=company
    ).count()

    shortlisted = JobApplication.objects.filter(
        job__company=company,status='Shortlisted').count()
    selected = JobApplication.objects.filter(
        job__company=company,status='Selected').count()

    context = {
        'company': company,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'expired_jobs': expired_jobs,
        'total_applications': total_applications,
        'jobs':jobs,
        'shortlisted':shortlisted,
        'selected':selected
    }

    return render(request, 'accounts/company_dashboard.html', context)
def user_logout(request):
    logout(request)
    return redirect('login')
def home(request):
    applied_jobs = []
    featured_jobs = Job.objects.filter(
        is_featured=True,
        company__is_verified=True,
        featured_until__gte=timezone.now().date()
    ).order_by('-id')[:6]
    if request.user.is_authenticated:
        try:
            jobseeker = JobSeeker.objects.get(user=request.user)

            applied_jobs = JobApplication.objects.filter(
                applicant=jobseeker
            ).values_list('job_id', flat=True)

        except JobSeeker.DoesNotExist:
            pass
    context = {
        'featured_jobs': featured_jobs,
        'applied_jobs': applied_jobs
    }

    return render(request, 'accounts/home.html', context)
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully")
        except User.DoesNotExist:
            messages.error(request, "Email not found")

    return render(request, 'accounts/forgot_password.html')
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(request, 'Password changed successfully.')

            if Company.objects.filter(user=user).exists():
                return redirect('/employer/company_profile')

            elif JobSeeker.objects.filter(user=user).exists():
                return redirect('/jobseeker/jobseeker_profile')

            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {
        'form': form
    })

@login_required
def superadmin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('/login')
    
    companies = Company.objects.all()
    context = {
        "users_count": User.objects.count(),
        "jobs_count": Job.objects.count(),
        "applications_count": JobApplication.objects.count(),
        "companies_count": Company.objects.count(),
        "jobseekers_count": JobSeeker.objects.count(),
        "companies":companies,
    }
    return render(request, "accounts/superadmin_dashboard.html", context)
@login_required
def toggle_company_status(request, company_id):
    if not request.user.is_superuser:
        return redirect('/login')

    company = get_object_or_404(Company, id=company_id)

    company.is_verified = not company.is_verified
    company.save()

    return redirect('/superadmin_dashboard/')