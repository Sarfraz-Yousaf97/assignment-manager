# taskmanager/vies.py
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .models import User, Project, Task, ProjectRole
from .serializer import RegisterSerializer, ProjectSerializer, TaskSerializer, ProjectRoleSerializer, CustomTokenObtainPairSerializer
from .permissions import ProjectPermission, TaskPermission



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_verified=False)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = f"http:localhost:8000/api/verify/{uid}/{token}/"  # Update with actual domain
            send_mail(
                'Verify your email',
                f'Click the link to verify: {verification_link}',
                'noreply@yourdomain.com',
                [user.email],
            )
            return Response({"message": "User created, verification email sent"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                return Response({"message": "Email verified successfully"})
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid verification link"}, status=status.HTTP_400_BAD_REQUEST)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        return Project.objects.filter(roles__user=self.request.user).distinct()

    def perform_create(self, serializer):
        project = serializer.save(creator=self.request.user)
        ProjectRole.objects.create(project=project, user=self.request.user, role='ADMIN')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, ProjectPermission])
    def assign_role(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        if role not in ['ADMIN', 'MEMBER', 'VIEWER']:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, id=user_id)
        ProjectRole.objects.update_or_create(project=project, user=user, defaults={'role': role})
        return Response({"message": "Role assigned/updated"})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, ProjectPermission])
    def remove_role(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        role = ProjectRole.objects.filter(project=project, user=user)
        if role.exists():
            role.delete()
            return Response({"message": "Role removed"})
        return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

class ProjectTaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskPermission]

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return Task.objects.filter(project=project)

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer.save(project=project)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        role_obj = ProjectRole.objects.get(project=task.project, user=request.user)
        if role_obj.role == 'MEMBER':
            allowed_fields = {'status'}
            for key in request.data:
                if key not in allowed_fields:
                    return Response({"error": "Members can only update task status"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def assign(self, request, project_pk=None, pk=None):
        task = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        task.assigned_to = user
        task.save()
        return Response({"message": "Task assigned"})

    @action(detail=True, methods=['post'])
    def unassign(self, request, project_pk=None, pk=None):
        task = self.get_object()
        task.assigned_to = None
        task.save()
        return Response({"message": "Task unassigned"})