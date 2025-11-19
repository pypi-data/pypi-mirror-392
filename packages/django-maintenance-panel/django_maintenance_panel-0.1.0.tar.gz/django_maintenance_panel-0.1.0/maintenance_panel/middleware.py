from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from .models import SiteConfig


class MaintenanceModeMiddleware:
    """
    منطق:
      - اگر maintenance_mode خاموش باشد -> هیچ تاثیری ندارد.
      - اگر maintenance_mode روشن باشد:
          * سوپر یوزر (is_superuser=True) همه‌جا دسترسی کامل دارد.
          * همه می‌توانند لاگین/لاگ‌اوت کنند (admin:login, admin:logout).
          * اگر کاربر staff باشد و سوپر یوزر نباشد -> بعد از لاگین صفحه بروزرسانی را می‌بیند.
          * مهمان‌ها و کاربران عادی (non-staff) سایت را عادی می‌بینند.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # static / media را رها کن
        static_url = getattr(settings, "STATIC_URL", "/static/")
        media_url = getattr(settings, "MEDIA_URL", "/media/")

        if path.startswith(static_url) or path.startswith(media_url):
            return self.get_response(request)

        config = SiteConfig.get_solo()

        # اگر حالت بروزرسانی خاموش است
        if not config.maintenance_mode:
            return self.get_response(request)

        user = getattr(request, "user", None)

        # سوپر یوزر همیشه دسترسی کامل دارد
        if user and user.is_authenticated and user.is_superuser:
            return self.get_response(request)

        # آدرس‌های لاگین/لاگ‌اوت پنل ادمین همیشه آزاد هستند
        logout_url = reverse("admin:logout")
        login_url = reverse("admin:login")

        allowed_paths = [logout_url, login_url]

        if any(path.startswith(p) for p in allowed_paths):
            return self.get_response(request)

        # اگر کاربر لاگین کرده و staff است (ولی سوپر یوزر نیست) → پیام بروزرسانی ببیند
        if user and user.is_authenticated and user.is_staff:
            html = render_to_string(
                "maintenance_panel/maintenance.html",
                {
                    "message": config.maintenance_message,
                },
                request=request,
            )
            return HttpResponse(html, status=503)

        # بقیه (مهمان / non-staff) سایت را عادی می‌بینند
        return self.get_response(request)
