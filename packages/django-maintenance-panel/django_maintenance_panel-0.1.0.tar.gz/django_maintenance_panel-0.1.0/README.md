# django-maintenance-panel

Simple reusable Django app that provides a maintenance mode logic:

- When `maintenance_mode` is off: nothing happens.
- When `maintenance_mode` is on:
  - Superusers see the site normally.
  - Staff (non-superusers) see a maintenance page **after login**, with a logout button.
  - Anonymous users & non-staff users see the site normally.

## Local install

Build and install:

    python -m pip install --upgrade build
    python -m build
    pip install .

## Django settings

    INSTALLED_APPS = [
        # ...
        "maintenance_panel",
    ]

    MIDDLEWARE = [
        # ...
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "maintenance_panel.middleware.MaintenanceModeMiddleware",
        # ...
    ]

    TEMPLATES = [
        {
            # ...
            "OPTIONS": {
                "context_processors": [
                    # ...
                    "maintenance_panel.context_processors.maintenance_context",
                ],
            },
        },
    ]

Then:

    python manage.py migrate maintenance_panel
