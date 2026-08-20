from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import Employe


class EmployeJWTAuthentication(JWTAuthentication):
    """
    Authentification JWT personnalisée qui résout le token vers un Employe
    (au lieu du User Django standard).
    """

    def get_user(self, validated_token):
        """
        Résout le user_id du token vers une instance Employe.
        """
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token contains no user_id')

        try:
            employe = Employe.objects.get(pk=user_id, actif=True)
        except Employe.DoesNotExist:
            raise InvalidToken('User not found')

        return employe