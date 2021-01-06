from rest_framework.permissions import IsAuthenticated
from .models import Project

class IsAllowedAccessToData(IsAuthenticated):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if super(IsAllowedAccessToData, self).has_permission(request, view):
            project_id = request.parser_context.get('kwargs', {}).get('project_id')
            if project_id is None:
                return False
            project = Project.objects.filter(id=project_id, users=request.user)
            return bool(project)
        else:
            return False