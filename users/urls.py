from django.urls import path

from .views import (
    SignUpView,
    SignInView,
    MasterSignUpView,
    CategoryServiceView,
)

urlpatterns = [
    path('/signup',SignUpView.as_view()),
    path('/signin',SignInView.as_view()),
    path('/master_signup',MasterSignUpView.as_view()),
    path('/category',CategoryServiceView.as_view())
]   
