"""FreeIPA API client for interacting with FreeIPA server."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from python_freeipa import ClientMeta
from python_freeipa.exceptions import FreeIPAError
from netbox.plugins import get_plugin_config


logger = logging.getLogger('netbox.plugins.netbox_freeipa')


class FreeIPAClient:
    """
    Client for interacting with FreeIPA API.
    
    This client handles authentication and provides methods to retrieve
    information about enrolled hosts from FreeIPA.
    """
    
    def __init__(self):
        """Initialize FreeIPA client with configuration from NetBox settings."""
        self.host = get_plugin_config('netbox_freeipa', 'freeipa_host')
        self.username = get_plugin_config('netbox_freeipa', 'freeipa_username')
        self.password = get_plugin_config('netbox_freeipa', 'freeipa_password')
        self.verify_ssl = get_plugin_config('netbox_freeipa', 'freeipa_verify_ssl', True)
        self.ca_cert = get_plugin_config('netbox_freeipa', 'freeipa_ca_cert')
        
        self._client = None
    
    def _get_client(self) -> ClientMeta:
        """
        Get or create FreeIPA client connection.
        
        Returns:
            ClientMeta: Connected FreeIPA client instance
        """
        if self._client is None:
            try:
                # Configure SSL verification
                verify_ssl = self.ca_cert if self.ca_cert else self.verify_ssl
                
                # Create client connection
                self._client = ClientMeta(
                    host=self.host,
                    verify_ssl=verify_ssl
                )
                
                # Login to FreeIPA
                self._client.login(self.username, self.password)
                logger.info(f"Successfully connected to FreeIPA server: {self.host}")
                
            except Exception as e:
                logger.error(f"Failed to connect to FreeIPA: {str(e)}")
                raise
        
        return self._client
    
    def disconnect(self):
        """Close the FreeIPA client connection."""
        if self._client:
            try:
                self._client.logout()
                logger.info("Disconnected from FreeIPA server")
            except Exception as e:
                logger.warning(f"Error during logout: {str(e)}")
            finally:
                self._client = None
    
    def get_all_hosts(self, page_size: Optional[int] = None) -> List[Dict]:
        """
        Retrieve all hosts enrolled in FreeIPA.
        
        Args:
            page_size: Number of hosts to retrieve per page. If None, uses plugin config.
        
        Returns:
            List of dictionaries containing host information
        """
        if page_size is None:
            page_size = get_plugin_config('netbox_freeipa', 'page_size', 100)
        
        try:
            client = self._get_client()
            
            # Get all hosts
            result = client.host_find(sizelimit=0)
            
            if result and 'result' in result:
                hosts = result['result']
                logger.info(f"Retrieved {len(hosts)} hosts from FreeIPA")
                return hosts
            else:
                logger.warning("No hosts found in FreeIPA or unexpected response format")
                return []
                
        except FreeIPAError as e:
            logger.error(f"FreeIPA error while retrieving hosts: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while retrieving hosts: {str(e)}")
            raise
    
    def get_host_details(self, fqdn: str) -> Optional[Dict]:
        """
        Retrieve detailed information about a specific host.
        
        Args:
            fqdn: Fully qualified domain name of the host
        
        Returns:
            Dictionary containing detailed host information, or None if not found
        """
        try:
            client = self._get_client()
            
            # Get host details
            result = client.host_show(fqdn)
            
            if result and 'result' in result:
                logger.info(f"Retrieved details for host: {fqdn}")
                return result['result']
            else:
                logger.warning(f"Host not found: {fqdn}")
                return None
                
        except FreeIPAError as e:
            logger.error(f"FreeIPA error while retrieving host {fqdn}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while retrieving host {fqdn}: {str(e)}")
            raise
    
    def parse_host_data(self, host_data: Dict) -> Dict:
        """
        Parse raw FreeIPA host data into a format suitable for NetBox model.
        
        Args:
            host_data: Raw host data from FreeIPA API
        
        Returns:
            Dictionary with parsed host information
        """
        # Extract FQDN (it's usually a list with one element)
        fqdn = host_data.get('fqdn', [''])[0] if isinstance(
            host_data.get('fqdn'), list
        ) else host_data.get('fqdn', '')
        
        # Extract description
        description = host_data.get('description', [''])[0] if isinstance(
            host_data.get('description'), list
        ) else host_data.get('description', '')
        
        # Extract UUID
        ipa_uuid = host_data.get('ipauniqueid', [''])[0] if isinstance(
            host_data.get('ipauniqueid'), list
        ) else host_data.get('ipauniqueid', '')
        
        # Extract SSH public key (take first if multiple)
        ssh_public_key = ''
        if 'ipasshpubkey' in host_data:
            key_list = host_data['ipasshpubkey']
            if isinstance(key_list, list) and key_list:
                ssh_public_key = key_list[0]
        
        # Extract managed by
        managed_by = host_data.get('managedby_host', [''])[0] if isinstance(
            host_data.get('managedby_host'), list
        ) else host_data.get('managedby_host', '')
        
        return {
            'fqdn': fqdn,
            'description': description,
            'ipa_uuid': ipa_uuid,
            'ssh_public_key': ssh_public_key,
            'managed_by': managed_by,
        }
    
    def get_all_dns_zones(self) -> List[Dict]:
        """
        Retrieve all DNS zones from FreeIPA.
        
        Returns:
            List of dictionaries containing DNS zone information
        """
        try:
            client = self._get_client()
            
            # Get all DNS zones
            result = client.dnszone_find(sizelimit=0)
            
            if result and 'result' in result:
                zones = result['result']
                logger.info(f"Retrieved {len(zones)} DNS zones from FreeIPA")
                return zones
            else:
                logger.warning("No DNS zones found in FreeIPA or unexpected response format")
                return []
                
        except FreeIPAError as e:
            logger.error(f"FreeIPA error while retrieving DNS zones: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while retrieving DNS zones: {str(e)}")
            raise
    
    def get_dns_records_for_zone(self, zone_name: str) -> List[Dict]:
        """
        Retrieve all DNS records for a specific zone.
        
        Args:
            zone_name: Name of the DNS zone
        
        Returns:
            List of dictionaries containing DNS record information
        """
        try:
            client = self._get_client()
            
            # Get all DNS records in the zone
            result = client.dnsrecord_find(zone_name, sizelimit=0)
            
            if result and 'result' in result:
                records = result['result']
                logger.info(f"Retrieved {len(records)} DNS records from zone {zone_name}")
                return records
            else:
                logger.warning(f"No DNS records found in zone {zone_name}")
                return []
                
        except FreeIPAError as e:
            logger.error(f"FreeIPA error while retrieving DNS records for zone {zone_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while retrieving DNS records for zone {zone_name}: {str(e)}")
            raise
    
    def parse_dns_zone_data(self, zone_data: Dict) -> Dict:
        """
        Parse raw FreeIPA DNS zone data into a format suitable for NetBox model.
        
        Args:
            zone_data: Raw DNS zone data from FreeIPA API
        
        Returns:
            Dictionary with parsed DNS zone information
        """
        def safe_extract(data, key, default=''):
            """Safely extract value from FreeIPA data, handling lists and dicts."""
            value = data.get(key, default)
            if isinstance(value, list):
                if len(value) > 0:
                    # If first element is a dict, try to get a string representation
                    if isinstance(value[0], dict):
                        # For dicts, try common keys or convert to string
                        return str(value[0].get('__dns_name__', value[0]))
                    return value[0]
                return default
            if isinstance(value, dict):
                # For dicts, try to get a meaningful string
                return str(value.get('__dns_name__', value))
            return value
        
        def safe_extract_int(data, key):
            """Safely extract integer value from FreeIPA data."""
            value = safe_extract(data, key, None)
            if value is None or value == '':
                return None
            try:
                # Handle string integers
                if isinstance(value, str):
                    return int(value)
                return int(value)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert {key}={value} to int")
                return None
        
        def safe_extract_bool(data, key, default=False):
            """Safely extract boolean value from FreeIPA data."""
            value = safe_extract(data, key, default)
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 'on')
            return bool(value)
        
        try:
            # Extract zone name - this is critical
            zone_name = safe_extract(zone_data, 'idnsname', '')
            
            # Remove trailing dot if present
            if zone_name and zone_name.endswith('.'):
                zone_name = zone_name[:-1]
            
            # Extract zone type
            zone_type = 'master'  # Default type
            if zone_data.get('idnsforwardpolicy'):
                zone_type = 'forward'
            
            # Extract SOA record fields - these might be in different formats
            soa_record = safe_extract(zone_data, 'idnssoamname', '')
            if soa_record and soa_record.endswith('.'):
                soa_record = soa_record[:-1]
            
            admin_email = safe_extract(zone_data, 'idnssoarname', '')
            if admin_email and admin_email.endswith('.'):
                admin_email = admin_email[:-1]
            
            # Extract integer fields
            serial_number = safe_extract_int(zone_data, 'idnssoaserial')
            refresh = safe_extract_int(zone_data, 'idnssoarefresh')
            retry = safe_extract_int(zone_data, 'idnssoaretry')
            expire = safe_extract_int(zone_data, 'idnssoaexpire')
            minimum = safe_extract_int(zone_data, 'idnssoaminimum')
            ttl = safe_extract_int(zone_data, 'dnsttl')
            
            # Extract boolean fields
            dynamic_update = safe_extract_bool(zone_data, 'idnsallowdynupdate', False)
            allow_sync_ptr = safe_extract_bool(zone_data, 'idnsallowsyncptr', False)
            
            return {
                'zone_name': zone_name,
                'zone_type': zone_type,
                'authoritative_nameserver': soa_record,
                'administrator_email': admin_email,
                'serial_number': serial_number,
                'refresh': refresh,
                'retry': retry,
                'expire': expire,
                'minimum': minimum,
                'ttl': ttl,
                'dynamic_update': dynamic_update,
                'allow_sync_ptr': allow_sync_ptr,
            }
        except Exception as e:
            logger.error(f"Error parsing DNS zone data: {str(e)}, data: {zone_data}")
            raise
    
    def parse_dns_record_data(self, record_data: Dict, zone_name: str) -> List[Dict]:
        """
        Parse raw FreeIPA DNS record data into a format suitable for NetBox model.
        
        Args:
            record_data: Raw DNS record data from FreeIPA API
            zone_name: Name of the DNS zone this record belongs to
        
        Returns:
            List of dictionaries with parsed DNS record information (one per record type/value)
        """
        def safe_extract_value(value):
            """Safely extract string value from various types."""
            if isinstance(value, dict):
                # For dict objects, try to extract meaningful value
                return str(value.get('__dns_name__', value))
            if isinstance(value, str):
                # Remove trailing dots from FQDN values
                return value.rstrip('.')
            return str(value)
        
        records = []
        
        try:
            # Extract record name
            idnsname_raw = record_data.get('idnsname', '')
            if isinstance(idnsname_raw, list):
                idnsname_raw = idnsname_raw[0] if idnsname_raw else ''
            
            # Apply safe extraction to handle dict objects
            record_name = safe_extract_value(idnsname_raw) if idnsname_raw else ''
            
            # Helper function to process record type
            def process_record_type(key, record_type):
                if key in record_data:
                    values = record_data[key]
                    if not isinstance(values, list):
                        values = [values]
                    
                    for value in values:
                        try:
                            clean_value = safe_extract_value(value)
                            if clean_value:  # Only add non-empty values
                                records.append({
                                    'record_name': record_name,
                                    'record_type': record_type,
                                    'record_value': clean_value,
                                    'zone_name': zone_name,
                                })
                        except Exception as e:
                            logger.warning(f"Could not process {record_type} record value {value}: {str(e)}")
            
            # Process all record types
            process_record_type('arecord', 'A')
            process_record_type('aaaarecord', 'AAAA')
            process_record_type('cnamerecord', 'CNAME')
            process_record_type('ptrrecord', 'PTR')
            process_record_type('txtrecord', 'TXT')
            process_record_type('mxrecord', 'MX')
            process_record_type('srvrecord', 'SRV')
            process_record_type('nsrecord', 'NS')
            
        except Exception as e:
            logger.error(f"Error parsing DNS record data for zone {zone_name}: {str(e)}, data: {record_data}")
        
        return records
    
    def sync_hosts(self) -> Dict[str, int]:
        """
        Synchronize all FreeIPA hosts with NetBox.
        
        Returns:
            Dictionary with sync statistics (created, updated, deleted counts)
        """
        from .models import FreeIPAHost
        
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
        }
        
        try:
            # Get all hosts from FreeIPA
            freeipa_hosts = self.get_all_hosts()
            freeipa_fqdns = set()
            
            # Process each host from FreeIPA
            for host_data in freeipa_hosts:
                try:
                    parsed_data = self.parse_host_data(host_data)
                    fqdn = parsed_data['fqdn']
                    
                    if not fqdn:
                        continue
                    
                    freeipa_fqdns.add(fqdn)
                    
                    # Create or update host in NetBox
                    try:
                        host, created = FreeIPAHost.objects.update_or_create(
                            fqdn=fqdn,
                            defaults=parsed_data
                        )
                        
                        if created:
                            stats['created'] += 1
                            logger.info(f"Created host: {fqdn}")
                        else:
                            stats['updated'] += 1
                            logger.debug(f"Updated host: {fqdn}")
                    except Exception as db_error:
                        stats['errors'] += 1
                        logger.error(f"Database error for host {fqdn}: {str(db_error)}")
                        continue
                
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error processing host: {str(e)}")
            
            # Delete hosts that no longer exist in FreeIPA
            deleted_count = FreeIPAHost.objects.exclude(
                fqdn__in=freeipa_fqdns
            ).delete()[0]
            stats['deleted'] = deleted_count
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} hosts no longer in FreeIPA")
            
            logger.info(
                f"Sync completed: {stats['created']} created, "
                f"{stats['updated']} updated, {stats['deleted']} deleted, "
                f"{stats['errors']} errors"
            )
            
        except Exception as e:
            logger.error(f"Error during host synchronization: {str(e)}")
            raise
        finally:
            self.disconnect()
        
        return stats
    
    def sync_dns_zones(self) -> Dict[str, int]:
        """
        Synchronize all FreeIPA DNS zones with NetBox.
        
        Returns:
            Dictionary with sync statistics (created, updated, deleted counts)
        """
        from .models import FreeIPADNSZone
        
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
        }
        
        try:
            # Get all DNS zones from FreeIPA
            freeipa_zones = self.get_all_dns_zones()
            freeipa_zone_names = set()
            
            # Process each zone from FreeIPA
            for zone_data in freeipa_zones:
                try:
                    parsed_data = self.parse_dns_zone_data(zone_data)
                    zone_name = parsed_data['zone_name']
                    
                    if not zone_name:
                        continue
                    
                    freeipa_zone_names.add(zone_name)
                    
                    # Create or update zone in NetBox
                    try:
                        zone, created = FreeIPADNSZone.objects.update_or_create(
                            zone_name=zone_name,
                            defaults=parsed_data
                        )
                        
                        if created:
                            stats['created'] += 1
                            logger.info(f"Created DNS zone: {zone_name}")
                        else:
                            stats['updated'] += 1
                            logger.debug(f"Updated DNS zone: {zone_name}")
                    except Exception as db_error:
                        stats['errors'] += 1
                        logger.error(f"Database error for zone {zone_name}: {str(db_error)}")
                        continue
                
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error processing DNS zone: {str(e)}")
            
            # Delete zones that no longer exist in FreeIPA
            deleted_count = FreeIPADNSZone.objects.exclude(
                zone_name__in=freeipa_zone_names
            ).delete()[0]
            stats['deleted'] = deleted_count
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} DNS zones no longer in FreeIPA")
            
            logger.info(
                f"DNS zone sync completed: {stats['created']} created, "
                f"{stats['updated']} updated, {stats['deleted']} deleted, "
                f"{stats['errors']} errors"
            )
            
        except Exception as e:
            logger.error(f"Error during DNS zone synchronization: {str(e)}")
            raise
        
        return stats
    
    def sync_dns_records(self) -> Dict[str, int]:
        """
        Synchronize all FreeIPA DNS records with NetBox.
        
        Returns:
            Dictionary with sync statistics (created, updated, deleted counts)
        """
        from .models import FreeIPADNSZone, FreeIPADNSRecord, FreeIPAHost
        from django.db import transaction
        
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
        }
        
        try:
            # Get all zones from NetBox
            zones = FreeIPADNSZone.objects.all()
            all_record_keys = set()
            
            # Use transaction.atomic to batch all database operations
            with transaction.atomic():
                for zone in zones:
                    try:
                        # Get records for this zone from FreeIPA
                        freeipa_records = self.get_dns_records_for_zone(zone.zone_name)
                        
                        for record_data in freeipa_records:
                            try:
                                # Parse the record data - returns a list of individual records
                                parsed_records = self.parse_dns_record_data(record_data, zone.zone_name)
                                
                                for parsed_data in parsed_records:
                                    record_name = parsed_data['record_name']
                                    record_type = parsed_data['record_type']
                                    record_value = parsed_data['record_value']
                                    
                                    # Create unique key for tracking
                                    record_key = (zone.id, record_name, record_type, record_value)
                                    all_record_keys.add(record_key)
                                    
                                    # Try to find associated host
                                    host = None
                                    if record_type in ['A', 'AAAA']:
                                        # Build FQDN from record name and zone
                                        if record_name == '@':
                                            fqdn = zone.zone_name
                                        else:
                                            fqdn = f"{record_name}.{zone.zone_name}"
                                        
                                        try:
                                            host = FreeIPAHost.objects.get(fqdn=fqdn)
                                        except FreeIPAHost.DoesNotExist:
                                            pass
                                    
                                    # Create or update record in NetBox
                                    try:
                                        # Check if record exists
                                        existing_record = FreeIPADNSRecord.objects.filter(
                                            dns_zone=zone,
                                            record_name=record_name,
                                            record_type=record_type,
                                            record_value=record_value
                                        ).first()
                                        
                                        if existing_record:
                                            # Update existing record
                                            if existing_record.host != host:
                                                existing_record.host = host
                                                existing_record.save(update_fields=['host', 'last_synced'])
                                            stats['updated'] += 1
                                        else:
                                            # Create new record
                                            FreeIPADNSRecord.objects.create(
                                                dns_zone=zone,
                                                record_name=record_name,
                                                record_type=record_type,
                                                record_value=record_value,
                                                host=host
                                            )
                                            stats['created'] += 1
                                            logger.debug(f"Created DNS record: {record_name}.{zone.zone_name} {record_type}")
                                    except Exception as db_error:
                                        stats['errors'] += 1
                                        logger.error(f"Database error for record {record_name}.{zone.zone_name}: {str(db_error)}")
                                        continue
                        
                            except Exception as e:
                                stats['errors'] += 1
                                logger.error(f"Error processing DNS record in zone {zone.zone_name}: {str(e)}")
                    
                    except Exception as e:
                        stats['errors'] += 1
                        logger.error(f"Error getting DNS records for zone {zone.zone_name}: {str(e)}")
                
                # Delete records that no longer exist in FreeIPA
                # Build Q objects for exclusion
                from django.db.models import Q
                exclude_q = Q(pk__in=[])  # Start with empty Q
                
                for zone_id, record_name, record_type, record_value in all_record_keys:
                    exclude_q |= Q(
                        dns_zone_id=zone_id,
                        record_name=record_name,
                        record_type=record_type,
                        record_value=record_value
                    )
                
                if all_record_keys:
                    deleted_count = FreeIPADNSRecord.objects.exclude(exclude_q).delete()[0]
                else:
                    deleted_count = FreeIPADNSRecord.objects.all().delete()[0]
                
                stats['deleted'] = deleted_count
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} DNS records no longer in FreeIPA")
            
            logger.info(
                f"DNS record sync completed: {stats['created']} created, "
                f"{stats['updated']} updated, {stats['deleted']} deleted, "
                f"{stats['errors']} errors"
            )
            
        except Exception as e:
            logger.error(f"Error during DNS record synchronization: {str(e)}")
            raise
        finally:
            self.disconnect()
        
        return stats
    
    def sync_all(self) -> Dict[str, Dict[str, int]]:
        """
        Synchronize all data from FreeIPA: hosts, DNS zones, and DNS records.
        
        Returns:
            Dictionary with sync statistics for each entity type
        """
        results = {}
        
        # Sync hosts
        try:
            results['hosts'] = self.sync_hosts()
        except Exception as e:
            logger.error(f"Failed to sync hosts: {str(e)}")
            results['hosts'] = {'error': str(e)}
        
        # Sync DNS zones
        try:
            results['dns_zones'] = self.sync_dns_zones()
        except Exception as e:
            logger.error(f"Failed to sync DNS zones: {str(e)}")
            results['dns_zones'] = {'error': str(e)}
        
        # Sync DNS records (must be after zones)
        try:
            results['dns_records'] = self.sync_dns_records()
        except Exception as e:
            logger.error(f"Failed to sync DNS records: {str(e)}")
            results['dns_records'] = {'error': str(e)}
        
        return results
