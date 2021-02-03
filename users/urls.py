from django.urls import path

from .views import (
    SignUpView,
    SignInView,
    MasterSignUpView,
    CategoryServiceView,
    KaKaoView,
    PasswordResetView,
    ProfileMainServiceView,
    ProfileIntroductionView,
    ProfileDescriptionView,
    ProfileListView,
    ProfileDetailView
)

urlpatterns = [
    path('/signup',SignUpView.as_view()),
    path('/signin',SignInView.as_view()),
    path('/master_signup',MasterSignUpView.as_view()),
    path('/category',CategoryServiceView.as_view()),
    path('/password_reset',PasswordResetView.as_view()),
    path('/kakao_signin',KaKaoView.as_view()),
    path('/profile',ProfileListView.as_view()),
    path('/profile/<int:master_id>',ProfileDetailView.as_view()),
    path('/profile_main_service',ProfileMainServiceView.as_view()),
    path('/profile_introduction',ProfileIntroductionView.as_view()),
    path('/profile_description',ProfileDescriptionView.as_view()),
]   
