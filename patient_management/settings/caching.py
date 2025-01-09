CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'patient_mgmt',
        'TIMEOUT': 300,  # 5 minutes default timeout
    },
    'event_store': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20
            },
        },
        'KEY_PREFIX': 'event_store',
        'TIMEOUT': 3600,  # 1 hour timeout for event store cache
    }
}

# Cache key patterns
CACHE_KEYS = {
    'patient_snapshot': 'patient:snapshot:{patient_id}',
    'patient_events': 'patient:events:{patient_id}',
    'clinical_events': 'clinical:events:{patient_id}',
    'lab_results': 'lab:results:{patient_id}:{lab_type}',
}

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'patient_snapshot': 300,  # 5 minutes
    'patient_events': 600,    # 10 minutes
    'clinical_events': 300,   # 5 minutes
    'lab_results': 1800,     # 30 minutes
}

# Cache version for cache invalidation
CACHE_VERSION = 1 