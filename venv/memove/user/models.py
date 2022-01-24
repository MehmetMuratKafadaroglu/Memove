from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_agent = models.BooleanField(default=False)
    profile_photo = models.ImageField(null=True, upload_to="user_photos")
    phone = models.CharField(max_length=20, null=True)

    def make_agent(self):
        self.is_agent = True
        self.save()