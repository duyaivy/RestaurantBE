from django.db import models

# Create your models here.
class Guest(models.Model):
    """
    Guest model for temporary restaurant guests
    Login creates a new guest session with JWT tokens
    SimpleJWT handles token management via blacklist
    """
    name = models.CharField(max_length=100, null=False)
    tableNumber = models.ForeignKey('tables.Table', on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Guest"

    def __str__(self):
        return f"{self.name} - Table {self.tableNumber_id}"
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated guests"""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False"""
        return False
    
    @property
    def is_active(self):
        """Guests are always active (token validation handled by SimpleJWT)"""
        return True
    