# admin/__init__.py
from admin.admin_auth import AdminAuth
from admin.admin_view import CategoryAdmin, ProductAdmin, UploadView, UserAdmin

__all__ = ["CategoryAdmin", "ProductAdmin", "UploadView", "UserAdmin"]