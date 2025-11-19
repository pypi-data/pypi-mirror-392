"""Fix custom_field_data and tags fields."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Fix field definitions for NetBox compatibility."""

    dependencies = [
        ('netbox_freeipa', '0001_initial'),
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freeipahost',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, editable=False),
        ),
        migrations.AlterField(
            model_name='freeipahost',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='+', to='extras.tag'),
        ),
    ]
