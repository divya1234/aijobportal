from django.db import models
from django.conf import settings

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from job.models import JobCategory

class JobSeeker(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES,blank=True,null=True)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    country = models.CharField(max_length=100)

    qualification = models.CharField(max_length=100)

    experience = models.CharField(
        max_length=50,
        default='Fresher'
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE
    )

    skills = models.ManyToManyField(
        'job.Skill',
        blank=True
    )
    resume = models.FileField(
        upload_to='resumes/'
    )

    linkedin = models.URLField(
        blank=True
    )

    github = models.URLField(
        blank=True
    )
    objective = models.TextField()


    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username
class Education(models.Model):
    job_seeker = models.ForeignKey(
        JobSeeker,
        on_delete=models.CASCADE
    )

    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    year_of_passing = models.IntegerField()
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
class WorkExperience(models.Model):
    job_seeker = models.ForeignKey(
        JobSeeker,
        on_delete=models.CASCADE
    )

    company_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(
        blank=True,
        null=True
    )

    currently_working = models.BooleanField(
        default=False
    )