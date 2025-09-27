from django.conf import settings
from django.db import models

class DeviceToken(models.Model):
    PLATFORM_CHOICES = [
        ("android", "Android"),
        ("ios", "iOS"),
        ("web", "Web"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="device_tokens")
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device Token"
        verbose_name_plural = "Device Tokens"

    def __str__(self):
        return f"{self.user_id} - {self.platform} - {self.token[:10]}..."
