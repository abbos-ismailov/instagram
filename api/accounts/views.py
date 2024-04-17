from rest_framework.generics import CreateAPIView, views, UpdateAPIView
from rest_framework import permissions, exceptions, response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    SignUpSerializer, 
    PersonalDataChangeSerializer, 
    PhotoUserChangeSerializer, 
    LoginSerializer, 
    LoginRefreshSerializer, 
    LogoutSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer
)
from .models import User, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED
from datetime import datetime
from api.base.utility import send_email
from api.base.utility import check_user_type, send_email
# Create your views here.


class CreateUserApiView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializer


class VerifyAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwagrs):
        user = self.request.user
        code = self.request.data.get("code")

        self.check_verify(user, code)
        return response.Response(
            data={
                "status": True,
                "auth_status": user.auth_status,
                "access": user.token()["access"],
                "refresh": user.token()["refresh"],
                "auth_status": self.request.user.auth_status 
            }
        )

    @staticmethod
    def check_verify(user, code):
        verify = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)

        if not verify.exists():
            data = {
                "status": False,
                "message": "Sizning parolingiz xato yoki eskirgan !!!"
            }
            raise exceptions.ValidationError(data)
        else:
            verify.update(is_confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        
        return True


class NewVerifyCodeApiView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)

        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone, code)
            
        else:
            data = {
                "message": "Sizning email yoki nomeringiz tori kemadi"
            }
            raise exceptions.ValidationError(data)
        
        return response.Response(
            data={
                "status": True,
                "message": "Sizning yangi kodingiz emailingizga yuborildi",
                "auth_status": self.request.user.auth_status     
            }
        )
    
    @staticmethod
    def check_verification(user):
        verify = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verify.exists():
            data = {
                "status": False,
                "message": "Sizning parolingiz eskirmagan ozroq kuting !!!"
            }
            raise exceptions.ValidationError(data)


class PersonalDataChangeApiView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = PersonalDataChangeSerializer
    http_method_names = ["patch", "put"]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super(PersonalDataChangeApiView, self).update(request, *args, **kwargs)
        data = {
            "status": True,
            "message": "User updated successfully",
            "auth_status": self.request.user.auth_status
        }
        return response.Response(data, status=200)
    

    def partial_update(self, request, *args, **kwargs):
        super(PersonalDataChangeApiView, self).partial_update(request, *args, **kwargs)
        data = {
            "status": True,
            "message": "User updated successfully",
            "auth_status": self.request.user.auth_status
        }
        return response.Response(data, status=200)


class ChangeUserPhotoApiView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def patch(self, request, *args, **kwargs):
        serializer = PhotoUserChangeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            serializer.update(user, serializer.validated_data)
            return response.Response(
                {
                    "status": True,
                    "message": "Rasm muofaqqiyatli o'zgratirildi"
                }, 
                status=200
            )


class LoginApiView(TokenObtainPairView):
    serializer_class = LoginSerializer

 
class RefreshTokenApiView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogoutApiView(views.APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "status": True,
                "message": "You are logout successfully !!!"
            }
            return response.Response(data=data, status=205)
        except:
            return response.Response(status=404)


class ForgetPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_calss = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_calss(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get("email_or_phone")
        user = serializer.validated_data.get("user")
        
        if check_user_type(email_or_phone) == "phone":
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.email, code)
        
        elif check_user_type(email_or_phone) == "email":
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)

        return response.Response({
            "status": True,
            "message": "Tasdiqlash kode yuborildi",
            "access": user.token()["access"],
            "refresh": user.token()["refresh"],
            "user_status": user.auth_status
        }, status=200)
        

class ResetPasswordApiView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ResetPasswordSerializer
    http_method_names = ["patch", "put"]
    
    def get_object(self):
        return self.request.user #### this is for changing which user


    def update(self, request, *args, **kwargs):
        res = super(ResetPasswordApiView, self).update(request, *args, **kwargs)
        
        try:
            user = User.objects.get(id=res.data.get("id"))
        except Exception as e :
            raise exceptions.NotFound(
                detail="User not found"
            )
            
        return response.Response({
            "status": True,
            "message": "Muofaqqiyatli o'zgartirildi",
            "access": user.token()["access"],
            "refresh": user.token()["refresh"]
        })

