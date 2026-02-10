from django.db import models

# Create your models here.
class Guest(models.Model):
    name = models.CharField(max_length=100)
    tableNumber = models.ForeignKey('tables.Table', on_delete=models.CASCADE)
    refeshToken = models.CharField(max_length=255)
    refreshTokenExpiryAt = models.DateTimeField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Guest"

    def __str__(self):
        return self.name
    