from django.views import generic
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator


from auth_with_email.models import User
from auth_with_email.forms import SignUpForm, CompleteRegistrationForm, ProfileEditForm
from auth_with_email.utils import RegistrationCompletedMixin, EmailConfirmationGeneratorMixin


class UserView(RegistrationCompletedMixin, generic.DetailView):
    template_name = "auth_with_email/user_view.html"
    model = User


class SignUpView(EmailConfirmationGeneratorMixin, generic.CreateView):
    model = User
    form_class = SignUpForm
    template_name = "auth_with_email/signup.html"

    def form_valid(self, form):
        super().form_valid(form)

        user = authenticate(
            self.request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password1"]
        )

        if user is not None:
            messages.add_message(self.request, messages.SUCCESS, f"User {user} successfully created")

            login(self.request, user)

            email = form.cleaned_data["email"]
            self.generate_confirmation_email(email)
        else:
            messages.add_message(self.request, messages.ERROR, f"Registration failed")
            return self.form_invalid(form)

        return HttpResponseRedirect(reverse("auth_with_email:complete_registration"))


class CompleteRegistrationView(LoginRequiredMixin, EmailConfirmationGeneratorMixin, View):
    template_name = "auth_with_email/complete_registration.html"

    form = CompleteRegistrationForm()

    def get(self, request, *args, **kwargs):
        self.form.fields["email"].initial = self.request.user.email
        return render(request, self.template_name, {"form": self.form})

    def post(self, request, *args, **kwargs):
        form = CompleteRegistrationForm(request.POST)
        if form.is_valid():

            email = form.cleaned_data["email"]
            self.generate_confirmation_email(email)

            return HttpResponseRedirect("/")

        else:
            messages.add_message(request, messages.ERROR, "Resending error")
            return HttpResponseRedirect(reverse("auth_with_email:complete_registration"))


class ActivateView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            user.registration_complete = True
            user.save()

            if request.user != user:
                login(request, user)

            messages.add_message(
                self.request, messages.SUCCESS,
                f"Thank you for your email confirmation. Now you can edit your profile."
            )
            return HttpResponseRedirect(reverse("auth_with_email:profile_edit"))
        else:
            messages.add_message(request, messages.ERROR, "Activation  link is invalid!")
            return HttpResponseRedirect(reverse("auth_with_email:complete_registration"))


class ProfileEdit(RegistrationCompletedMixin, generic.UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "auth_with_email/profile.html"

    # user can't edit another users profiles
    def get_object(self, queryset=None):
        return self.request.user

