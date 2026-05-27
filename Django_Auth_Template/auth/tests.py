from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from django.urls import reverse

from .models import User, UserProfile
from .serializers import UserLoginSerializer, UserRegistrationSerializer


class AuthSerializerTests(TestCase):


	def setUp(self):
		self.client = APIClient()

	def test_registration_creates_user_and_profile(self):
		serializer = UserRegistrationSerializer(
			data={
				'email': 'alice@example.com',
				'password': 'StrongPass123!',
				'password_confirm': 'StrongPass123!',
				'first_name': 'Alice',
				'last_name': 'Liddell',
			}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		user = serializer.save()

		self.assertIsInstance(user, User)
		self.assertTrue(UserProfile.objects.filter(user=user).exists())
		self.assertTrue(User.objects.filter(email='alice@example.com').exists())

	def test_login_serializer_accepts_valid_credentials(self):
		user = User.objects.create_user(
			username='alice',
			email='alice@example.com',
			password='StrongPass123!',
		)

		serializer = UserLoginSerializer(data={'email': user.email, 'password': 'StrongPass123!'})

		self.assertTrue(serializer.is_valid(), serializer.errors)
		self.assertEqual(serializer.validated_data['user'], user)

	def test_refresh_and_logout_flow(self):
		user = User.objects.create_user(
			username='alice',
			email='alice@example.com',
			password='StrongPass123!',
		)

		login_response = self.client.post(
			reverse('login'),
			{'email': user.email, 'password': 'StrongPass123!'},
			format='json',
		)

		self.assertEqual(login_response.status_code, 200)
		refresh = login_response.data['refresh']

		refresh_response = self.client.post(
			reverse('refresh'),
			{'refresh': refresh},
			format='json',
		)
		self.assertEqual(refresh_response.status_code, 200)
		self.assertIn('access', refresh_response.data)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh_response.data['access']}")
		logout_response = self.client.post(reverse('logout'), {'refresh': refresh}, format='json')
		self.assertEqual(logout_response.status_code, 205)

		blacklisted_refresh_response = self.client.post(
			reverse('refresh'),
			{'refresh': refresh},
			format='json',
		)
		self.assertIn(blacklisted_refresh_response.status_code, {400, 401})

	def test_password_reset_flow(self):
		user = User.objects.create_user(
			username='alice',
			email='alice@example.com',
			password='StrongPass123!',
		)

		forgot_response = self.client.post(
			reverse('password-forgot'),
			{'email': user.email},
			format='json',
		)
		self.assertEqual(forgot_response.status_code, 200)

		uid = urlsafe_base64_encode(force_bytes(user.pk))
		token = default_token_generator.make_token(user)

		reset_response = self.client.post(
			reverse('password-reset'),
			{
				'uid': uid,
				'token': token,
				'password': 'NewStrongPass123!',
				'password_confirm': 'NewStrongPass123!',
			},
			format='json',
		)
		self.assertEqual(reset_response.status_code, 200)

		user.refresh_from_db()
		self.assertTrue(user.check_password('NewStrongPass123!'))
