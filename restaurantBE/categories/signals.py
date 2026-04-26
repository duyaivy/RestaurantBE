from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from restaurantBE.categories.models import Category
CACHE_KEY_LIST = "category_list_all"
@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    """Invalidate category list cache when a category changes."""
    cache.delete(CACHE_KEY_LIST)
    # Also invalidate specific detail cache if we use it
    cache.delete(f"category_detail_{instance.id}")
