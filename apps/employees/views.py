from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from employees.serializers import EmployeeRegisterSerializer


class EmployeeRegisterView(generics.CreateAPIView):
    """
    Register a new employee with optional password and multipart profile picture upload.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = EmployeeRegisterSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                'success': True,
                'message': 'Employee registered successfully.',
                'data': {
                    'id': str(user.id),
                    'employee_id': user.employee_id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                }
            },
            status=status.HTTP_201_CREATED
        )