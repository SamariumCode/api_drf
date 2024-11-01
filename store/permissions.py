from rest_framework import permissions


# from rest_framework.permissions import SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method == 'GET' or (request.user and request.user.is_staff))

        # if request.method in permissions.SAFE_METHODS:
        #     return True
        # return bool(request.user and request.user.is_staff)


class SendPrivateEmail(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('store.send_private_email'))


import copy


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
