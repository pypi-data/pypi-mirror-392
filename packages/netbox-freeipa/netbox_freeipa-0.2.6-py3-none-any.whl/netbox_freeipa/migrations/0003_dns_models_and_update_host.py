# Generated migration for DNS models and host model updates

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_freeipa', '0002_fix_fields'),
    ]

    operations = [
        # Remove fields from FreeIPAHost
        migrations.RemoveField(
            model_name='freeipahost',
            name='enrolled',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='enrollment_date',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='mac_address',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='ip_address',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='has_keytab',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='certificate_subject',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='certificate_issuer',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='certificate_valid_not_before',
        ),
        migrations.RemoveField(
            model_name='freeipahost',
            name='certificate_valid_not_after',
        ),
        
        # Create FreeIPADNSZone model
        migrations.CreateModel(
            name='FreeIPADNSZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('zone_name', models.CharField(help_text='DNS zone name (e.g., example.com)', max_length=255, unique=True, verbose_name='Zone Name')),
                ('zone_type', models.CharField(blank=True, help_text='Type of DNS zone (master, forward, etc.)', max_length=50, verbose_name='Zone Type')),
                ('authoritative_nameserver', models.CharField(blank=True, help_text='Primary nameserver for this zone', max_length=255, verbose_name='Authoritative Nameserver')),
                ('administrator_email', models.CharField(blank=True, help_text='Email address of the zone administrator', max_length=255, verbose_name='Administrator Email')),
                ('serial_number', models.BigIntegerField(blank=True, help_text='SOA serial number', null=True, verbose_name='Serial Number')),
                ('refresh', models.IntegerField(blank=True, help_text='SOA refresh interval in seconds', null=True)),
                ('retry', models.IntegerField(blank=True, help_text='SOA retry interval in seconds', null=True)),
                ('expire', models.IntegerField(blank=True, help_text='SOA expire time in seconds', null=True)),
                ('minimum', models.IntegerField(blank=True, help_text='SOA minimum TTL in seconds', null=True)),
                ('ttl', models.IntegerField(blank=True, help_text='Default time to live for records in seconds', null=True, verbose_name='TTL')),
                ('dynamic_update', models.BooleanField(default=False, help_text='Whether dynamic updates are allowed', verbose_name='Dynamic Update')),
                ('allow_sync_ptr', models.BooleanField(default=False, help_text='Whether PTR record synchronization is enabled', verbose_name='Allow Sync PTR')),
                ('last_synced', models.DateTimeField(auto_now=True, help_text='Last time this record was synchronized with FreeIPA')),
            ],
            options={
                'verbose_name': 'FreeIPA DNS Zone',
                'verbose_name_plural': 'FreeIPA DNS Zones',
                'ordering': ['zone_name'],
            },
        ),
        
        # Create FreeIPADNSRecord model
        migrations.CreateModel(
            name='FreeIPADNSRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('record_name', models.CharField(help_text='DNS record name (hostname or subdomain)', max_length=255, verbose_name='Record Name')),
                ('record_type', models.CharField(help_text='DNS record type (A, AAAA, CNAME, PTR, etc.)', max_length=10, verbose_name='Record Type')),
                ('record_value', models.CharField(help_text='DNS record value (IP address, hostname, etc.)', max_length=500, verbose_name='Record Value')),
                ('ttl', models.IntegerField(blank=True, help_text='Time to live in seconds', null=True, verbose_name='TTL')),
                ('last_synced', models.DateTimeField(auto_now=True, help_text='Last time this record was synchronized with FreeIPA')),
                ('dns_zone', models.ForeignKey(help_text='DNS zone this record belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='dns_records', to='netbox_freeipa.freeipadnszone', verbose_name='DNS Zone')),
                ('host', models.ForeignKey(blank=True, help_text='FreeIPA host associated with this DNS record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dns_records', to='netbox_freeipa.freeipahost', verbose_name='Associated Host')),
            ],
            options={
                'verbose_name': 'FreeIPA DNS Record',
                'verbose_name_plural': 'FreeIPA DNS Records',
                'ordering': ['dns_zone', 'record_name', 'record_type'],
                'unique_together': {('dns_zone', 'record_name', 'record_type', 'record_value')},
            },
        ),
    ]
