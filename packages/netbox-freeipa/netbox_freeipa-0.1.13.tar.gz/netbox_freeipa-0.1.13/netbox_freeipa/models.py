"""Django models for NetBox FreeIPA plugin."""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class FreeIPAHost(NetBoxModel):
    """
    Model representing a host enrolled in FreeIPA.
    
    This model stores information about hosts managed by FreeIPA identity
    management system, including their enrollment status, certificates, and
    other relevant metadata.
    
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
    
    # Enrollment information
    enrolled = models.BooleanField(
        default=False,
        help_text='Whether the host is currently enrolled in FreeIPA'
    )
    
    enrollment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date and time when the host was enrolled'
    )
    
    # Host details from FreeIPA
    ipa_uuid = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='IPA UUID',
        help_text='Unique identifier in FreeIPA'
    )
    
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        verbose_name='MAC Address',
        help_text='Primary MAC address of the host'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address',
        help_text='Primary IP address of the host'
    )
    
    ssh_public_key = models.TextField(
        blank=True,
        verbose_name='SSH Public Key',
        help_text='SSH public key for the host'
    )
    
    # Certificate information
    has_keytab = models.BooleanField(
        default=False,
        verbose_name='Has Keytab',
        help_text='Whether the host has a Kerberos keytab'
    )
    
    certificate_subject = models.CharField(
        max_length=500,
        blank=True,
        help_text='Certificate subject DN'
    )
    
    certificate_issuer = models.CharField(
        max_length=500,
        blank=True,
        help_text='Certificate issuer DN'
    )
    
    certificate_valid_not_before = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Certificate validity start date'
    )
    
    certificate_valid_not_after = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Certificate validity end date'
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
    
    @property
    def is_certificate_valid(self):
        """Check if the host's certificate is currently valid."""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.certificate_valid_not_before or not self.certificate_valid_not_after:
            return None
        
        return (
            self.certificate_valid_not_before <= now <= 
            self.certificate_valid_not_after
        )
    
    @property
    def status_label(self):
        """Return a human-readable status label."""
        if not self.enrolled:
            return 'Not Enrolled'
        elif self.is_certificate_valid is False:
            return 'Certificate Expired'
        elif self.is_certificate_valid is True:
            return 'Active'
        else:
            return 'Enrolled'
