from restaurantBE.constants.roles import DishStatus
from django.db import models


class Dish(models.Model):
    name = models.JSONField(null=False)
    price = models.IntegerField(null=False)
    description = models.JSONField(null=False)
    image = models.CharField(max_length=255, null=False)
    status = models.CharField(
        max_length=20, choices=DishStatus.choices, default=DishStatus.AVAILABLE
    )
    category_id = models.IntegerField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Dish"

    def __str__(self):
        return f"Dish {self.id}"
