from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView, RegisterView, VerifyEmailView,
    ProjectViewSet, ProjectTaskViewSet
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

# Nested tasks under projects
from rest_framework_nested import routers

project_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
project_router.register(r'tasks', ProjectTaskViewSet, basename='project-task')

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
] + router.urls + project_router.urls