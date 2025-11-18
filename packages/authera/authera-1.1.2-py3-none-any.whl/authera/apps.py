from django.apps import AppConfig


class AutheraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authera"


    def ready(self):
        from django.contrib.auth.models import Group
        from django.conf import settings

        # Create default groups if they don't exist
        for group in settings.USER_PERMISSIONS:
            Group.objects.get_or_create(name=group)