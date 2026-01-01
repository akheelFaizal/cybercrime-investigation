from django.core.exceptions import ValidationError
import os

def validate_evidence_file(file):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported file extension. Allowed: {", ".join(valid_extensions)}')
    
    if file.size > 5 * 1024 * 1024: # 5MB
        raise ValidationError('File too large. Max size is 5MB.')
