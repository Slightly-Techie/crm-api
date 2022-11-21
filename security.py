from passlib.context import CryptContext


class Password:
    """A Password Class that provides a static method
    to verify a password and a static method to hash a password"""

    context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify(plain: str, hashed: str):
        """Takes plain password and hashed form
        and verifies if the hashed plain is equal to the hashed from user"""
        return Password.context.verify(secret=plain, hash=hashed)

    @staticmethod
    def hash(password: str):
        """Hashes password with bcrypt encryption context"""
        return Password.context.hash(secret=password)