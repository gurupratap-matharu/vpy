# Generated by Django 5.1.6 on 2025-03-18 18:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0003_formpage_formfield"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.AddField(
            model_name="formpage",
            name="thank_you_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
            ),
        ),
    ]
