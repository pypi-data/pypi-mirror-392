# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025, 2ps all rights reserved.

import os
import logging
from fastmcp.server.auth.providers.azure import AzureProvider
from fastmcp.server.auth.oauth_proxy import ProxyDCRClient
from mcp.shared.auth import OAuthClientInformationFull
from pydantic import AnyUrl


log = logging.getLogger('fastmcp')


class PatchedAzureProvider(AzureProvider):
    def _get_resource_url(self, mcp_path):
        return None  # Force v2.0 behavior

    def client_info_cache_structure(self, client_id, client_info: OAuthClientInformationFull = None):
        """
        creates the client info cache structure for a given client_id
        """
        log.info('creating client info cache structure for client_id: %s', client_id)
        client_secret = None
        redirect_uris = [AnyUrl('http://localhost')]
        grant_types = ['authorization_code', 'refresh_token']
        scope = self._default_scope_str
        if client_info:
            client_secret = client_info.client_secret
            redirect_uris = client_info.redirect_uris or redirect_uris
            grant_types = client_info.grant_types or grant_types
            scope = client_info.scope or scope
        proxy_client = ProxyDCRClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            scope=scope,
            token_endpoint_auth_method='none',
            allowed_redirect_uri_patterns=self._allowed_client_redirect_uris,
        )

        # Store as structured dict with all needed metadata
        storage_data = {
            'client': proxy_client.model_dump(mode='json'),
            'allowed_redirect_uri_patterns': self._allowed_client_redirect_uris,
        }
        log.info('-- storage_data: %s', storage_data)
        return storage_data

    async def cache_client_info(self, client_id, storage_data) -> None:
        try:
            await self._client_storage.set(client_id, storage_data)
        except AttributeError:
            await self._client_storage.put(client_id, storage_data)

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        '''
        Get client information by ID. This is generally the random ID
        provided to the DCR client during registration, not the upstream client ID.

        For unregistered clients, returns None (which will raise an error in the SDK).

        we have overridden this method because some stupid local clients cache
        the client id, and thus, those clients think they are already registered
        when they are not.
        '''
        # Load from storage
        log.info('getting client %s', client_id)
        data = await self._client_storage.get(client_id)
        log.info('-- data: %s', data)
        if not data:
            log.info('the client thinks it is already registered, but it isn\'t')
            data = self.client_info_cache_structure(client_id)
            await self.cache_client_info(client_id, data)

        if client_data := data.get('client', None):
            log.info('-- client_data: %s', client_data)
            return ProxyDCRClient(
                allowed_redirect_uri_patterns=data.get(
                    'allowed_redirect_uri_patterns', self._allowed_client_redirect_uris
                ),
                **client_data,
            )
        log.info('-- returning none')
        return None

    def authorize(self, *args, **kwargs):
        """
        overridden from base method to
        remove resource from auth_params if present
        """
        log.info('authorize called with args: %s, kwargs: %s', args, kwargs)
        if len(args) >= 2 and hasattr(args[1], 'resource'):
            # Create a copy of auth_params without the resource attribute
            auth_params = args[1]
            if hasattr(auth_params, '__dict__'):
                # Create new auth_params without resource
                new_values = {
                    k: v for k, v in auth_params.__dict__.items()
                    if k != 'resource'
                }
                new_auth_params = type(auth_params)(**new_values)
                args = (args[0], new_auth_params) + args[2:]
        return super().authorize(*args, **kwargs)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        '''Register a client locally

        When a client registers, we create a ProxyDCRClient that is more
        forgiving about validating redirect URIs, since the DCR client's
        redirect URI will likely be localhost or unknown to the proxied IDP. The
        proxied IDP only knows about this server's fixed redirect URI.

        we have to override it here because fastmcp 2.12.5 has a stupid bug
        where the default JsonStorage client storage doesn't actually implement
        the interface defined in py-key-value-aio, so the parent class's
        register_client method fails when used with redis (this is so stupid!).
        '''
        log.info('Registering client %s', client_info.client_id)
        # Create a ProxyDCRClient with configured redirect URI validation
        proxy_client = ProxyDCRClient(
            client_id=client_info.client_id,
            client_secret=client_info.client_secret,
            redirect_uris=client_info.redirect_uris or [AnyUrl('http://localhost')],
            grant_types=client_info.grant_types
            or ['authorization_code', 'refresh_token'],
            scope=client_info.scope or self._default_scope_str,
            token_endpoint_auth_method='none',
            allowed_redirect_uri_patterns=self._allowed_client_redirect_uris,
        )

        # Store as structured dict with all needed metadata
        storage_data = {
            'client': proxy_client.model_dump(mode='json'),
            'allowed_redirect_uri_patterns': self._allowed_client_redirect_uris,
        }
        await self.cache_client_info(client_info.client_id, storage_data)

        # Log redirect URIs to help users discover what patterns they might need
        if client_info.redirect_uris:
            for uri in client_info.redirect_uris:
                log.info(
                    'Client registered with redirect_uri: %s - if restricting redirect URIs, '
                    'ensure this pattern is allowed in allowed_client_redirect_uris',
                    uri,
                )

        log.info(
            'Registered client %s with %d redirect URIs',
            client_info.client_id,
            len(proxy_client.redirect_uris),
        )


def azure_auth(tenant_id=None, client_id=None, client_secret=None,
               base_url=None, redis_host=None,
               redis_db=None, redis_port=6379, scopes=None):
    """
    create an AzureProvider with optional Redis-backed client storage.
    you can either pass in the required parameters to the function.  if
    a parameter is not sent, we will try to source the value from the
    environment
    """
    from .redis import redis_auth_kwargs

    redis_host = redis_host or os.environ.get('REDIS_HOST')
    log.info('redis_host: [%s]', redis_host)
    if redis_host:
        redis_port = redis_port or os.environ.get('REDIS_PORT', '6379')
        redis_db = redis_db or os.environ.get('REDIS_DB', '0')
        auth_kwargs = redis_auth_kwargs(redis_host, redis_db, redis_port)
    else:
        auth_kwargs = {}
    scopes = scopes or ['openid', 'profile', 'email']
    tenant_id = tenant_id or os.environ.get('TENANT_ID')
    client_id = client_id or os.environ.get('CLIENT_ID')
    client_secret = client_secret or os.environ.get('CLIENT_SECRET')
    base_url = base_url or os.environ.get('PUBLIC_URL')
    auth = PatchedAzureProvider(
        # Provider's configuration URL
        # config_url=f'https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration',
        tenant_id=tenant_id,
        # Your registered app credentials
        client_id=client_id,
        client_secret=client_secret,

        # Your FastMCP server's public URL
        base_url=base_url,
        required_scopes=scopes,
        # allowed_client_redirect_uris=[],
        # allowed_client_redirect_uris=[ 'https://*', 'http://localhost:*' ],
        # Optional: customize the callback path (default is '/auth/callback')
        # redirect_path='/custom/callback',
        **auth_kwargs,
    )
    return auth
