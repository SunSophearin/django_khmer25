from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    image = CloudinaryField("image", blank=True, null=True)

    def __str__(self):
        return self.user.username
