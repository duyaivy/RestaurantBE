
import uuid

class RandomUtils:
    @staticmethod
    def generateToken():
        """Generate a random UUID token"""
        return str(uuid.uuid4())
