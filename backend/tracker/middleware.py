from django.utils import timezone
from .models import AuditTrail


class AuditMiddleware:
    """Middleware qui journalise les opérations POST/PUT/PATCH/DELETE."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Journalise uniquement les mutations
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Skip les endpoints d'audit pour éviter les boucles
            if request.path.startswith('/api/audit'):
                return response

            employe = request.user if request.user.is_authenticated else None

            AuditTrail.objects.create(
                timestamp=timezone.now(),
                employe=employe,
                action=f"{request.method} {request.path}",
                table_cible='request',
                adresse_ip=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )

        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')