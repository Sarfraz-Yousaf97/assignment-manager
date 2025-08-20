from rest_framework import permissions
from .models import ProjectRole

class ProjectPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        try:
            role_obj = ProjectRole.objects.get(project=obj, user=request.user)
        except ProjectRole.DoesNotExist:
            return False

        role = role_obj.role

        if request.method in permissions.SAFE_METHODS:
            return True

        return role == 'ADMIN'

class TaskPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        project_pk = view.kwargs.get('project_pk')
        if not project_pk:
            return False
        try:
            role_obj = ProjectRole.objects.get(project__pk=project_pk, user=request.user)
        except ProjectRole.DoesNotExist:
            return False

        role = role_obj.role

        if view.action in ['list', 'retrieve']:
            return True

        if view.action in ['create', 'destroy']:
            return role == 'ADMIN'

        if view.action == 'update':
            return role in ['ADMIN', 'MEMBER']

        if view.action in ['assign', 'unassign']:
            return role == 'ADMIN'

        return False