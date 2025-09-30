# usuarios/management/commands/create_user_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import UserProfile

class Command(BaseCommand):
    help = 'Crea UserProfiles para usuarios existentes que no tengan uno'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        created_count = 0
        
        for user in users_without_profile:
            # Crear perfil por defecto con rol RESIDENTE
            UserProfile.objects.create(
                user=user,
                role=UserProfile.Role.RESIDENTE
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Creado perfil para usuario: {user.username}')
            )
        
        if created_count == 0:
            self.stdout.write(
                self.style.WARNING('Todos los usuarios ya tienen perfil.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Se crearon {created_count} perfiles de usuario.')
            )