from django.contrib import admin

# Register your models here.
from .models import User, Project, ProjectRole, Task


admin.site.register(User)
admin.site.register(Task)
admin.site.register(ProjectRole)
admin.site.register(ProjectRole)