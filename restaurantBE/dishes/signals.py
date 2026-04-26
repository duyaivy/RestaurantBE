import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from restaurantBE.dishes.models import Dish
logger = logging.getLogger(__name__)
@receiver([post_save, post_delete], sender=Dish)
def invalidate_dish_cache(sender, instance, **kwargs):
    """
    Invalidate dish list cache and specific detail cache.
    Since list cache keys depend on query params, we use a pattern-based 
    invalidation or a simpler version: invalidate all keys starting with 'dish_list_'.
    Note: django-redis supports delete_pattern, but we'll use a version 
    that tracks keys or just clears the most common one if pattern isn't easy.
    Actually, django-redis HAS delete_pattern.
    """
    try:
        # Invalidate all variants of dish lists (different pages/filters)
        cache.delete_pattern("dish_list_*")
        # Invalidate specific dish detail
        cache.delete(f"dish_detail_{instance.id}")
        # Category detail also contains dishes, so invalidate it too
        if instance.category_id_id:
             cache.delete(f"category_detail_{instance.category_id_id}")
             # And category list just in case
             cache.delete("category_list_all")
        
        logger.info(f"Invalidated cache for dish {instance.id}")
    except Exception:
        logger.exception("Error invalidating dish cache")