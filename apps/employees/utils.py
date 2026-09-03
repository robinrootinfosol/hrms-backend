from datetime import datetime
from django.db import transaction
from django.contrib.auth import get_user_model


def generate_employee_id() -> str:
    """
    Generates a unique, sequential Employee ID using the current year.
    Format: EMP<YYYY><0000>
    """
    User = get_user_model()
    current_year = datetime.now().year
    prefix = f"EMP{current_year}"

    with transaction.atomic():
        last_user = (
            User.objects.select_for_update()
            .filter(employee_id__startswith=prefix)
            .order_by('-employee_id')
            .first()
        )

        if last_user and last_user.employee_id:
            try:
                last_sequence = int(last_user.employee_id.replace(prefix, ''))
                next_sequence = last_sequence + 1
            except ValueError:
                next_sequence = 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:04d}"