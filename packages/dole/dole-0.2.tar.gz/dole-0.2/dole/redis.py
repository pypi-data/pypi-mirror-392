# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025, 2ps all rights reserved.

import os
import logging
from key_value.aio.stores.redis import RedisStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper


log = logging.getLogger('fastmcp')


def redis_auth_kwargs(host=None, db=None, port=6379, url=None, encryption_key=None):
    if host:
        log.info('initializing redis store, host: [%s], port: [%s], db: [%s]', host, port, db)
        if db:
            try:
                db = int(db or 0)
            except ValueError:
                db = 0
        if port:
            try:
                port = int(port or 6379)
            except ValueError:
                port = 6379
        redis_store = RedisStore(
            host=host,
            port=port,
            db=db,
        )
    elif url:
        log.info('initializing redis store, url: [%s]', url)
        redis_store = RedisStore(url=url)
    # Optionally wrap with encryption
    encryption_key = encryption_key or os.environ.get('FERNET_ENCRYPTION_KEY')
    if encryption_key:
        log.info('Using encryption wrapper for Redis key-value store')
        redis_store = FernetEncryptionWrapper(
            redis_store,
            key=encryption_key,
        )
    return {
        'client_storage': redis_store
    }
