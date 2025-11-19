from django.contrib import admin
from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("maintenance_mode", "updated_at")
    fields = ("maintenance_mode", "maintenance_message")

    def has_add_permission(self, request):
        # فقط یک ردیف تنظیمات
        if SiteConfig.objects.exists():
            return False
        return super().has_add_permission(request)
