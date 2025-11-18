import datetime

from django.db import models
from django.utils import timezone
import zoneinfo


class Timezone(models.Model):
    owner = models.OneToOneField(
        "auth.User", related_name="timezone", primary_key=True, on_delete=models.CASCADE
    )
    timezone = models.CharField(max_length=32, default="UTC")

    def __str__(self):
        return self.timezone

    def activate(self):
        timezone.activate(self.tzinfo)

    def localtime(self) -> datetime.datetime:
        return timezone.localtime(timezone=self.tzinfo)

    def localdate(self) -> datetime.date:
        return timezone.localdate(timezone=self.tzinfo)

    @property
    def tzinfo(self) -> zoneinfo.ZoneInfo:
        return zoneinfo.ZoneInfo(self.timezone)

    @classmethod
    def for_user(cls, owner):
        obj, created = cls.objects.get_or_create(owner=owner)
        return obj
