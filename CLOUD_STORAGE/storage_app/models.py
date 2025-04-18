from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# class UserFile(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
#     file_name = models.CharField(max_length=255)
#     file_url = models.URLField(max_length=500)
#     file_size = models.IntegerField(default=0)  # Size in bytes
#     file_type = models.CharField(max_length=100)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.user.username} - {self.file_name}"


class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)
    file_url = models.URLField(max_length=500)
    file_size = models.IntegerField(default=0)  # Size in bytes
    file_type = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default='others')  # New field
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.file_name}"