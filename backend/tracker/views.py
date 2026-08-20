from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

from .models import (
    Site,
    Employe,
    Coupure,
    SessionGroupe,
    PleineCarburant,
    ConsommationElectrique,
    CalculRatioCarburant,
    SeuillAlerte,
    Alerte,
    ScoreFiabiliteEmploye,
    AuditTrail,
)
from .serializers import (
    SiteSerializer,
    EmployeSerializer,
    EmployeCreateSerializer,
    CoupureSerializer,
    CoupureCloseSerializer,
    SessionGroupeSerializer,
    SessionGroupeStopSerializer,
    PleineCarburantSerializer,
    ConsommationElectriqueSerializer,
    CalculRatioCarburantSerializer,
    SeuillAlerteSerializer,
    AlerteSerializer,
    AlerteResolveSerializer,
    ScoreFiabiliteEmployeSerializer,
    AuditTrailSerializer,
)
from .permissions import (
    IsAdministratrice,
    IsEmploye,
    IsEmployeOwnSite,
)
from .services import (
    CalculateurRatioCarburant,
    DetecteurAnomalieCarburant,
    DetecteurAnomalieElectricite,
)
try:
    from .tasks.notifications import envoyer_alerte_telegram
except ImportError:
    envoyer_alerte_telegram = None


# ─────────────── AUTHENTIFICATION ───────────────

