from django.contrib.auth import signals
from django.dispatch import receiver
from django.contrib import messages


@receiver(signals.user_logged_in)
def send_login_message(sender, request, user, **kwargs):
    messages.add_message(request, messages.SUCCESS, f"You have successfully logged in as {user}", fail_silently=True)


@receiver(signals.user_logged_out)
def send_logout_message(sender, request, **kwargs):
    messages.add_message(request, messages.WARNING, "You have successfully logged out", fail_silently=True)


@receiver(signals.user_login_failed)
def send_login_failed_message(sender, request, **kwargs):
    messages.add_message(request, messages.ERROR, "Login failed", fail_silently=True)
