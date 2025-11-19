"""Initial migration for NetBox FreeIPA plugin."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Create FreeIPAHost model."""

    initial = True

    dependencies = [
        ('extras', '0001_initial'),  # NetBox extras dependency
    ]

    operations = [
        migrations.CreateModel(
            name='FreeIPAHost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('fqdn', models.CharField(help_text='Fully qualified domain name of the host', max_length=255, unique=True, verbose_name='FQDN')),
                ('description', models.CharField(blank=True, help_text='Description of the host', max_length=200)),
                ('enrolled', models.BooleanField(default=False, help_text='Whether the host is currently enrolled in FreeIPA')),
                ('enrollment_date', models.DateTimeField(blank=True, help_text='Date and time when the host was enrolled', null=True)),
                ('ipa_uuid', models.CharField(blank=True, help_text='Unique identifier in FreeIPA', max_length=255, verbose_name='IPA UUID')),
                ('mac_address', models.CharField(blank=True, help_text='Primary MAC address of the host', max_length=17, verbose_name='MAC Address')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='Primary IP address of the host', null=True, verbose_name='IP Address')),
                ('ssh_public_key', models.TextField(blank=True, help_text='SSH public key for the host', verbose_name='SSH Public Key')),
                ('has_keytab', models.BooleanField(default=False, help_text='Whether the host has a Kerberos keytab', verbose_name='Has Keytab')),
                ('certificate_subject', models.CharField(blank=True, help_text='Certificate subject DN', max_length=500)),
                ('certificate_issuer', models.CharField(blank=True, help_text='Certificate issuer DN', max_length=500)),
                ('certificate_valid_not_before', models.DateTimeField(blank=True, help_text='Certificate validity start date', null=True)),
                ('certificate_valid_not_after', models.DateTimeField(blank=True, help_text='Certificate validity end date', null=True)),
                ('managed_by', models.CharField(blank=True, help_text='Entity managing this host in FreeIPA', max_length=255)),
                ('last_synced', models.DateTimeField(auto_now=True, help_text='Last time this record was synchronized with FreeIPA')),
                ('tags', models.ManyToManyField(blank=True, related_name='netbox_freeipa_freeipahost_tags', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'FreeIPA Host',
                'verbose_name_plural': 'FreeIPA Hosts',
                'ordering': ['fqdn'],
            },
        ),
    ]
