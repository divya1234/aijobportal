from django.db import models

# Create your models here.
from django.db import models
from employer.models import Company
from django.conf import settings

class FeaturedPlan(models.Model):
    name = models.CharField(max_length=50)

    duration_days = models.IntegerField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

class JobCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Skill(models.Model):
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        related_name='skills'
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        
class Job(models.Model):
    JOB_TYPES = (
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        ('Remote', 'Remote'),
    )
    EXPERIENCE_CHOICES = [
        ('Fresher', 'Fresher'),
        ('0-1', '0-1 Years'),
        ('1-3', '1-3 Years'),
        ('3-5', '3-5 Years'),
        ('5-10', '5-10 Years'),
        ('10+', '10+ Years'),
    ]


    title = models.CharField(max_length=200)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    location = models.CharField(max_length=200)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience = models.CharField(
            max_length=20,
            choices=EXPERIENCE_CHOICES
        )  
    vacancies = models.PositiveIntegerField(default=1)
    
    description = models.TextField()
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE
    )
    skills = models.ManyToManyField(Skill)

    posted_date = models.DateTimeField(auto_now_add=True)
    application_deadline = models.DateField()

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    plan = models.ForeignKey(
        FeaturedPlan,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    featured_until = models.DateField(
        null=True,
        blank=True
    )
    def __str__(self):
        return self.title
class JobApplication(models.Model):

    STATUS = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Selected', 'Selected'),
    )

    job = models.ForeignKey(
        'job.Job',
        on_delete=models.CASCADE
    )

    applicant = models.ForeignKey(
        'jobseeker.JobSeeker',
        on_delete=models.CASCADE
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Applied'
    )
class ResumeAnalysis(models.Model):

    applicant = models.ForeignKey(
        'jobseeker.JobSeeker',
        on_delete=models.CASCADE
    )

    resume_score = models.IntegerField()

    matched_skills = models.TextField()

    missing_skills = models.TextField()

    analyzed_at = models.DateTimeField(
        auto_now_add=True
    )
