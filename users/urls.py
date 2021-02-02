from django.urls import path

from .views import (
    SignUpView,
    SignInView,
    MasterSignUpView,
    CategoryServiceView,
    PasswordResetView,
    KaKaoView,
)

urlpatterns = [
    path('/signup',SignUpView.as_view()),
    path('/signin',SignInView.as_view()),
    path('/master_signup',MasterSignUpView.as_view()),
    path('/category',CategoryServiceView.as_view()),
    path('/password_reset',PasswordResetView.as_view()),
    path('/kakao_signin',KaKaoView.as_view())
]   
