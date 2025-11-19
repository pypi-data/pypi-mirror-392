from .models import SiteConfig


def maintenance_context(request):
    try:
        config = SiteConfig.get_solo()
    except Exception:
        return {}

    return {
        "maintenance_mode": config.maintenance_mode,
        "maintenance_message": config.maintenance_message,
    }
