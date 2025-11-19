"""Django models for NetBox FreeIPA plugin."""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class FreeIPAHost(NetBoxModel):
    """
    Model representing a host enrolled in FreeIPA.
    
    This model stores information about hosts managed by FreeIPA identity
    management system.
    
    NOTE: This is a read-only mirror of FreeIPA data. No changes are made to FreeIPA.
    """
    
    clone_fields = []  # No cloning support needed for read-only data
    
    # Primary host information
    fqdn = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='FQDN',
        help_text='Fully qualified domain name of the host'
    )
    
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text='Description of the host'
    )
    
    # Host details from FreeIPA
    ipa_uuid = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='IPA UUID',
        help_text='Unique identifier in FreeIPA'
    )
    
    ssh_public_key = models.TextField(
        blank=True,
        verbose_name='SSH Public Key',
        help_text='SSH public key for the host'
    )
    
    # Metadata
    managed_by = models.CharField(
        max_length=255,
        blank=True,
        help_text='Entity managing this host in FreeIPA'
    )
    
    last_synced = models.DateTimeField(
        auto_now=True,
        help_text='Last time this record was synchronized with FreeIPA'
    )
    
    class Meta:
        ordering = ['fqdn']
        verbose_name = 'FreeIPA Host'
        verbose_name_plural = 'FreeIPA Hosts'
    
    def __str__(self):
        return self.fqdn
    
    def get_absolute_url(self):
        """Return the URL to view this host."""
        return reverse('plugins:netbox_freeipa:freeipahost', args=[self.pk])


class FreeIPADNSZone(NetBoxModel):
    """
    Model representing a DNS zone in FreeIPA.
    
    DNS zones contain DNS records for domains managed by FreeIPA.
    """
    
    clone_fields = []
    
    # Zone information
    zone_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Zone Name',
        help_text='DNS zone name (e.g., example.com)'
    )
    
    zone_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Zone Type',
        help_text='Type of DNS zone (master, forward, etc.)'
    )
    
    authoritative_nameserver = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Authoritative Nameserver',
        help_text='Primary nameserver for this zone'
    )
    
    administrator_email = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Administrator Email',
        help_text='Email address of the zone administrator'
    )
    
    serial_number = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Serial Number',
        help_text='SOA serial number'
    )
    
    refresh = models.IntegerField(
        null=True,
        blank=True,
        help_text='SOA refresh interval in seconds'
    )
    
    retry = models.IntegerField(
        null=True,
        blank=True,
        help_text='SOA retry interval in seconds'
    )
    
    expire = models.IntegerField(
        null=True,
        blank=True,
        help_text='SOA expire time in seconds'
    )
    
    minimum = models.IntegerField(
        null=True,
        blank=True,
        help_text='SOA minimum TTL in seconds'
    )
    
    ttl = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='TTL',
        help_text='Default time to live for records in seconds'
    )
    
    dynamic_update = models.BooleanField(
        default=False,
        verbose_name='Dynamic Update',
        help_text='Whether dynamic updates are allowed'
    )
    
    allow_sync_ptr = models.BooleanField(
        default=False,
        verbose_name='Allow Sync PTR',
        help_text='Whether PTR record synchronization is enabled'
    )
    
    last_synced = models.DateTimeField(
        auto_now=True,
        help_text='Last time this record was synchronized with FreeIPA'
    )
    
    class Meta:
        ordering = ['zone_name']
        verbose_name = 'FreeIPA DNS Zone'
        verbose_name_plural = 'FreeIPA DNS Zones'
    
    def __str__(self):
        return self.zone_name
    
    def get_absolute_url(self):
        """Return the URL to view this DNS zone."""
        return reverse('plugins:netbox_freeipa:freeipadnszone', args=[self.pk])


class FreeIPADNSRecord(NetBoxModel):
    """
    Model representing a DNS record in FreeIPA.
    
    DNS records are associated with zones and hosts.
    """
    
    clone_fields = []
    
    # Record information
    dns_zone = models.ForeignKey(
        FreeIPADNSZone,
        on_delete=models.CASCADE,
        related_name='dns_records',
        verbose_name='DNS Zone',
        help_text='DNS zone this record belongs to'
    )
    
    record_name = models.CharField(
        max_length=255,
        verbose_name='Record Name',
        help_text='DNS record name (hostname or subdomain)'
    )
    
    record_type = models.CharField(
        max_length=10,
        verbose_name='Record Type',
        help_text='DNS record type (A, AAAA, CNAME, PTR, etc.)'
    )
    
    record_value = models.CharField(
        max_length=500,
        verbose_name='Record Value',
        help_text='DNS record value (IP address, hostname, etc.)'
    )
    
    ttl = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='TTL',
        help_text='Time to live in seconds'
    )
    
    # Link to host if this is a host record
    host = models.ForeignKey(
        FreeIPAHost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dns_records',
        verbose_name='Associated Host',
        help_text='FreeIPA host associated with this DNS record'
    )
    
    last_synced = models.DateTimeField(
        auto_now=True,
        help_text='Last time this record was synchronized with FreeIPA'
    )
    
    class Meta:
        ordering = ['dns_zone', 'record_name', 'record_type']
        verbose_name = 'FreeIPA DNS Record'
        verbose_name_plural = 'FreeIPA DNS Records'
        unique_together = [['dns_zone', 'record_name', 'record_type', 'record_value']]
    
    def __str__(self):
        return f"{self.record_name}.{self.dns_zone.zone_name} ({self.record_type})"
    
    def get_absolute_url(self):
        """Return the URL to view this DNS record."""
        return reverse('plugins:netbox_freeipa:freeipadnsrecord', args=[self.pk])
    
    @property
    def fqdn(self):
        """Return the fully qualified domain name for this record."""
        if self.record_name == '@':
            return self.dns_zone.zone_name
        return f"{self.record_name}.{self.dns_zone.zone_name}"
