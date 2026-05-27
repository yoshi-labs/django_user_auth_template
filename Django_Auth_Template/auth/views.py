from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
	ForgotPasswordSerializer,
	LogoutSerializer,
	ResetPasswordSerializer,
	UserLoginSerializer,
	UserRegistrationSerializer,
	UserSerializer,
)


class RegisterView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = UserRegistrationSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		refresh = RefreshToken.for_user(user)

		return Response(
			{
				'user': UserSerializer(user).data,
				'refresh': str(refresh),
				'access': str(refresh.access_token),
			},
			status=status.HTTP_201_CREATED,
		)


class LoginView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = UserLoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		refresh = RefreshToken.for_user(user)

		return Response(
			{
				'user': UserSerializer(user).data,
				'refresh': str(refresh),
				'access': str(refresh.access_token),
			},
			status=status.HTTP_200_OK,
		)


class MeView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		serializer = LogoutSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		try:
			token = RefreshToken(serializer.validated_data['refresh'])
			token.blacklist()
		except TokenError:
			return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

		return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)


class ForgotPasswordView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = ForgotPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = User.objects.filter(email__iexact=serializer.validated_data['email']).first()
		if user:
			uid = urlsafe_base64_encode(force_bytes(user.pk))
			token = default_token_generator.make_token(user)
			reset_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}?uid={uid}&token={token}"

			send_mail(
				subject='Reset your password',
				message=(
					'We received a password reset request.\n\n'
					f'Reset your password here: {reset_url}\n\n'
					'If you did not request this, you can ignore this email.'
				),
				from_email=settings.DEFAULT_FROM_EMAIL,
				recipient_list=[user.email],
				fail_silently=False,
			)

		return Response(
			{'detail': 'If an account exists for that email, a reset link has been sent.'},
			status=status.HTTP_200_OK,
		)


class ResetPasswordView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = ResetPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.get_user()

		if not user:
			return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

		user.set_password(serializer.validated_data['password'])
		user.save(update_fields=['password'])

		return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)
