# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # For Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your Gmail App Password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Same as EMAIL_HOST_USER 