from django.core.cache import cache
from django.conf import settings
from typing import Any, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

def get_static_cache_key(key_type: str, identifier: str = '') -> str:
    """Generate a cache key for static data"""
    prefix = getattr(settings, 'STATIC_CACHE_KEY_PREFIX', 'static')
    return f"{prefix}:{key_type}:{identifier}"

def cache_static_lookup(key_type: str, identifier: str, data: Any) -> None:
    """Cache static lookup data with the configured timeout"""
    cache_key = get_static_cache_key(key_type, identifier)
    timeout = getattr(settings, 'STATIC_CACHE_TIMEOUT', 3600)  # Default 1 hour
    try:
        cache.set(
            cache_key,
            data,
            timeout=timeout
        )
        logger.debug(f"Cached static lookup: {cache_key}")
    except Exception as e:
        logger.error(f"Error caching static lookup {cache_key}: {str(e)}")

def get_static_lookup(key_type: str, identifier: str) -> Optional[Any]:
    """Retrieve static lookup data from cache"""
    cache_key = get_static_cache_key(key_type, identifier)
    try:
        data = cache.get(cache_key)
        if data is not None:
            logger.debug(f"Cache hit for static lookup: {cache_key}")
        else:
            logger.debug(f"Cache miss for static lookup: {cache_key}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving static lookup {cache_key}: {str(e)}")
        return None

def invalidate_static_lookup(key_type: str, identifier: str = '') -> None:
    """Invalidate a static lookup cache entry"""
    cache_key = get_static_cache_key(key_type, identifier)
    try:
        cache.delete(cache_key)
        logger.debug(f"Invalidated static lookup: {cache_key}")
    except Exception as e:
        logger.error(f"Error invalidating static lookup {cache_key}: {str(e)}")

def cache_static_choices(model_name: str, choices: List[tuple]) -> None:
    """Cache model choices (e.g., status choices, gender choices)"""
    cache_static_lookup('choices', model_name, choices)

def get_static_choices(model_name: str) -> Optional[List[tuple]]:
    """Retrieve cached model choices"""
    return get_static_lookup('choices', model_name)

# Example usage for common static data
def cache_common_lookups() -> None:
    """Cache commonly used static lookups"""
    from ..models import Patient, PatientNote
    
    # Cache model choices
    cache_static_choices('patient_gender', Patient.GENDER_CHOICES)
    cache_static_choices('note_categories', PatientNote.NOTE_CATEGORIES)
    
    # Cache other static data as needed
    common_statuses = ['active', 'inactive', 'pending']
    cache_static_lookup('common', 'statuses', common_statuses)
    
    logger.info("Cached common static lookups") 