class AdminLoginView(APIView):
    """Connexion administratrice via email + mot de passe."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'email et password sont requis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.contrib.auth.hashers import check_password
        # Vérifier dans la table Employe avec role='administratrice'
        # Note : le mot de passe admin est stocké dans le champ email + django User
        # pour simplifier, on vérifie via email/password de User Django
        from django.contrib.auth import authenticate
        user = authenticate(username=email, password=password)

        if not user:
            return Response(
                {'detail': 'Identifiants invalides.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Trouver l'employé correspondant
        employe = Employe.objects.filter(email=email, actif=True).first()
        if not employe or employe.role != 'administratrice':
            return Response(
                {'detail': 'Accès non autorisé pour ce compte.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        refresh['user_id'] = str(employe.id)
        refresh['role'] = employe.role

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(employe.id),
                'email': employe.email,
                'nom': employe.nom,
                'prenom': employe.prenom,
                'role': employe.role,
            },
        })


class PINLoginView(APIView):
    """Connexion employé via PIN + site_id."""

    permission_classes = [AllowAny]

    def post(self, request):
        pin = request.data.get('pin')
        site_id = request.data.get('site_id')

        if not pin or not site_id:
            return Response(
                {'detail': 'pin et site_id sont requis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Brute-force protection : max 3 essais en 30s
        from django.core.cache import cache
        cache_key = f"pin_attempts_{site_id}_{pin}"
        attempts = cache.get(cache_key, 0)
        if attempts >= 3:
            return Response(
                {'detail': 'Trop de tentatives. Réessayez dans 30 secondes.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            employe = Employe.objects.get(
                site_id=site_id,
                role='employe',
                actif=True,
            )
        except Employe.DoesNotExist:
            return Response(
                {'detail': 'Aucun employé trouvé pour ce site.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not employe.verify_pin(pin):
            cache.set(cache_key, attempts + 1, timeout=30)
            return Response(
                {'detail': 'PIN invalide.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Reset compteur après succès
        cache.delete(cache_key)

        # Générer JWT access token (durée 8h, pas de refresh pour employé)
        from rest_framework_simplejwt.tokens import AccessToken
        import uuid

        payload = {
            'user_id': str(employe.id),
            'role': 'employe',
            'site_id': str(employe.site_id),
            'exp': timezone.now() + timedelta(hours=8),
            'iat': timezone.now(),
        }
        # Utiliser AccessToken.for_user avec un User Django factice
        # Ou générer manuellement
        from django.contrib.auth.models import User
        dummy_user, _ = User.objects.get_or_create(
            username=f"employe_{employe.id}",
            defaults={'is_active': True},
        )
        token = AccessToken.for_user(dummy_user)
        token['user_id'] = str(employe.id)
        token['role'] = 'employe'
        token['site_id'] = str(employe.site_id)

        return Response({
            'access': str(token),
            'user': {
                'id': str(employe.id),
                'prenom': employe.prenom,
                'nom': employe.nom,
                'site_id': str(employe.site_id),
                'role': employe.role,
            },
        })


# ─────────────── SITES ───────────────

class SiteViewSet(viewsets.ModelViewSet):
    """CRUD des sites. Admin uniquement pour écriture."""

    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [IsAdministratrice]

    def get_queryset(self):
        queryset = super().get_queryset()
        actif = self.request.query_params.get('actif')
        if actif is not None:
            queryset = queryset.filter(actif=actif.lower() == 'true')
        return queryset

    def perform_destroy(self, instance):
        # Soft-delete
        instance.actif = False
        instance.save()


# ─────────────── EMPLOYÉS ───────────────

class EmployeViewSet(viewsets.ModelViewSet):
    """Gestion des employés. Admin uniquement."""

    queryset = Employe.objects.all()
    permission_classes = [IsAdministratrice]

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeCreateSerializer
        return EmployeSerializer

    @action(detail=True, methods=['post'])
    def reset_pin(self, request, pk=None):
        """Réinitialiser le PIN d'un employé."""
        employe = self.get_object()
        new_pin = request.data.get('pin')
        if not new_pin or len(new_pin) != 4 or not new_pin.isdigit():
            return Response(
                {'detail': 'PIN doit être 4 chiffres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        employe.set_pin(new_pin)
        return Response({'detail': 'PIN réinitialisé avec succès.'})


# ─────────────── COUPURES ───────────────

class CoupureViewSet(viewsets.ModelViewSet):
    """Gestion des coupures électriques."""

    queryset = Coupure.objects.select_related('site', 'employe_id_declaration')
    serializer_class = CoupureSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAdministratrice()]
        return [IsEmployeOwnSite()]

    def get_queryset(self):
        queryset = self.queryset

        # Employé : uniquement son site
        if self.request.user.role == 'employe':
            queryset = queryset.filter(site_id=self.request.user.site_id)

        # Filtres admin
        site_id = self.request.query_params.get('site_id')
        statut = self.request.query_params.get('statut')
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def perform_create(self, serializer):
        site_id = serializer.validated_data['site'].id

        # Règle 1 : une seule coupure ouverte par site
        if Coupure.objects.filter(site_id=site_id, statut='ouverte').exists():
            raise serializers_validation_error("Une coupure est déjà ouverte pour ce site.")

        serializer.save(
            employe_id_declaration=self.request.user,
            statut='ouverte',
        )

    @action(detail=True, methods=['patch'])
    def close(self, request, pk=None):
        """Fermer une coupure."""
        coupure = self.get_object()

        if coupure.statut == 'fermee':
            return Response(
                {'detail': 'Cette coupure est déjà fermée.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role == 'employe' and request.user.site_id != coupure.site_id:
            return Response(
                {'detail': 'Accès refusé.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CoupureCloseSerializer(
            data=request.data,
            context={'coupure': coupure},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        date_fin = serializer.validated_data['date_fin']
        duree = (date_fin - coupure.date_debut).total_seconds() / 3600

        coupure.date_fin = date_fin
        coupure.duree_heures = round(duree, 2)
        coupure.statut = 'fermee'
        coupure.save()

        return Response(CoupureSerializer(coupure).data)


def serializers_validation_error(detail):
    from rest_framework.exceptions import ValidationError
    return ValidationError({'detail': detail})


# ─────────────── SESSIONS GROUPE ───────────────

class SessionGroupeViewSet(viewsets.ModelViewSet):
    """Gestion des sessions de groupe électrogène."""

    queryset = SessionGroupe.objects.select_related('site', 'employe_id_declaration')
    serializer_class = SessionGroupeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAdministratrice()]
        return [IsEmployeOwnSite()]

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.role == 'employe':
            queryset = queryset.filter(site_id=self.request.user.site_id)

        site_id = self.request.query_params.get('site_id')
        statut = self.request.query_params.get('statut')
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset

    def perform_create(self, serializer):
        site_id = serializer.validated_data['site'].id

        # Règle 2 : une seule session groupe ouverte par site
        if SessionGroupe.objects.filter(site_id=site_id, statut='en_cours').exists():
            raise serializers_validation_error("Une session groupe est déjà ouverte pour ce site.")

        serializer.save(
            employe_id_declaration=self.request.user,
            statut='en_cours',
        )

    @action(detail=True, methods=['patch'])
    def stop(self, request, pk=None):
        """Arrêter une session groupe."""
        session = self.get_object()

        if session.statut == 'fermee':
            return Response(
                {'detail': 'Cette session est déjà fermée.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role == 'employe' and request.user.site_id != session.site_id:
            return Response(
                {'detail': 'Accès refusé.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SessionGroupeStopSerializer(
            data=request.data,
            context={'session': session},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        timestamp_fin = serializer.validated_data['timestamp_fin']
        duree = (timestamp_fin - session.timestamp_debut).total_seconds() / 3600

        session.timestamp_fin = timestamp_fin
        session.duree_heures = round(duree, 2)
        session.statut = 'fermee'
        session.save()

        # Recalculer le ratio du mois après fermeture
        mois = session.timestamp_debut.date().replace(day=1)
        CalculateurRatioCarburant().calculer(site_id=session.site_id, mois_annee=mois)

        return Response(SessionGroupeSerializer(session).data)


# ─────────────── CARBURANT ───────────────

class PleineCarburantViewSet(viewsets.ModelViewSet):
    """Gestion des pleins de carburant."""

    queryset = PleineCarburant.objects.select_related('site', 'employe_id_declaration')
    serializer_class = PleineCarburantSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAdministratrice()]
        return [IsEmployeOwnSite()]

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.role == 'employe':
            queryset = queryset.filter(site_id=self.request.user.site_id)

        site_id = self.request.query_params.get('site_id')
        if site_id:
            queryset = queryset.filter(site_id=site_id)

        return queryset

    def perform_create(self, serializer):
        plein = serializer.save(employe_id_declaration=self.request.user)

        # Recalculer le ratio du mois après nouveau plein
        mois = plein.date_plein.replace(day=1)
        CalculateurRatioCarburant().calculer(site_id=plein.site_id, mois_annee=mois)


class CalculRatioCarburantViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture des ratios de consommation carburant."""

    queryset = CalculRatioCarburant.objects.select_related('site')
    serializer_class = CalculRatioCarburantSerializer
    permission_classes = [IsAdministratrice]

    def get_queryset(self):
        queryset = self.queryset
        site_id = self.request.query_params.get('site_id')
        mois = self.request.query_params.get('mois')
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if mois:
            from datetime import datetime
            mois_date = datetime.strptime(mois, '%Y-%m').date().replace(day=1)
            queryset = queryset.filter(mois_annee=mois_date)
        return queryset


# ─────────────── ÉLECTRICITÉ ───────────────

class ConsommationElectriqueViewSet(viewsets.ModelViewSet):
    """Gestion des consommations électriques mensuelles."""

    queryset = ConsommationElectrique.objects.select_related('site', 'employe_id_declarant')
    serializer_class = ConsommationElectriqueSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAdministratrice()]
        return [IsEmployeOwnSite()]

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.role == 'employe':
            queryset = queryset.filter(site_id=self.request.user.site_id)

        site_id = self.request.query_params.get('site_id')
        if site_id:
            queryset = queryset.filter(site_id=site_id)

        return queryset

    def perform_create(self, serializer):
        conso = serializer.save(employe_id_declarant=self.request.user)

        # Détecter anomalie électrique après enregistrement
        DetecteurAnomalieElectricite().detecter(
            site_id=conso.site_id,
            mois=conso.mois_annee,
        )


# ─────────────── ALERTES ───────────────

class AlerteViewSet(viewsets.ModelViewSet):
    """Gestion des alertes."""

    queryset = Alerte.objects.select_related('site', 'employe_id_lien')
    serializer_class = AlerteSerializer
    permission_classes = [IsAdministratrice]

    def get_queryset(self):
        queryset = self.queryset
        statut = self.request.query_params.get('statut')
        type_alerte = self.request.query_params.get('type_alerte')
        site_id = self.request.query_params.get('site_id')
        if statut:
            queryset = queryset.filter(statut=statut)
        if type_alerte:
            queryset = queryset.filter(type_alerte=type_alerte)
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        return queryset

    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """Résoudre une alerte."""
        alerte = self.get_object()

        if alerte.statut != 'actif':
            return Response(
                {'detail': 'Cette alerte n\'est plus active.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AlerteResolveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        alerte.statut = 'resolu'
        alerte.resolution_type = serializer.validated_data['resolution_type']
        alerte.resolution_note = serializer.validated_data.get('resolution_note', '')
        alerte.resolu_par = request.user
        alerte.date_resolution = timezone.now()
        alerte.save()

        return Response(AlerteSerializer(alerte).data)


# ─────────────── SEUILS ALERTE ───────────────

class SeuillAlerteView(APIView):
    """Configuration des seuils d'alerte."""

    permission_classes = [IsAdministratrice]

    def get(self, request):
        seuils = SeuillAlerte.get_solo()
        return Response(SeuillAlerteSerializer(seuils).data)

    def put(self, request):
        seuils = SeuillAlerte.get_solo()
        serializer = SeuillAlerteSerializer(seuils, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(modifie_par=request.user)
        return Response(serializer.data)


# ─────────────── SCORES FIABILITÉ ───────────────

class ScoreFiabiliteViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture des scores de fiabilité."""

    queryset = ScoreFiabiliteEmploye.objects.select_related('employe')
    serializer_class = ScoreFiabiliteEmployeSerializer
    permission_classes = [IsAdministratrice]

    def get_queryset(self):
        queryset = self.queryset
        employe_id = self.request.query_params.get('employe_id')
        mois = self.request.query_params.get('mois')
        if employe_id:
            queryset = queryset.filter(employe_id=employe_id)
        if mois:
            from datetime import datetime
            mois_date = datetime.strptime(mois, '%Y-%m').date().replace(day=1)
            queryset = queryset.filter(mois_annee=mois_date)
        return queryset


# ─────────────── AUDIT ───────────────

class AuditTrailViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture du journal d'audit."""

    queryset = AuditTrail.objects.select_related('employe')
    serializer_class = AuditTrailSerializer
    permission_classes = [IsAdministratrice]

    def get_queryset(self):
        queryset = self.queryset
        employe_id = self.request.query_params.get('employe_id')
        table = self.request.query_params.get('table_cible')
        if employe_id:
            queryset = queryset.filter(employe_id=employe_id)
        if table:
            queryset = queryset.filter(table_cible=table)
        return queryset


# ─────────────── DASHBOARD ───────────────

class DashboardView(APIView):
    """Vue synthétique pour l'administratrice."""

    permission_classes = [IsAdministratrice]

    def get(self, request):
        now = timezone.now()
        aujourdhui = now.date()
        premier_mois = aujourdhui.replace(day=1)

        # Sites actifs
        sites = Site.objects.filter(actif=True)
        sites_actifs = sites.count()

        # Coupures actives
        coupures_actives = Coupure.objects.filter(
            statut='ouverte',
        ).select_related('site', 'employe_id_declaration')
        coupures_data = [{
            'site_id': str(c.site_id),
            'nom_site': c.site.nom,
            'date_debut': c.date_debut,
            'duree_actuelle_heures': round((now - c.date_debut).total_seconds() / 3600, 2),
            'employe': f"{c.employe_id_declaration.prenom} {c.employe_id_declaration.nom}",
        } for c in coupures_actives]

        # Groupes actifs
        groupes_actifs = SessionGroupe.objects.filter(
            statut='en_cours',
        ).select_related('site')
        groupes_data = [{
            'site_id': str(g.site_id),
            'nom_site': g.site.nom,
            'timestamp_debut': g.timestamp_debut,
            'duree_actuelle_heures': round((now - g.timestamp_debut).total_seconds() / 3600, 2),
        } for g in groupes_actifs]

        # Alertes non résolues
        alertes = Alerte.objects.filter(
            statut='actif',
        ).select_related('site')[:20]
        alertes_data = [{
            'alerte_id': str(a.id),
            'type': a.type_alerte,
            'site': a.site.nom,
            'timestamp': a.timestamp_creation,
            'severite': a.severite,
            'motif_technique': a.motif_technique,
        } for a in alertes]

        # Scores fiabilité
        # Score du mois courant et du mois précédent
        mois_precedent = (premier_mois - timedelta(days=1)).replace(day=1)
        scores_mois = ScoreFiabiliteEmploye.objects.filter(
            mois_annee=premier_mois,
        ).select_related('employe')
        scores_precedent = {
            s.employe_id: s.score_final
            for s in ScoreFiabiliteEmploye.objects.filter(mois_annee=mois_precedent)
        }
        scores_data = [{
            'employe_id': str(s.employe_id),
            'nom': s.employe.nom,
            'prenom': s.employe.prenom,
            'score_mois_courant': s.score_final,
            'score_mois_precedent': scores_precedent.get(s.employe_id),
            'nombre_operations_mois': s.nombre_operations_mois,
        } for s in scores_mois]

        # Statistiques mensuelles
        stats = {
            'total_coupures_mois': Coupure.objects.filter(
                date_debut__year=aujourdhui.year,
                date_debut__month=aujourdhui.month,
            ).count(),
            'duree_totale_coupures_heures': round(
                Coupure.objects.filter(
                    date_debut__year=aujourdhui.year,
                    date_debut__month=aujourdhui.month,
                    duree_heures__isnull=False,
                ).aggregate(total=Sum('duree_heures'))['total'] or 0,
                2,
            ),
            'total_litres_carburant': PleineCarburant.objects.filter(
                date_plein__year=aujourdhui.year,
                date_plein__month=aujourdhui.month,
            ).aggregate(total=Sum('quantite_litres'))['total'] or 0,
            'ratio_moyen_carburant': CalculRatioCarburant.objects.filter(
                mois_annee=premier_mois,
            ).aggregate(moyenne=Avg('ratio_litres_par_heure'))['moyenne'] or 0,
            'consommation_electricite_kwh': ConsommationElectrique.objects.filter(
                mois_annee=premier_mois,
            ).aggregate(total=Sum('consommation_kwh'))['total'] or 0,
        }

        return Response({
            'sites_actifs': sites_actifs,
            'coupures_actives': coupures_data,
            'groupes_actifs': groupes_data,
            'alertes_non_resolues': alertes_data,
            'scores_fiabilite_employes': scores_data,
            'statistiques_mensuelles': stats,
        })


# ─────────────── HISTORIQUE MENSUEL ───────────────

class HistoriqueMensuelView(APIView):
    """Historique mensuel détaillé pour un site."""

    permission_classes = [IsAdministratrice]

    def get(self, request):
        site_id = request.query_params.get('site_id')
        mois = request.query_params.get('mois')

        if not site_id:
            return Response(
                {'detail': 'site_id est requis.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from datetime import datetime
            mois_date = datetime.strptime(mois, '%Y-%m').date().replace(day=1) if mois else None
        except (ValueError, TypeError):
            mois_date = None

        # 6 derniers mois de ratios
        if mois_date is None:
            mois_date = timezone.now().date().replace(day=1)
        debut = (mois_date - timedelta(days=192)).replace(day=1)

        ratios = CalculRatioCarburant.objects.filter(
            site_id=site_id,
            mois_annee__gte=debut,
            mois_annee__lte=mois_date,
        ).order_by('mois_annee')

        # 6 derniers mois de consommations électriques
        consos = ConsommationElectrique.objects.filter(
            site_id=site_id,
            mois_annee__gte=debut,
            mois_annee__lte=mois_date,
        ).order_by('mois_annee')

        # 6 derniers mois stats coupures
        coupures = Coupure.objects.filter(
            site_id=site_id,
            date_debut__gte=debut,
            date_debut__lt=(mois_date + timedelta(days=32)).replace(day=1),
        )

        return Response({
            'ratios_carburant': CalculRatioCarburantSerializer(ratios, many=True).data,
            'consommations_electriques': ConsommationElectriqueSerializer(consos, many=True).data,
            'statistiques_coupures': {
                'total': coupures.count(),
                'duree_totale_heures': round(
                    coupures.aggregate(total=Sum('duree_heures'))['total'] or 0,
                    2,
                ),
                'par_mois': list(
                    Coupure.objects.filter(
                        site_id=site_id,
                        date_debut__gte=debut,
                        date_debut__lt=(mois_date + timedelta(days=32)).replace(day=1),
                    ).values('date_debut__month').annotate(
                        total=Count('id'),
                        duree=Sum('duree_heures'),
                    ).order_by('date_debut__month')
                ),
            },
        })