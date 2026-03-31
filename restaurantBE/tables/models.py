from restaurantBE.constants.choices import TableStatus
from django.db import models


class Table(models.Model):
    number = models.IntegerField(primary_key=True)
    capacity = models.IntegerField(null=False)
    status = models.CharField(
        max_length=20, choices=TableStatus.choices, default=TableStatus.AVAILABLE
    )
    token = models.CharField(max_length=255, null=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Table"
        ordering = ["number"]
        indexes = [
            models.Index(fields=["status"], name="idx_table_status"),
        ]

    def __str__(self):
        return f"Table {self.number}"
