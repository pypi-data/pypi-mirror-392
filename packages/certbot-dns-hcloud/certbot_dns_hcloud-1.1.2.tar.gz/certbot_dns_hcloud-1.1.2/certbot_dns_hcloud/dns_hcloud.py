"""DNS authenticator for Hetzner Console"""
import logging
from typing import Any
from typing import Callable
from typing import Optional

import hcloud
import hcloud.zones

from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Hetzner Console

    This Authenticator uses the Hetzner Console API to fulfill a dns-01 challenge.
    """

    description = ('Obtain certificates using a DNS TXT record (if you are using Hetzner Console for'
                   'DNS).')
    ttl = 120

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.credentials: Optional[CredentialsConfiguration] = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None],
                             default_propagation_seconds: int = 60) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add('credentials', help='Hetzner Console credentials INI file.')
    
    def more_info(self) -> str:
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' \
               'the Hetzner Console API.'
    
    def _validate_credentials(self, credentials: CredentialsConfiguration) -> None:
        token = credentials.conf('api-token')
        if not token:
            raise errors.PluginError('{}: is required.'
                                     .format(credentials.confobj.filename))
    
    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'Hetzner Console credentials INI file.',
            None,
            self._validate_credentials)

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_hetzner_client().add_txt_record(domain, validation_name, validation, self.ttl)
    
    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_hetzner_client().del_txt_record(domain, validation_name, validation)

    def _get_hetzner_client(self) -> '_HClient':
        if not self.credentials:
            raise errors.Error('Plugin has not been prepared.')
        if self.credentials.conf('api-token'):
            return _HClient(api_token = self.credentials.conf('api-token'))



class _HClient:
    """Encapsulates all communication with the Hetzner Console API"""

    def __init__(self, api_token: str) -> None:
        self.client = hcloud.Client(token=api_token)

    def add_txt_record(self, domain: str, record_name: str, record_content: str,
                       record_ttl: int) -> None:
        """Add a TXT record using the supplied information.

        :param str domain: The domain to use to look up the Hetzner zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :param int record_ttl: The record TTL (number of seconds that the record may be cached).
        :raises certbot.errors.PluginError: if an error occures communicating with the Hetzner DNS
            API
        """
        zone = self._find_zone(domain)
        name = '.'.join(record_name.split('.')[:-len(zone.name.split('.'))])
        try:
            logger.debug('Attempting to add record for domain %s.', domain)
            self.client.zones.add_rrset_records(
                rrset=hcloud.zones.ZoneRRSet(
                    zone=zone,
                    name=name,
                    type="TXT"),
                ttl=record_ttl,
                records=[hcloud.zones.ZoneRecord(value='"' + record_content + '"')]
            ).wait_until_finished()
        except hcloud.HCloudException as e:
            logger.debug('Encountered HCloudException adding TXT record: %s', e)
            raise errors.PluginError('Encountered HCloudException adding TXT record: {}'.format(e))
        
        logger.debug('Successfully addded TXT record.')
    
    def del_txt_record(self, domain: str, record_name: str, record_content: str) -> None:
        """Delete a TXT record using the supplied information.
        
        Note that bothe the record's name and content are used to ensure that similar records
        created concurrently (e.g., due to concurrent invocations of this plugin) are not deleted.

        Failures are logged, but not raised.

        :param str domain: The domain to use to look up the Hetzner zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        """

        try:
            zone = self._find_zone(domain)
        except errors.PluginError as e:
            logger.debug('Encountered error finding zone during deletion: %s', e)
            return
        
        name = '.'.join(record_name.split('.')[:-len(zone.name.split('.'))])
        if zone:
            try:
                self.client.zones.remove_rrset_records(
                    rrset=hcloud.zones.ZoneRRSet(
                        zone=zone,
                        name=name,
                        type="TXT"),
                    records=[hcloud.zones.ZoneRecord(value='"' + record_content + '"')]
                ).wait_until_finished()
            except hcloud.HCloudException as e:
                logger.warning('Encountered HCloudException deleting TXT record: %s', e)
        else:
            logger.debug('Zone not found; no cleanup needed.')
        
    def _find_zone(self, domain: str) -> hcloud.zones.BoundZone:
        """Find the zone for a given domain.
        
        :param str domain: The domain for which to find the zone.
        :returns: The zone, if found.
        :rtype: hcloud.zones.BoundZone
        :raises certbot.errors.PluginError: if no zone is found.
        """

        zone_name_guesses = dns_common.base_domain_name_guesses(domain)

        try:
            zones = self.client.zones.get_all()
        except hcloud.HCloudException as e:
            logger.debug('Encountered HCloudException fetching zones from API to find zone: %s',
                         e)
            raise errors.PluginError('Encountered HCloudException fetching zones to find zone:' \
                                     ' %s'.format(e))

        for zone_name in zone_name_guesses:
            for zone in zones:
                if zone.name == zone_name:
                    logger.debug('Found zone (%s) for %s using name %s', str(zone.name), domain,
                                 zone_name)
                    return zone

        raise errors.PluginError('Unable to determine zone for {:} using zone names: {:}'
                                 .format(domain, zone_name_guesses))