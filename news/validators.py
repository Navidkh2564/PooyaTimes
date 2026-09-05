from django.core.exceptions import ValidationError


MAX_IMAGE_SIZE = 8 * 1024 * 1024
MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024


def validate_image_size(uploaded_file):
    if uploaded_file.size > MAX_IMAGE_SIZE:
        raise ValidationError('حجم تصویر نباید بیشتر از ۸ مگابایت باشد.')


def validate_attachment_size(uploaded_file):
    if uploaded_file.size > MAX_ATTACHMENT_SIZE:
        raise ValidationError('حجم فایل نباید بیشتر از ۲۰ مگابایت باشد.')
