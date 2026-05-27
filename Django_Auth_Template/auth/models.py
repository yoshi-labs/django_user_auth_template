from django.contrib.auth.models import AbstractUser
from django.db import models


# you should optionnaly customize user attributes relatively to your project user properties
# Create your models here.
class User(AbstractUser):
    """_summary_: Custom User Models 

    Fields:
       - username (str): Username of the user
       - email (str): Email address
       - password (str): Password of the user
       - phone: (Optionnal): phone number
       is_verified (bool): Whether the user has been verified
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["email"]


    def __str__(self):
        return f"user: {self.username} \n mail: {self.email}"


#Optionnal class for personalizing and get more about user informations
class UserProfile(models.Model):
    """
    User profile extension model for additional user details.
    
    Fields:
    - user: One-to-one relationship with User
    - bio: User biography
    - avatar: Profile avatar image
    - date_of_birth: User's date of birth
    - country: User's country
    - city: User's city
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        ordering = ['-created_at']
        verbose_name_plural = "Users Profile"
    
    def __str__(self):
        return f"Profile of {self.user.email}"
    
    def get_display_name(self):
        """Get user's display name."""
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.email

    