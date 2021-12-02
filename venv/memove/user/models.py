from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
   are_you_an_agent = models.BooleanField(default=False)
   address = models.CharField(max_length=250, null=True)
   city = models.CharField(max_length=50, null=True)
   profile_photo = models.ImageField(null=True, upload_to="user_photos")
   postcode = models.CharField(max_length=50, null=True)
