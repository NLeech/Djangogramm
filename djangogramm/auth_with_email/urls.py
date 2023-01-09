from django.urls import path
from django.contrib.auth import views as auth_views

from auth_with_email import views, forms

app_name = "auth_with_email"
urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="auth_with_email/login.html",
            next_page="/",
            authentication_form=forms.LoginForm
        ),
        name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="/"),
        name="logout"),
    path(
        "signup/",
        views.SignUpView.as_view(),
        name='signup'),
    path(
        "profile/",
        views.ProfileEdit.as_view(),
        name="profile_edit"),
    path(
        "user/<int:pk>/",
        views.UserView.as_view(),
        name="profile"),
    path(
        "complete_registration/",
        views.CompleteRegistrationView.as_view(),
        name="complete_registration"),
    path(
        "activate/<uidb64>/<token>",
        views.ActivateView.as_view(),
        name="activate")
]
