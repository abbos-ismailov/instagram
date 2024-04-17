from .models import User, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_DONE
from rest_framework import exceptions, serializers, generics
from django.db.models import Q
from api.base.utility import check_user_type, send_email, send_phone_code, check_username
from django.core.validators import FileExtensionValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, models



class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs) 
        self.fields["email_phone"] = serializers.CharField(required=False)
    
    
    class Meta:
        model= User
        fields = (
            "id",
            "auth_type",
            "auth_status"
        )
        extra_kwargs = {
            "auth_type": {"read_only": True, "required": False},
            "auth_status": {"read_only": True, "required": False}
        }
    
    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_EMAIL)
            # send_phone_code(user.phone, code)
            send_email(user.email, code)
        user.save()
        return user
    
    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data=data)
        
        return data
    
    def validate_email_phone(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                "success": False,
                "message": "Bu email bilan avval ro'yhatdan o'tilgan"
            }
            raise exceptions.ValidationError(data=data)
        
        elif value and User.objects.filter(phone=value).exists():
            data = {
                "success": False,
                "message": "Bu raqam bilan avval ro'yhatdan o'tilgan"
            }
            raise exceptions.ValidationError(data=data)
        
        return value

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get("email_phone")).lower()
        user_type = check_user_type(user_input)
        if user_type=="email":
            data = {
                "email": user_input,
                "auth_type":VIA_EMAIL,
            }
        
        elif user_type=="phone":
            data = {
                "phone": user_input,
                "auth_type":VIA_PHONE,
            }
        else:
            data = {
                "status": False,
                "message": "You have to send me email or phone number."
            }
            raise exceptions.ValidationError(data)
        
        return data

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class PersonalDataChangeSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get("password", None)
        confirm_password = data.get("confirm_password", None)
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if password != confirm_password:
            raise exceptions.ValidationError({
                "status": False,
                "message": "Parollar bir biriga teng bo'lishi kerak !!!"
            }) 
            
        if password:
            validate_password(password=password)

        if first_name != None and (len(first_name) < 3 or len(first_name) > 35):
            raise exceptions.ValidationError({
                "message": "First name must be between 3 and 35 characters"
            })
        
        if last_name != None and (len(last_name) < 3 or len(last_name) > 35):
            raise exceptions.ValidationError({
                "message": "Last name must be between 3 and 35 characters"
            })

        return data
    
    def validate_username(self, username):
        if check_username(username) == False:
            raise exceptions.ValidationError({
                "message": "Username must be between 3 and 35 characters"
            })
        
        if User.objects.filter(username=username).exists():
            raise exceptions.ValidationError({
                "message": "Bu username allaqachon olingan"
            })        
        
        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.password = validated_data.get("password", instance.password)

        if instance.password:
            instance.set_password(instance.password)
        
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        
        instance.save()
        return instance


class PhotoUserChangeSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[
        FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "svg", "heic", "heif", "webp"]
            )
    ])

    def update(self, instance, validated_data):
        photo = validated_data.get("photo", None)

        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()

        return instance


class LoginSerializer(TokenObtainPairSerializer):
    
    def __init__(self, *args, **kwargs) -> None:
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields["userinput"] = serializers.CharField(required=True)
        self.fields["username"] = serializers.CharField(required=False, read_only=True)
    
    def auth_validate(self, data):
        user_input = data.get("userinput") ### email, phone, username
        if check_user_type(user_input) == "username":
            username = user_input
        elif check_user_type(user_input) == "email":
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == "phone":
            user = self.get_user(phone=user_input)
            username = user.username
        else:
            raise exceptions.ValidationError({
                "status": False,
                "message": "Siz email, username yoki phone yuborishingiz kerak"
            })
    
        authentication_kwargs = {
            self.username_field: username,
            "password": data.get("password")
        }

        current_user = User.objects.filter(username__iexact=username).first() #### iexact receives upper and lower letters
        if current_user is not None and current_user.auth_status == DONE or PHOTO_DONE:
            user = authenticate(**authentication_kwargs)
            if user is not None:
                self.user = user
            else:
                raise exceptions.ValidationError({
                    "status": False,
                    "message": "Sorry, login or password You entered is incorrect, please cheack and try again."
                })
        else:
            raise exceptions.ValidationError({
                "status": False,
                "message": "Siz hali to'liq ro'yhatdan o'tmagansiz"
            })
        

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise exceptions.ValidationError(
                {
                    "status": False,
                    "message": "No active user"
                }
            )
        return users.first()

    def validate(self, data):
        self.auth_validate(data=data)
        data = self.user.token()
        data["auth_status"] = self.user.auth_status
        data["username"] = self.user.username
        return data
    

class LoginRefreshSerializer(TokenRefreshSerializer):
    
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data["access"])
        user_id = access_token_instance["user_id"]
        user = generics.get_object_or_404(User, id=user_id)
        models.update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgetPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        email_or_phone = attrs.get("email_or_phone", None)
        if email_or_phone is None:
            raise exceptions.ValidationError({
                "status": False,
                "message": "email yoki phone kiriting"
            })
        
        user = User.objects.filter(Q(email=email_or_phone) | Q(phone=email_or_phone))
        if not user.exists():
            raise exceptions.ValidationError({
                "status": False,
                "message": "User topilmadi"
            })
        attrs["user"] = user.first()
        return attrs
        

class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=8, required=True, write_only=True)
    
    class Meta:
        model = User
        fields = (
            "id",
            "password",
            "confirm_password"
        )
    
    def validate(self, attrs):
        password = attrs.get("password", None)
        confirm_password = attrs.get("confirm_password", None)
        
        if password != confirm_password:
            raise exceptions.ValidationError(
                {
                    "status": False,
                    "message": "Parollar bir biriga teng bolishi kerak"
                }
            )
        if password:
            validate_password(password)
        
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password")
        instance.set_password(password)
        
        return super(ResetPasswordSerializer, self).update(instance, validated_data)




