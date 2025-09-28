from django.conf import settings
from django.db import models

class DeviceToken(models.Model):
    class Platform(models.TextChoices):
        ANDROID = "android", "Android"
        IOS     = "ios",     "iOS"
        WEB     = "web",     "Web"

    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_tokens",
        null=True, blank=True,
    )
    token     = models.CharField(max_length=255, unique=True)
    platform  = models.CharField(max_length=10, choices=Platform.choices)
    active    = models.BooleanField(default=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        owner = getattr(self.user, "username", "—") if self.user else "—"
        return f"{owner} · {self.platform}"

    class Meta:
        verbose_name = "Dispositivo (token push)"
        verbose_name_plural = "Dispositivos (tokens push)"


class Dispositivo(models.Model):
    # usa el user configurado, NO importes User directo
    usuario          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dispositivos')
    token_dispositivo= models.CharField(max_length=255, unique=True)
    activo           = models.BooleanField(default=True)
    fecha_creacion   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"

    def __str__(self):
        return f"Dispositivo de {getattr(self.usuario, 'username', self.usuario_id)}"
