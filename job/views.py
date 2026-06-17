from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from job.models import JobCategory,Skill,Job,JobApplication,FeaturedPlan
from employer.models import Company
from jobseeker.models import JobSeeker
from aijobportal.decorators import company_required,jobseeker_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
import razorpay
from django.conf import settings
from django.db.models import Q
# Create your views here.
def joblist(request):
    today = timezone.now().date()
    applied_jobs = []
    q = request.GET.get('q')

    if q:
        jobs = Job.objects.filter(
            Q(title__icontains=q) |
            Q(company__company_name__icontains=q) |
            Q(location__icontains=q) |
            Q(category__name__icontains=q)|
            Q(skills__name__icontains=q)
        ).distinct()
    else:

        jobs = Job.objects.filter(
            application_deadline__gte=today,
            is_active=True,
            company__is_verified=True
        ).order_by('-posted_date')

    if request.user.is_authenticated:
        try:
            jobseeker = JobSeeker.objects.get(user=request.user)

            applied_jobs = JobApplication.objects.filter(
                applicant=jobseeker
            ).values_list('job_id', flat=True)

        except JobSeeker.DoesNotExist:
            pass
    return render(request, 'job/jobs.html', {
        'jobs': jobs,
        'applied_jobs': applied_jobs,
    })

@company_required
def add_notification(request):

    if request.user.user_type != 'company':
        return redirect('home')

    categories = JobCategory.objects.all()

    if request.method == 'POST':

        company = Company.objects.get(user=request.user)

        title = request.POST.get('title')
        experience = request.POST.get('experience')
        salary = request.POST.get('salary')
        application_deadline = request.POST.get('application_deadline')
        location = request.POST.get('location')
        vacancies = request.POST.get('vacancies')
        description = request.POST.get('description')
        job_type = request.POST.get('job_type')
        category_id = request.POST.get('category')

        # selected skills
        skill_ids = request.POST.getlist('skills')

        job = Job.objects.create(
            company=company,
            title=title,
            experience=experience,
            salary=salary,
            application_deadline=application_deadline,
            location=location,
            vacancies=vacancies,
            description=description,
            job_type=job_type,
            category_id=category_id
        )

        # save skills
        job.skills.set(skill_ids)
        return redirect('manage_jobs')

    return render(
        request,
        'job/add_notification.html',
        {
            'category': categories
        }
    )

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('manage_jobs')
def get_skills(request):

    category_id = request.GET.get('category_id')

    skills = Skill.objects.filter(
        category_id=category_id
    ).values('id', 'name')

    return JsonResponse({
        'skills': list(skills)
    })

@company_required
def manage_jobs(request):

    company = Company.objects.get(user=request.user)

    jobs = Job.objects.filter(company=company)

    context = {
        'jobs': jobs,
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'closed_jobs': jobs.filter(is_active=False).count(),
    }

    return render(
        request,
        'job/manage_jobs.html',
        context
    )
@company_required
def edit_job(request, job_id):
    company = Company.objects.get(user=request.user)

    job = get_object_or_404(
        Job,
        id=job_id,
        company=company
    )

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.location = request.POST.get('location')
        job.salary = request.POST.get('salary')
        job.job_type = request.POST.get('job_type')
        job.experience = request.POST.get('experience')
        job.vacancies = request.POST.get('vacancies')
        job.description = request.POST.get('description')
        job.application_deadline = request.POST.get('application_deadline')

        category_id = request.POST.get('category')
        job.category = JobCategory.objects.get(id=category_id)

        job.save()

        skills = request.POST.getlist('skills')
        job.skills.set(skills)

        return redirect('manage_jobs')

    categories = JobCategory.objects.all()
    skills = Skill.objects.filter(category_id=job.category)

    return render(request, 'job/edit_job.html', {
        'job': job,
        'categories': categories,
        'skills': skills,
    })
def job_details(request, id):
    job = get_object_or_404(Job, id=id)

    score = None
    matched = []
    missing = []

    if request.user.is_authenticated:
        try:
            jobseeker = JobSeeker.objects.get(user=request.user)

            resume_skills = [
                skill.name.lower()
                for skill in jobseeker.skills.all()
            ]

            job_skills = [
                skill.name.lower()
                for skill in job.skills.all()
            ]

            matched = list(set(resume_skills) & set(job_skills))
            missing = list(set(job_skills) - set(resume_skills))

            if job_skills:
                score = round(
                    len(matched) / len(job_skills) * 100,
                    2
                )

        except JobSeeker.DoesNotExist:
            pass

    context = {
        'job': job,
        'score': score,
        'matched': matched,
        'missing': missing,
    }

    return render(request, 'job/job_details.html', context)

    job = get_object_or_404(Job, id=id)

    already_applied = False

    if request.user.is_authenticated:
        try:
            jobseeker = JobSeeker.objects.get(user=request.user)
            already_applied = JobApplication.objects.filter(
                job=job,
                applicant=jobseeker
            ).exists()
        except JobSeeker.DoesNotExist:
            pass

    context = {
        'job': job,
        'already_applied': already_applied,
    }

    return render(request, 'job/job_details.html', context)


@jobseeker_required
def apply_job(request, id):
    job = get_object_or_404(Job, id=id)

    try:
        jobseeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        messages.error(request, "Job Seeker profile not found.")
        return redirect('job_details', id=job.id)

    if JobApplication.objects.filter(
        job=job,
        applicant=jobseeker
    ).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_details', id=job.id)

    JobApplication.objects.create(
        job=job,
        applicant=jobseeker,
        status='Pending'
    )

    messages.success(request, "Application submitted successfully.")
    return redirect('job_details', id=job.id)
