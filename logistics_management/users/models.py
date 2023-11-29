from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    model_use_count = models.JSONField(default=dict)  # Store use count for each model as a JSON dictionary
    
    # New fields for gender and age
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"