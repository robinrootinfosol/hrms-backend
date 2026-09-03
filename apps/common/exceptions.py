from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = 'An error occurred'
        errors = {}

        if isinstance(response.data, dict):
            # If standard DRF detail exists, promote it to top-level message
            if 'detail' in response.data:
                message = str(response.data['detail'])
                # Everything other than 'detail' becomes field-level errors
                errors = {k: v for k, v in response.data.items() if k != 'detail'}
            else:
                errors = response.data
        elif isinstance(response.data, list):
            errors = {'non_field_errors': response.data}
        else:
            message = str(response.data)

        response.data = {
            'success': False,
            'message': message,
            'errors': errors,
            'status_code': response.status_code
        }

    return response