@company_required
def applications_list(request):
    company = Company.objects.get(user=request.user)

    applications = JobApplication.objects.filter(
        job__company=company
    ).select_related('job', 'applicant')

    return render(request, 'job/applications_list.html', {
        'applications': applications
    })
@company_required
def update_application_status(request, app_id, status):

    application = get_object_or_404(JobApplication, id=app_id)

    company = request.user.company

    if application.job.company != company:
        messages.error(request, "Access denied.")
        return redirect('applications_list')

    application.status = status
    application.save()

    messages.success(request, "Status updated successfully.")
    return redirect('applications_list')


    jobseeker = JobSeeker.objects.get(
        user=request.user
    )

    resume_skills = jobseeker.skills.split(',')

    job_skills = job.skills.split(',')

    matched = set(
        skill.strip().lower()
        for skill in resume_skills
    ).intersection(
        set(
            skill.strip().lower()
            for skill in job_skills
        )
    )

    score = (
        len(matched) / len(job_skills)
    ) * 100 if job_skills else 0

    missing_skills = (
        set(job_skills) - matched
    )

    context = {
        'job': job,
        'score': round(score, 2),
        'matched': matched,
        'missing': missing_skills,
    }

    return render(
        request,
        'resume_analysis.html',
        context
    )
def upgrade_job(request,id):

    job = get_object_or_404(Job, id=id)
    plans = FeaturedPlan.objects.all()

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")

        return redirect(
            'payment_page',
            job_id=job.id,
            plan_id=plan_id
        )

    return render(
        request,
        'job/upgrade_job.html',
        {
            'job': job,
            'plans': plans
        }
    )
def payment_page(request, job_id, plan_id):

    job = get_object_or_404(Job, id=job_id)
    plan = get_object_or_404(FeaturedPlan, id=plan_id)

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    #amount = int(plan.price * 100)
    amount =int(1*100)
    payment = client.order.create({
        "amount": amount,
        "currency": "INR"
    })

    context = {
        'job': job,
        'plan': plan,
        'payment': payment,
        'key': settings.RAZORPAY_KEY_ID
    }

    return render(request, 'job/payment_page.html', context)
def payment_success(request):

    job_id = request.GET.get('job_id')
    plan_id = request.GET.get('plan_id')

    job = get_object_or_404(Job, id=job_id)
    plan = get_object_or_404(FeaturedPlan, id=plan_id)

    job.is_featured = True
    job.plan=plan
    job.featured_until = date.today() + timedelta(days=plan.duration_days)
    job.save()

    return redirect('company_dashboard')
def application_detail(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related(
            'job',
            'applicant'
        ),
        id=application_id
    )

    applicant_skills = [
        skill.name.lower()
        for skill in application.applicant.skills.all()
    ]

    job_skills = [
        skill.name.lower()
        for skill in application.job.skills.all()
    ]

    matched = list(set(applicant_skills) & set(job_skills))
    missing = list(set(job_skills) - set(applicant_skills))

    score = 0

    if job_skills:
        score = round(
            len(matched) / len(job_skills) * 100,
            2
        )
    skills = application.applicant.skills.all()
    
    return render(request, 'job/application_detail.html', {
        'application': application,
        'score': score,
        'matched': matched,
        'missing': missing,
        'skills' : skills
    })
@jobseeker_required
def my_applications(request):
    jobseeker = JobSeeker.objects.get(user=request.user)
    applications = []
    applications = JobApplication.objects.filter(
        applicant_id=jobseeker.id
        ).select_related('job')

    return render(request, 'job/my_applications.html', {
        'applications': applications
    })
def featured_jobs(request):
    today = timezone.now().date()
    applied_jobs = []
    q = request.GET.get('q')

    if q:
        jobs = Job.objects.filter(
            Q(title__icontains=q) |
            Q(company__company_name__icontains=q) |
            Q(location__icontains=q) |
            Q(category__name__icontains=q) |
            Q(skills__name__icontains=q),
            is_featured=True,
            featured_until__gte=timezone.now().date()
        ).distinct()
    else:

        jobs = Job.objects.filter(
            application_deadline__gte=today,
            is_active=True,
            is_featured=True,
            company__is_verified=True,
            featured_until__gte=timezone.now().date()
        ).order_by('-posted_date')

    if request.user.is_authenticated:
        try:
            jobseeker = JobSeeker.objects.get(user=request.user)

            applied_jobs = JobApplication.objects.filter(
                applicant=jobseeker
            ).values_list('job_id', flat=True)

        except JobSeeker.DoesNotExist:
            pass
    return render(request, 'job/jobs.html', {
        'jobs': jobs,
        'applied_jobs': applied_jobs,
    })

def skill_list(request):
    categories = JobCategory.objects.all()
    skills = Skill.objects.select_related('category')

    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")

        if name and category_id:
            Skill.objects.create(
                name=name,
                category_id=category_id
            )
            return redirect('skill_list')

    return render(request, "job/skills.html", {
        "skills": skills,
        "categories": categories
    })

def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        return redirect('/login')

    skill = get_object_or_404(Skill, id=skill_id)
    skill.delete()

    return redirect('/jobs/skill_list')

def category_list(request):
    if not request.user.is_superuser:
        return redirect('/login')

    categories = JobCategory.objects.all().order_by('name')

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            JobCategory.objects.create(name=name)
            return redirect('category_list')

    return render(request, "job/categories.html", {
        "categories": categories
    })
def delete_category(request, category_id):
    if not request.user.is_superuser:
        return redirect('/login')

    category = get_object_or_404(JobCategory, id=category_id)
    category.delete()

    return redirect('category_list')