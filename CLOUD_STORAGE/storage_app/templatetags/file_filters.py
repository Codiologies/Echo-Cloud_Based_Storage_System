from django import template

register = template.Library()

@register.filter
def is_image(file_type):
    """Check if the file type is an image."""
    return file_type and file_type.startswith('image/')

@register.filter
def is_video(file_type):
    """Check if the file type is a video."""
    return file_type and file_type.startswith('video/')

@register.filter
def is_audio(file_type):
    """Check if the file type is an audio file."""
    return file_type and file_type.startswith('audio/')

@register.filter
def is_pdf(file_type):
    """Check if the file type is a PDF."""
    return file_type == 'application/pdf' 