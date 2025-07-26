from django.core.exceptions import ValidationError


def validate_file_size(value):
    file_size = value.size

    if file_size > 10485760:
        raise ValidationError("Вы не можете загружать файл размером более 10МБ")
    else:
        return value
