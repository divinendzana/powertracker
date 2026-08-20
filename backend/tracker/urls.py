from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminLoginView,
    PINLoginView,
    SiteViewSet,
    EmployeViewSet,
    CoupureViewSet,
    SessionGroupeViewSet,
    PleineCarburantViewSet,
    CalculRatioCarburantViewSet,
    ConsommationElectriqueViewSet,
    AlerteViewSet,
    SeuillAlerteView,
    ScoreFiabiliteViewSet,
    AuditTrailViewSet,
    DashboardView,
    HistoriqueMensuelView,
)

router = DefaultRouter()
router.register(r'sites', SiteViewSet, basename='sites')
router.register(r'employes', EmployeViewSet, basename='employes')
router.register(r'coupures', CoupureViewSet, basename='coupures')
router.register(r'sessions-groupe', SessionGroupeViewSet, basename='sessions-groupe')
router.register(r'pleins-carburant', PleineCarburantViewSet, basename='pleins-carburant')
router.register(r'ratios-carburant', CalculRatioCarburantViewSet, basename='ratios-carburant')
router.register(r'consommations-electricite', ConsommationElectriqueViewSet, basename='consommations-electricite')
router.register(r'alertes', AlerteViewSet, basename='alertes')
router.register(r'scores-fiabilite', ScoreFiabiliteViewSet, basename='scores-fiabilite')
router.register(r'audit', AuditTrailViewSet, basename='audit')

urlpatterns = [
    # Authentification
    path('auth/login/', AdminLoginView.as_view(), name='admin-login'),
    path('auth/login-pin/', PINLoginView.as_view(), name='pin-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('historique-mensuel/', HistoriqueMensuelView.as_view(), name='historique-mensuel'),

    # Seuils d'alerte
    path('seuils-alerte/', SeuillAlerteView.as_view(), name='seuils-alerte'),

    # Router
    path('', include(router.urls)),
]