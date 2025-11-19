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
        
        # Check if host is enrolled
        enrolled = host_data.get('has_keytab', False)
        
        # Extract UUID
        ipa_uuid = host_data.get('ipauniqueid', [''])[0] if isinstance(
            host_data.get('ipauniqueid'), list
        ) else host_data.get('ipauniqueid', '')
        
        # Extract MAC address (take first if multiple)
        mac_address = ''
        if 'macaddress' in host_data:
            mac_list = host_data['macaddress']
            if isinstance(mac_list, list) and mac_list:
                mac_address = mac_list[0]
        
        # Extract IP address (take first if multiple)
        ip_address = None
        if 'ipaddress' in host_data:
            ip_list = host_data.get('ipaddress', [])
            if isinstance(ip_list, list) and ip_list:
                ip_address = ip_list[0]
        
        # Extract SSH public key (take first if multiple)
        ssh_public_key = ''
        if 'ipasshpubkey' in host_data:
            key_list = host_data['ipasshpubkey']
            if isinstance(key_list, list) and key_list:
                ssh_public_key = key_list[0]
        
        # Extract certificate information
        has_keytab = host_data.get('has_keytab', False)
        
        # Extract certificate subject and issuer if available
        certificate_subject = ''
        certificate_issuer = ''
        if 'usercertificate' in host_data:
            # Certificate parsing would go here
            # For now, we just note its presence
            pass
        
        # Extract managed by
        managed_by = host_data.get('managedby_host', [''])[0] if isinstance(
            host_data.get('managedby_host'), list
        ) else host_data.get('managedby_host', '')
        
        # Extract enrollment date from Kerberos principal creation
        enrollment_date = None
        if 'krbprincipalname' in host_data and 'krblastpwdchange' in host_data:
            # Parse enrollment date if available
            krblastpwdchange = host_data.get('krblastpwdchange', [None])[0]
            if krblastpwdchange:
                try:
                    # FreeIPA returns dates in generalized time format
                    enrollment_date = datetime.strptime(
                        krblastpwdchange, '%Y%m%d%H%M%SZ'
                    )
                except (ValueError, TypeError):
                    pass
        
        return {
            'fqdn': fqdn,
            'description': description,
            'enrolled': enrolled,
            'enrollment_date': enrollment_date,
            'ipa_uuid': ipa_uuid,
            'mac_address': mac_address,
            'ip_address': ip_address,
            'ssh_public_key': ssh_public_key,
            'has_keytab': has_keytab,
            'certificate_subject': certificate_subject,
            'certificate_issuer': certificate_issuer,
            'managed_by': managed_by,
        }
    
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
