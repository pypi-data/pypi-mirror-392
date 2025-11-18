# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0006_require_contenttypes_0002"),
    ]

    operations = [
        migrations.CreateModel(
            name="Timezone",
            fields=[
                (
                    "owner",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL,
                        related_name="timezone",
                        serialize=False,
                        primary_key=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                ("timezone", models.CharField(max_length=32)),
            ],
        ),
    ]
