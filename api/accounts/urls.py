from django.urls import path
from .views import(CreateUserApiView, 
                   VerifyAPIView, 
                   NewVerifyCodeApiView, 
                   PersonalDataChangeApiView, 
                   ChangeUserPhotoApiView, 
                   LoginApiView, 
                   RefreshTokenApiView,
                   LogoutApiView,
                   ForgetPasswordView,
                   ResetPasswordApiView
                   )

urlpatterns = [
    path('login/', LoginApiView.as_view()),
    path('login/refresh/', RefreshTokenApiView.as_view()),
    path('logout/', LogoutApiView.as_view()),
    path('signup/', CreateUserApiView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-code/', NewVerifyCodeApiView.as_view()),
    path('data-change/', PersonalDataChangeApiView.as_view()),
    path('change-user-photo/', ChangeUserPhotoApiView.as_view()),
    path('forget-password/', ForgetPasswordView.as_view()),
    path('reset-password/', ResetPasswordApiView.as_view())   
]
