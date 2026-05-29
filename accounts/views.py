from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout, get_user_model
from .serializers import UserSerializer, LoginSerializer, CreateUserSerializer
from .permissions import IsAdmin

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        user_data = UserSerializer(user).data
        return Response({
            'message': 'Login successful',
            'user': user_data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint
    """
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current logged-in user
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    User management - Admin only
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        user = self.get_object()
        if user == request.user:
            return Response(
                {'error': 'You cannot deactivate yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'message': 'User activated'})
