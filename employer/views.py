from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from job.models import JobCategory
from employer.models import Company,Industry
from django.contrib.auth import authenticate, login
from aijobportal.decorators import company_required,jobseeker_required
User = get_user_model()
# Create your views here.
def companies(request):
    companies = Company.objects.filter(is_verified=True)
    return render(request,'employer/companies.html',{"companies":companies})

def company_register(request):
    industries  = Industry.objects.all()
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        industry = request.POST.get('industry')
        website = request.POST.get('website')
        facebook_url = request.POST.get('facebook_url')
        linkedin_url = request.POST.get('linkedin_url')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        password = request.POST.get('password')
        c_password = request.POST.get('c_password')

        company_size = request.POST.get('company_size')
        description = request.POST.get('description')
        founded_year = request.POST.get('founded_year')

        logo = request.FILES.get('logo')
        required_fields = [
            'company_name',
            'industry',
            'email',
            'phone',
            'address',
            'city',
            'state',
            'country',
            'company_size'
        ]

        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f"{field.replace('_', ' ').title()} is required.")
                return render(request,'employer/company_register.html',{'industry':industries })    
        if password != c_password:
            messages.error(request, "Passwords do not match")
            return render(request,'employer/company_register.html',{'industry':industries })    

        # Email already exists in User table
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request,'employer/company_register.html',{'industry':industries })    

        if Company.objects.filter(email=email).exists():
            messages.error(request, "Company email already registered")
            return render(request,'employer/company_register.html',{'industry':industries })    

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            user_type='company'
        )

        Company.objects.create(
            user=user,
            company_name=company_name,
            industry=industry,
            website=website,
            facebook_url=facebook_url,
            linkedin_url=linkedin_url,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            country=country,
            company_size=company_size,
            description=description,
            founded_year=founded_year if founded_year else None,
            logo=logo
        )

            #return redirect('dashboard')  # change to your URL name
        
        messages.success(
            request,
            "Company registered successfully. Your account is pending admin verification. You can log in after approval."
        )
        return render(request,'employer/company_register.html',{'industry':industries })    
    
    return render(request,'employer/company_register.html',{'industry':industries })

@company_required
def company_profile(request):
    company = Company.objects.get(user=request.user)

    return render(request, 'employer/profile.html', {
        'company': company
    })
@company_required
def edit_company_profile(request):
    industries  = Industry.objects.all()
    company = Company.objects.get(user=request.user)

    if request.method == "POST":
        company.company_name = request.POST.get("company_name")
        company.industry_id = request.POST.get("industry")
        company.email = request.POST.get("email")
        company.phone = request.POST.get("phone")
        company.website = request.POST.get("website")
        company.linkedin_url = request.POST.get("linkedin_url")
        company.facebook_url = request.POST.get("facebook_url")
        company.address = request.POST.get("address")
        company.city = request.POST.get("city")
        company.state = request.POST.get("state")
        company.country = request.POST.get("country")
        company.company_size = request.POST.get("company_size")
        company.founded_year = request.POST.get("founded_year")
        company.description = request.POST.get("description")

        if request.FILES.get("logo"):
            company.logo = request.FILES.get("logo")

        company.save()

        return redirect("company_profile")
    else:
        return render(request, 'employer/edit_profile.html', {'industries': industries,'company':company})