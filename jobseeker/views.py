from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import JobSeeker
from job.models import JobCategory,Skill
from employer.models import Company,Industry
from django.contrib.auth import authenticate, login
from aijobportal.decorators import company_required,jobseeker_required
User = get_user_model()

def register(request):

    categories = JobCategory.objects.all()

    if request.method == 'POST':

        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        category_id = request.POST.get('category')
        experience = request.POST.get('experience')

        qualification = request.POST.get('qualification')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        objective = request.POST.get('objective')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')

        resume = request.FILES.get('resume')

        skill_ids = request.POST.getlist('skills')

        # Password validation
        if password != cpassword:
            messages.error(request, "Passwords do not match")
            return render(
                request,
                'jobseeker/register.html',
                {'category': categories}
            )

        # Email validation
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(
                request,
                'jobseeker/register.html',
                {'category': categories}
            )

        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=fname,
            last_name=lname,
            user_type='jobseeker'
        )

        # Create Job Seeker Profile
        jobseeker = JobSeeker.objects.create(
            user=user,
            phone=phone,
            category_id=category_id,
            experience=experience,
            qualification=qualification,
            city=city,
            gender=gender,
            date_of_birth=date_of_birth,
            objective=objective,
            resume=resume
        )

        # Save selected skills
        jobseeker.skills.set(skill_ids)

        messages.success(
            request,
            "Registration completed successfully."
        )

        login(request, user)
        return redirect('joblist')
        
    else:

        return render(
            request,
            'jobseeker/register.html',
            {'category': categories}
        )
@jobseeker_required
def jobseeker_profile(request):
    jobseeker = JobSeeker.objects.select_related(
        'user',
        'category'
    ).prefetch_related(
        'skills'
    ).get(user=request.user)

    return render(request, 'jobseeker/profile.html', {
        'jobseeker': jobseeker
    })
@jobseeker_required
def edit_profile(request):
    jobseeker = JobSeeker.objects.get(user=request.user)

    categories = JobCategory.objects.all()
    skills = Skill.objects.all()

    if request.method == "POST":

        jobseeker.phone = request.POST.get("phone")
        jobseeker.gender = request.POST.get("gender")
        jobseeker.date_of_birth = request.POST.get("date_of_birth")

        jobseeker.address = request.POST.get("address")
        jobseeker.city = request.POST.get("city")
        jobseeker.state = request.POST.get("state")
        jobseeker.country = request.POST.get("country")

        jobseeker.qualification = request.POST.get("qualification")
        jobseeker.experience = request.POST.get("experience")

        jobseeker.category_id = request.POST.get("category")

        jobseeker.linkedin = request.POST.get("linkedin")
        jobseeker.github = request.POST.get("github")
        jobseeker.objective = request.POST.get("objective")

        if request.FILES.get("resume"):
            jobseeker.resume = request.FILES["resume"]

        jobseeker.save()

        skill_ids = request.POST.getlist("skills")
        jobseeker.skills.set(skill_ids)

        return redirect("jobseeker_profile")

    return render(request, 'jobseeker/edit_profile.html', {
        'jobseeker': jobseeker,
        'categories': categories,
        'skills': skills,
    })