from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.mail import BadHeaderError, send_mail
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string


class EmailConfirmationGeneratorMixin:
    def generate_confirmation_email(self, email) -> None:
        """
        Send registration confirmation email
        :param email: email recipient

        """
        if self.request.user.registration_complete:
            # the user has already completed his registration
            messages.add_message(self.request, messages.WARNING, f"User {self.request.user} is already activated!")
            return

        uid = urlsafe_base64_encode(force_bytes(self.request.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.request.user)
        context = {
            "user": self.request.user,
            "site": get_current_site(self.request),
            "uid": uid,
            "token": token
        }

        subject = "Please activate your account."
        body = render_to_string(template_name="auth_with_email/activation_email_body.html", context=context)
        try:
            send_mail(from_email=settings.EMAIL_HOST_USER, subject=subject, message=body, recipient_list=[email])
        except BadHeaderError:
            messages.add_message(self.request, messages.ERROR, f"Failed to send an activation link to {email}")
            return

        messages.add_message(self.request, messages.SUCCESS, f"The activation link was sent to you.")


class RegistrationCompletedMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.registration_complete:
            return HttpResponseRedirect(reverse("auth_with_email:complete_registration"))

        return super().dispatch(request, *args, **kwargs)


