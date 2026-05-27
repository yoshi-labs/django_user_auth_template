import re

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'date_of_birth', 'country', 'city']


class UserSerializer(serializers.ModelSerializer):
    """Serializer used for user responses."""

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_verified',
            'profile'
        ]
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    username = serializers.CharField(required = False,
                                     allow_blank = True,
                                     max_length = 150,
                                     help_text="Optional username; a unique one will be generated if needed" )
    
    password = serializers.CharField(write_only=True,
                                     required = True,
                                     validators = [validate_password],
                                     help_text="Password must contain at least 8 characters, including uppercase and lowercase letters." 
                                     )
    
    password_confirm = serializers.CharField(
                                    write_only=True,
                                    required=True,
                                    style={'input_type': 'password'},
                                    help_text="Confirm your password"
                                )
    
    class Meta: 
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'password',
            'password_confirm',
        ]

        extra_kwargs = {
            'id': {'read_only': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def validate_username(self, value):
        if not value:
            return value
        if len(value) < 3:
            raise serializers.ValidationError("Username must at least 3 characters long.")
        if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, dots, underscores and hyphens.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email already exists.")
        return value.lower()
    
    def validate_phone(self, value):
        """Validate phone number format."""
        if value and not re.match(r'^\+?[0-9]{7,20}$', value.replace(' ', '').replace('-', '')):
            raise serializers.ValidationError("Phone number is invalid.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        password = attrs.get("password")
        confirm_password = attrs.get("password_confirm")
        if confirm_password is None:
            confirm_password = attrs.get("password2")

        if password != confirm_password:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})

        return attrs

    def _generate_unique_username(self, preferred_username):
        """Return a username that does not collide with existing users."""
        base_username = re.sub(r'[^a-zA-Z0-9_.-]', '', preferred_username).strip('._-')

        if len(base_username) < 3:
            base_username = f"user{re.sub(r'[^0-9]', '', preferred_username)}"

        base_username = base_username[:140] or "user"
        candidate = base_username
        suffix = 1

        while User.objects.filter(username=candidate).exists():
            suffix_text = f"_{suffix}"
            candidate = f"{base_username[:150 - len(suffix_text)]}{suffix_text}"
            suffix += 1

        return candidate

    def create(self, validated_data):
        """Create new user."""
        validated_data.pop('password_confirm', None)
        preferred_username = validated_data.get('username') or validated_data['email'].split('@')[0]
        return User.objects.create_user(
            email=validated_data['email'],
            username=self._generate_unique_username(preferred_username),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
        )
UserRegistration = UserRegistrationSerializer


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login validation."""

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Authenticate user."""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email__iexact=email)
            authenticated_user = authenticate(username=user.username, password=password)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not authenticated_user:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not authenticated_user.is_active:
            raise serializers.ValidationError("User account is not active.")
        
        attrs['user'] = authenticated_user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Password fields did not match.'})
        return attrs

    def get_user(self):
        uid = self.validated_data.get('uid')
        token = self.validated_data.get('token')

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

        if not default_token_generator.check_token(user, token):
            return None

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with user claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['username'] = user.username
        token['phone'] = user.phone
        token['is_verified'] = user.is_verified
        
        return token
