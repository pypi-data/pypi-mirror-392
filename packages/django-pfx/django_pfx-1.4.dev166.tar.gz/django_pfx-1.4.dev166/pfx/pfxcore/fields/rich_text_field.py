from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.signals import pre_save
from django.utils.safestring import mark_safe

import nh3


class RichTextField(models.TextField):
    """
    A TextField that automatically sanitizes HTML input using nh3.

    Args:
        nh3_config (str|None): Key of the NH3_CONFIGS dict from settings.
            Set to None to disable sanitization for this field.
    """
    def __init__(self, *args, nh3_config='default', **kwargs):
        super().__init__(*args, **kwargs)
        if nh3_config is None:
            self.nh3_kwargs = None
        else:
            if (not hasattr(settings, 'NH3_CONFIGS') or
                    nh3_config not in settings.NH3_CONFIGS):
                raise ImproperlyConfigured(
                    f"Missing NH3_CONFIGS['{nh3_config}'] configuration. "
                    "You must use an existing configuration or set "
                    "nh3_config=None to explicitly disable sanitization "
                    "for this field.")
            self.nh3_kwargs = settings.NH3_CONFIGS[nh3_config]

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Values are sanitized before saving, so any value returned from the DB
        # is safe to render unescaped.
        return mark_safe(value)

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only=private_only)

        if self.nh3_kwargs:
            # connect a pre_save signal for this field
            def sanitize(sender, instance, **kwargs):
                value = getattr(instance, name)
                if value:
                    clean_value = nh3.clean(value, **self.nh3_kwargs)
                    setattr(instance, name, mark_safe(clean_value))

            pre_save.connect(sanitize, sender=cls, weak=False)
