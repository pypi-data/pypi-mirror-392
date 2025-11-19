"""Django forms for NetBox FreeIPA plugin."""

from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField

from .models import FreeIPAHost


class FreeIPAHostForm(NetBoxModelForm):
    """Form for creating/editing FreeIPA hosts."""
    
    class Meta:
        model = FreeIPAHost
        fields = [
            'fqdn', 'description', 'enrolled', 'enrollment_date',
            'ipa_uuid', 'mac_address', 'ip_address', 'ssh_public_key',
            'has_keytab', 'certificate_subject', 'certificate_issuer',
            'certificate_valid_not_before', 'certificate_valid_not_after',
            'managed_by', 'tags'
        ]


class FreeIPAHostFilterForm(NetBoxModelFilterSetForm):
    """Filter form for FreeIPA hosts list."""
    
    model = FreeIPAHost
    
    fqdn = forms.CharField(
        required=False,
        label='FQDN'
    )
    
    enrolled = forms.NullBooleanField(
        required=False,
        label='Enrolled',
        widget=forms.Select(choices=(
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ))
    )
    
    has_keytab = forms.NullBooleanField(
        required=False,
        label='Has Keytab',
        widget=forms.Select(choices=(
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ))
    )
