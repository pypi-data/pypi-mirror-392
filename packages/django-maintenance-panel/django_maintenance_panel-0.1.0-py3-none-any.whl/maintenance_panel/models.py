from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteConfig(models.Model):
    maintenance_mode = models.BooleanField(
        _("فعال‌سازی حالت بروزرسانی"),
        default=False,
        help_text=_("اگر فعال شود، فقط کارمندان (staff) غیر سوپر یوزر صفحه بروزرسانی را می‌بینند."),
    )
    maintenance_message = models.CharField(
        _("پیام بروزرسانی"),
        max_length=255,
        default=_("سایت در حال بروزرسانی است. لطفاً دقایقی دیگر مراجعه کنید."),
    )
    updated_at = models.DateTimeField(_("آخرین بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("تنظیمات سایت")
        verbose_name_plural = _("تنظیمات سایت")

    def __str__(self):
        return "تنظیمات اصلی سایت"

    # فقط یک ردیف
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
