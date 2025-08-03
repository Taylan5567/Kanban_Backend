from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    

    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return True

        # Schreibzugriffe nur für Staff
        return request.user and request.user.is_authenticated and request.user.is_staff
