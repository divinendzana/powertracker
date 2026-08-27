r"""
Suite de tests backend PowerTracker (Étape 5 du roadmap).

Exécution :
    .venv\Scripts\python.exe backend\manage.py test tracker --parallel 1

Couvre :
- Modèles (règles save/get_solo/PIN bcrypt)
- Authentification (JWT admin, PIN employé, protection brute-force)
- Permissions par rôle
- Endpoints CRUD + actions métier (close, stop, resolve, reset_pin)
- Logique services (ratios L/h, détection anomalies, scores fiabilité)
- Dashboard / Historique / Seuils
"""
import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import (
    Site,
    Employe,
    Coupure,
    SessionGroupe,
    PleineCarburant,
    ConsommationElectrique,
    CalculRatioCarburant,
    Alerte,
    SeuillAlerte,
    ScoreFiabiliteEmploye,
    AuditTrail,
)
from .services import (
    CalculateurRatioCarburant,
    DetecteurAnomalieElectricite,
    DetecteurAnomalieCarburant,
    CalculateurScoreFiabilite,
)

# Redis/Docker n'étant pas encore disponibles, on exécute les tâches Celery en
# mode eager : aucune connexion au broker n'est tentée pendant les tests.
CELERY_EAGER = {
    'CELERY_TASK_ALWAYS_EAGER': True,
    'CELERY_TASK_EAGER_PROPAGATES': False,
}


class BaseAuthTestCase(TestCase):
    """Socle commun : jeux de données + helpers de connexion JWT/PIN."""

    ADMIN_EMAIL = 'divine.ndzana@camtel.cm'
    ADMIN_PASSWORD = 'Passw0rd-Secure!'
    EMPLOYE_PIN = '2468'

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(
            nom='Siège Douala',
            adresse='Boulevard de la Liberté',
            type_carburant='essence',
            puissance_kva=500,
        )
        cls.site_b = Site.objects.create(
            nom='Restaurant Yaoundé',
            adresse='Avenue Kennedy',
            type_carburant='gazoil',
            actif=False,
        )

        # Admin : un User Django (pour authenticate()) + l'Employe correspondant
        cls.admin_user = User.objects.create_user(
            username=cls.ADMIN_EMAIL,
            email=cls.ADMIN_EMAIL,
            password=cls.ADMIN_PASSWORD,
        )
        cls.admin = Employe.objects.create(
            prenom='Divine',
            nom='Ndzana',
            email=cls.ADMIN_EMAIL,
            role='administratrice',
            actif=True,
        )

        # Employés terrain (compte par PIN uniquement)
        cls.employe_a = Employe.objects.create(
            site=cls.site_a,
            prenom='Jean',
            nom='Mbarga',
            role='employe',
            actif=True,
        )
        cls.employe_a.set_pin(cls.EMPLOYE_PIN)
        cls.employe_a.save()

        cls.employe_b = Employe.objects.create(
            site=cls.site_b,
            prenom='Alice',
            nom='Fotso',
            role='employe',
            actif=True,
        )
        cls.employe_b.set_pin('1357')
        cls.employe_b.save()

    def setUp(self):
        self.client = APIClient()
        cache.clear()  # réinitialise les compteurs anti brute-force

    # ───────── Helpers de connexion ─────────

    def login_admin(self):
        res = self.client.post(
            reverse('admin-login'),
            {'email': self.ADMIN_EMAIL, 'password': self.ADMIN_PASSWORD},
            format='json',
        )
        self.assertEqual(res.status_code, 200, res.content)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        return res.data

    def login_employe(self, employe=None, pin=None):
        employe = employe or self.employe_a
        res = self.client.post(
            reverse('pin-login'),
            {'pin': pin or self.EMPLOYE_PIN, 'site_id': str(employe.site_id)},
            format='json',
        )
        self.assertEqual(res.status_code, 200, res.content)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        return res.data

    def auth_as(self, employe):
        """Forge directement un access token sans passer par les endpoints."""
        from rest_framework_simplejwt.tokens import AccessToken
        dummy_user, _ = User.objects.get_or_create(
            username=f'employe_{employe.id}',
            defaults={'is_active': True},
        )
        token = AccessToken.for_user(dummy_user)
        token['user_id'] = str(employe.id)
        token['role'] = employe.role
        if employe.site_id:
            token['site_id'] = str(employe.site_id)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # ───────── Factories ORM ─────────

    @staticmethod
    def make_coupure_fermee(site, employe, debut, heures):
        return Coupure.objects.create(
            site=site,
            date_debut=debut,
            date_fin=debut + timedelta(hours=heures),
            duree_heures=heures,
            employe_id_declaration=employe,
            statut='fermee',
        )

    @staticmethod
    def make_session_fermee(site, employe, debut, heures):
        return SessionGroupe.objects.create(
            site=site,
            timestamp_debut=debut,
            timestamp_fin=debut + timedelta(hours=heures),
            duree_heures=heures,
            employe_id_declaration=employe,
            statut='fermee',
        )

    @staticmethod
    def make_plein(site, employe, jours_arriere=5, litres=40.0, prix=830.0):
        return PleineCarburant.objects.create(
            site=site,
            quantite_litres=litres,
            prix_unitaire_fcfa=prix,
            date_plein=(timezone.now() - timedelta(days=jours_arriere)).date(),
            employe_id_declaration=employe,
        )


class ModelesTests(BaseAuthTestCase):
    """Règles métier au niveau des modèles."""

    def test_plein_calcule_montant_total_automatiquement(self):
        plein = self.make_plein(self.site_a, self.employe_a, jours_arriere=1,
                                litres=40, prix=830)
        self.assertAlmostEqual(plein.montant_total_fcfa, 33200.0)

    def test_montant_recalcule_apres_modification(self):
        plein = self.make_plein(self.site_a, self.employe_a, litres=10, prix=800)
        self.assertEqual(plein.montant_total_fcfa, 8000.0)
        plein.quantite_litres = 30
        plein.save()
        plein.refresh_from_db()
        self.assertEqual(plein.montant_total_fcfa, 24000.0)

    def test_seuill_alerte_est_un_singleton(self):
        s1 = SeuillAlerte.get_solo()
        s2 = SeuillAlerte.get_solo()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(SeuillAlerte.objects.count(), 1)
        self.assertEqual(s1.seuil_carburant_pct, 20.0)
        self.assertEqual(s1.seuil_electricite_pct, 30.0)

    def test_seuill_alerte_save_force_pk_1(self):
        rouge = SeuillAlerte(pk=42, seuil_carburant_pct=50)
        rouge.save()  # le save() écrase le pk à 1
        self.assertEqual(rouge.pk, 1)
        self.assertEqual(SeuillAlerte.objects.count(), 1)

    def test_set_pin_et_verify_pin(self):
        employe = Employe.objects.create(
            site=self.site_a, prenom='Test', nom='Pin', role='employe',
        )
        employe.set_pin('1234')
        employe.save()
        self.assertTrue(employe.pin_hash)
        self.assertNotEqual(employe.pin_hash, '1234')  # bien haché
        self.assertTrue(employe.verify_pin('1234'))
        self.assertFalse(employe.verify_pin('9999'))

    def test_verify_pin_sans_hash_retourne_faux(self):
        employe = Employe.objects.create(
            site=self.site_a, prenom='Test', nom='SansPin', role='employe',
        )
        self.assertFalse(employe.verify_pin('1234'))

    def test_representation_textuelle_des_modeles(self):
        debut = timezone.now()
        coupure = self.make_coupure_fermee(
            self.site_a, self.employe_a, debut, heures=2,
        )
        session = self.make_session_fermee(
            self.site_a, self.employe_a, debut, heures=2,
        )
        ratio = CalculRatioCarburant.objects.create(
            site=self.site_a, mois_annee=debut.date().replace(day=1),
            ratio_litres_par_heure=4.0, total_litres_periode=80,
            total_heures_groupe=20, nombre_pleins_periode=2,
            nombre_sessions_groupe=2,
        )
        self.assertIn('Siège Douala', str(coupure))
        self.assertIn('Siège Douala', str(session))
        self.assertIn('4.0 L/h', str(ratio))


@override_settings(**CELERY_EAGER)
class AdminLoginApiTests(BaseAuthTestCase):

    def test_connexion_admin_succes(self):
        data = self.login_admin()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['email'], self.ADMIN_EMAIL)
        self.assertEqual(data['user']['role'], 'administratrice')

    def test_token_admin_contient_role_et_user_id(self):
        from rest_framework_simplejwt.tokens import AccessToken
        data = self.login_admin()
        token = AccessToken(data['access'])
        self.assertEqual(str(token['user_id']), str(self.admin.id))
        self.assertEqual(token['role'], 'administratrice')

    def test_champs_manquants_400(self):
        res = self.client.post(reverse('admin-login'), {'email': 'x'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_mauvais_mot_de_passe_401(self):
        res = self.client.post(
            reverse('admin-login'),
            {'email': self.ADMIN_EMAIL, 'password': 'mauvais-mot-de-passe'},
            format='json',
        )
        self.assertEqual(res.status_code, 401)

    def test_compte_non_admin_403(self):
        email_employe = 'jean.mbarga@camtel.cm'
        User.objects.create_user(
            username=email_employe, email=email_employe, password='Passw0rd-X!',
        )
        self.employe_a.email = email_employe
        self.employe_a.save()
        res = self.client.post(
            reverse('admin-login'),
            {'email': email_employe, 'password': 'Passw0rd-X!'},
            format='json',
        )
        self.assertEqual(res.status_code, 403)


@override_settings(**CELERY_EAGER)
class PinLoginApiTests(BaseAuthTestCase):

    PIN_URL = '/api/auth/login-pin/'

    def test_connexion_pin_succes(self):
        data = self.login_employe(self.employe_a)
        self.assertIn('access', data)
        self.assertEqual(data['user']['id'], str(self.employe_a.id))
        self.assertEqual(data['user']['role'], 'employe')

    def test_token_employe_contient_site_id(self):
        from rest_framework_simplejwt.tokens import AccessToken
        data = self.login_employe(self.employe_b, pin='1357')
        token = AccessToken(data['access'])
        self.assertEqual(str(token['user_id']), str(self.employe_b.id))
        self.assertEqual(str(token['site_id']), str(self.site_b.id))

    def test_champs_manquants_400(self):
        res = self.client.post(self.PIN_URL, {'pin': '2468'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_site_inconnu_404(self):
        import uuid as uuid_mod
        res = self.client.post(
            self.PIN_URL, {'pin': '2468', 'site_id': str(uuid_mod.uuid4())},
            format='json',
        )
        self.assertEqual(res.status_code, 404)

    def test_employe_inactif_404(self):
        self.employe_a.actif = False
        self.employe_a.save()
        res = self.client.post(
            self.PIN_URL, {'pin': self.EMPLOYE_PIN, 'site_id': str(self.site_a.id)},
            format='json',
        )
        self.assertEqual(res.status_code, 404)

    def test_pin_invalide_401_et_compteur_incrementé(self):
        payload = {'pin': '9999', 'site_id': str(self.site_a.id)}
        res = self.client.post(self.PIN_URL, payload, format='json')
        self.assertEqual(res.status_code, 401)
        key = f"pin_attempts_{self.site_a.id}_9999"
        self.assertEqual(cache.get(key), 1)

    def test_blocage_apres_trois_tentatives_429(self):
        payload = {'pin': '9999', 'site_id': str(self.site_a.id)}
        for _ in range(3):
            self.client.post(self.PIN_URL, payload, format='json')
        res = self.client.post(self.PIN_URL, payload, format='json')
        self.assertEqual(res.status_code, 429)

    def test_succes_reinitialise_le_compteur_du_pin_utilise(self):
        url = self.PIN_URL
        self.client.post(url, {'pin': '9999', 'site_id': str(self.site_a.id)},
                         format='json')  # 1 échec sur le PIN 9999
        self.login_employe(self.employe_a, pin=self.EMPLOYE_PIN)  # succès

        # Comportement attendu : le succès n'affecte QUE son propre compteur,
        # le compteur du mauvais PIN conserve sa valeur (pas d'effet de bord
        # global), et un nouvel essai poursuit l'incrément normalement.
        res = self.client.post(url, {'pin': '9999',
                                     'site_id': str(self.site_a.id)},
                               format='json')
        self.assertEqual(res.status_code, 401)  # pas de blocage injustifié
        self.assertEqual(cache.get(f"pin_attempts_{self.site_a.id}_9999"), 2)


class PermissionsApiTests(BaseAuthTestCase):
    """Contrôle d'accès par rôle sur les endpoints sensibles."""

    def test_anonyme_401_sur_sites(self):
        res = self.client.get(reverse('sites-list'))
        self.assertEqual(res.status_code, 401)

    def test_employe_403_sur_liste_sites(self):
        self.auth_as(self.employe_a)
        res = self.client.get(reverse('sites-list'))
        self.assertEqual(res.status_code, 403)

    def test_admin_200_sur_liste_vide_ratios(self):
        self.login_admin()
        res = self.client.get(reverse('ratios-carburant-list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['results'], [])

    def test_token_invalide_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token.bidon.modifié')
        res = self.client.get(reverse('sites-list'))
        self.assertEqual(res.status_code, 401)

    def test_token_utilisateur_supprime_401(self):
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(self.admin_user)  # user_id = User.pk
        token['user_id'] = str(uuid.uuid4())           # Employe inexistant
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get(reverse('sites-list'))
        self.assertEqual(res.status_code, 401)


@override_settings(**CELERY_EAGER)
class SitesApiTests(BaseAuthTestCase):

    def test_admin_cree_un_site(self):
        self.login_admin()
        payload = {
            'nom': 'Annexe Bonapriso',
            'adresse': 'Rue Njo-Njo',
            'type_carburant': 'gazoil',
        }
        res = self.client.post(reverse('sites-list'), payload, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertTrue(Site.objects.filter(nom='Annexe Bonapriso').exists())

    def test_nom_de_site_unique_400(self):
        self.login_admin()
        res = self.client.post(
            reverse('sites-list'),
            {'nom': 'Siège Douala', 'adresse': 'doublon'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_filtre_actif(self):
        self.login_admin()
        res_actifs = self.client.get(reverse('sites-list'), {'actif': 'true'})
        res_inactifs = self.client.get(reverse('sites-list'), {'actif': 'false'})
        noms_actifs = [s['nom'] for s in res_actifs.data['results']]
        noms_inactifs = [s['nom'] for s in res_inactifs.data['results']]
        self.assertIn('Siège Douala', noms_actifs)
        self.assertNotIn('Restaurant Yaoundé', noms_actifs)
        self.assertIn('Restaurant Yaoundé', noms_inactifs)

    def test_patch_site_par_admin(self):
        self.login_admin()
        res = self.client.patch(
            reverse('sites-detail', args=[self.site_a.id]),
            {'puissance_kva': 750},
            format='json',
        )
        self.assertEqual(res.status_code, 200)
        self.site_a.refresh_from_db()
        self.assertEqual(self.site_a.puissance_kva, 750)

    def test_delete_est_un_soft_delete(self):
        self.login_admin()
        res = self.client.delete(reverse('sites-detail', args=[self.site_a.id]))
        self.assertIn(res.status_code, (200, 204))
        site = Site.objects.get(pk=self.site_a.id)  # toujours en base
        self.assertFalse(site.actif)

    def test_employe_ne_peut_pas_creer_un_site(self):
        self.auth_as(self.employe_a)
        res = self.client.post(
            reverse('sites-list'),
            {'nom': 'Site pirate', 'adresse': 'x'},
            format='json',
        )
        self.assertEqual(res.status_code, 403)


@override_settings(**CELERY_EAGER)
class EmployesApiTests(BaseAuthTestCase):

    def test_admin_liste_tous_les_employes(self):
        self.login_admin()
        res = self.client.get(reverse('employes-list'))
        self.assertEqual(res.status_code, 200)
        ids = {e['id'] for e in res.data['results']}
        self.assertEqual(len(ids), 3)  # admin + employe_a + employe_b

    def test_creation_employe_avec_pin_201(self):
        self.login_admin()
        payload = {
            'site': str(self.site_a.id),
            'prenom': 'Paul',
            'nom': 'Ebeke',
            'role': 'employe',
            'pin': '7890',
        }
        res = self.client.post(reverse('employes-list'), payload, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        employe = Employe.objects.get(nom='Ebeke')
        self.assertTrue(employe.verify_pin('7890'))
        self.assertFalse(employe.verify_pin('1111'))
        self.assertNotIn('pin', res.data)

    def test_creation_avec_pin_non_numerique_400(self):
        self.login_admin()
        res = self.client.post(
            reverse('employes-list'),
            {'site': str(self.site_a.id), 'prenom': 'X', 'nom': 'Y',
             'pin': '12ab'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_reset_pin_action(self):
        self.login_admin()
        url = reverse('employes-reset-pin', args=[self.employe_b.id])
        res = self.client.post(url, {'pin': '4321'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.employe_b.refresh_from_db()
        self.assertTrue(self.employe_b.verify_pin('4321'))

    def test_reset_pin_invalide_400(self):
        self.login_admin()
        url = reverse('employes-reset-pin', args=[self.employe_b.id])
        res = self.client.post(url, {'pin': '99'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_employe_acces_liste_interdit(self):
        self.auth_as(self.employe_a)
        res = self.client.get(reverse('employes-list'))
        self.assertEqual(res.status_code, 403)


@override_settings(**CELERY_EAGER)
class CoupuresApiTests(BaseAuthTestCase):

    def _payload_coupure(self, site):
        return {
            'site': str(site.id),
            'date_debut': timezone.now().isoformat(),
            'cause_descriptif': 'Délestage AES',
        }

    def test_employe_declare_une_coupure_ouverte(self):
        self.login_employe(self.employe_a)
        res = self.client.post(
            reverse('coupures-list'), self._payload_coupure(self.site_a),
            format='json',
        )
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.data['statut'], 'ouverte')
        coupure = Coupure.objects.get(id=res.data['id'])
        self.assertEqual(coupure.employe_id_declaration, self.employe_a)

    def test_une_seule_coupure_ouverte_par_site(self):
        Coupure.objects.create(
            site=self.site_a,
            date_debut=timezone.now(),
            employe_id_declaration=self.employe_a,
            statut='ouverte',
        )
        self.auth_as(self.employe_a)
        res = self.client.post(
            reverse('coupures-list'), self._payload_coupure(self.site_a),
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('déjà ouverte', str(res.data))

    def test_deux_sites_peuvent_avoir_chacun_sa_coupure(self):
        Coupure.objects.create(
            site=self.site_a, date_debut=timezone.now(),
            employe_id_declaration=self.employe_a, statut='ouverte',
        )
        self.auth_as(self.employe_b)
        res = self.client.post(
            reverse('coupures-list'), self._payload_coupure(self.site_b),
            format='json',
        )
        self.assertEqual(res.status_code, 201)

    def test_close_calcule_la_duree(self):
        debut = timezone.now() - timedelta(hours=3)
        coupure = Coupure.objects.create(
            site=self.site_a, date_debut=debut,
            employe_id_declaration=self.employe_a, statut='ouverte',
        )
        self.auth_as(self.employe_a)
        res = self.client.patch(
            reverse('coupures-close', args=[coupure.id]),
            {'date_fin': timezone.now().isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 200, res.content)
        coupure.refresh_from_db()
        self.assertEqual(coupure.statut, 'fermee')
        self.assertAlmostEqual(coupure.duree_heures, 3.0, delta=0.05)

    def test_close_date_fin_anterieure_au_debut_400(self):
        debut = timezone.now()
        coupure = Coupure.objects.create(
            site=self.site_a, date_debut=debut,
            employe_id_declaration=self.employe_a, statut='ouverte',
        )
        self.auth_as(self.employe_a)
        res = self.client.patch(
            reverse('coupures-close', args=[coupure.id]),
            {'date_fin': (debut - timedelta(minutes=10)).isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_close_sur_coupure_deja_fermee_400(self):
        coupure = self.make_coupure_fermee(
            self.site_a, self.employe_a, timezone.now(), heures=1,
        )
        self.auth_as(self.employe_a)
        res = self.client.patch(
            reverse('coupures-close', args=[coupure.id]),
            {'date_fin': timezone.now().isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_employee_autre_site_ne_voit_pas_la_coupure_404(self):
        coupure = Coupure.objects.create(
            site=self.site_b, date_debut=timezone.now(),
            employe_id_declaration=self.employe_b, statut='ouverte',
        )
        self.auth_as(self.employe_a)  # employé du site A
        res = self.client.get(reverse('coupures-detail', args=[coupure.id]))
        self.assertEqual(res.status_code, 404)

    def test_admin_voit_et_ferme_toutes_les_coupures(self):
        coupure_b = Coupure.objects.create(
            site=self.site_b, date_debut=timezone.now() - timedelta(hours=1),
            employe_id_declaration=self.employe_b, statut='ouverte',
        )
        self.make_coupure_fermee(
            self.site_a, self.employe_a, timezone.now(), heures=1,
        )
        self.login_admin()
        liste = self.client.get(reverse('coupures-list'))
        self.assertEqual(len(liste.data['results']), 2)
        res = self.client.patch(
            reverse('coupures-close', args=[coupure_b.id]),
            {'date_fin': timezone.now().isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 200)


@override_settings(**CELERY_EAGER)
class SessionsGroupeApiTests(BaseAuthTestCase):

    def _ouvrir_session(self, site):
        return {
            'site': str(site.id),
            'timestamp_debut': timezone.now().isoformat(),
        }

    def test_employe_declare_une_session_en_cours(self):
        self.login_employe(self.employe_a)
        res = self.client.post(
            reverse('sessions-groupe-list'), self._ouvrir_session(self.site_a),
            format='json',
        )
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.data['statut'], 'en_cours')
        session = SessionGroupe.objects.get(id=res.data['id'])
        self.assertEqual(session.employe_id_declaration, self.employe_a)

    def test_une_seule_session_ouverte_par_site(self):
        SessionGroupe.objects.create(
            site=self.site_a,
            timestamp_debut=timezone.now(),
            employe_id_declaration=self.employe_a,
            statut='en_cours',
        )
        self.auth_as(self.employe_a)
        res = self.client.post(
            reverse('sessions-groupe-list'), self._ouvrir_session(self.site_a),
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('déjà ouverte', str(res.data))

    def test_stop_calcule_la_duree_et_ferme(self):
        debut = timezone.now() - timedelta(hours=2, minutes=30)
        session = SessionGroupe.objects.create(
            site=self.site_a, timestamp_debut=debut,
            employe_id_declaration=self.employe_a, statut='en_cours',
        )
        self.auth_as(self.employe_a)
        res = self.client.patch(
            reverse('sessions-groupe-stop', args=[session.id]),
            {'timestamp_fin': timezone.now().isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 200, res.content)
        session.refresh_from_db()
        self.assertEqual(session.statut, 'fermee')
        self.assertAlmostEqual(session.duree_heures, 2.5, delta=0.05)

    def test_stop_sur_session_deja_fermee_400(self):
        session = self.make_session_fermee(
            self.site_a, self.employe_a, timezone.now(), heures=1,
        )
        self.auth_as(self.employe_a)
        res = self.client.patch(
            reverse('sessions-groupe-stop', args=[session.id]),
            {'timestamp_fin': timezone.now().isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_stop_recalcule_le_ratio_du_mois(self):
        maintenant = timezone.now()
        mois_courant = maintenant.date().replace(day=1)
        # Données du mois : 2 sessions fermées de 5 h + un plein de 40 L
        self.make_session_fermee(
            self.site_a, self.employe_a,
            maintenant.replace(day=2, hour=8), heures=5,
        )
        self.make_session_fermee(
            self.site_a, self.employe_a,
            maintenant.replace(day=3, hour=8), heures=5,
        )
        PleineCarburant.objects.create(
            site=self.site_a, quantite_litres=40, prix_unitaire_fcfa=800,
            date_plein=maintenant.date(),
            employe_id_declaration=self.employe_a,
        )
        session = SessionGroupe.objects.create(
            site=self.site_a,
            timestamp_debut=maintenant - timedelta(hours=1),
            employe_id_declaration=self.employe_a, statut='en_cours',
        )
        self.auth_as(self.employe_a)
        res = self.client.patch(
            reverse('sessions-groupe-stop', args=[session.id]),
            {'timestamp_fin': maintenant.isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 200, res.content)
        ratio = CalculRatioCarburant.objects.get(
            site=self.site_a, mois_annee=mois_courant,
        )
        self.assertAlmostEqual(ratio.total_heures_groupe, 11.0, delta=0.05)
        self.assertAlmostEqual(ratio.ratio_litres_par_heure, 40 / 11, delta=0.05)


@override_settings(**CELERY_EAGER)
class PleinsCarburantApiTests(BaseAuthTestCase):

    def test_employe_enregistre_un_plein_201(self):
        self.login_employe(self.employe_a)
        payload = {
            'site': str(self.site_a.id),
            'quantite_litres': 40,
            'prix_unitaire_fcfa': 850,
            'date_plein': timezone.now().date().isoformat(),
        }
        res = self.client.post(reverse('pleins-carburant-list'), payload,
                               format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertAlmostEqual(res.data['montant_total_fcfa'], 34000.0)
        plein = PleineCarburant.objects.get(id=res.data['id'])
        self.assertEqual(plein.employe_id_declaration, self.employe_a)

    def test_quantite_négative_400(self):
        self.login_employe(self.employe_a)
        res = self.client.post(
            reverse('pleins-carburant-list'),
            {'site': str(self.site_a.id), 'quantite_litres': -10,
             'prix_unitaire_fcfa': 800,
             'date_plein': timezone.now().date().isoformat()},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_date_futur_400(self):
        self.login_employe(self.employe_a)
        demain = (timezone.now() + timedelta(days=1)).date().isoformat()
        res = self.client.post(
            reverse('pleins-carburant-list'),
            {'site': str(self.site_a.id), 'quantite_litres': 10,
             'prix_unitaire_fcfa': 800, 'date_plein': demain},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_admin_liste_tous_les_pleins(self):
        self.make_plein(self.site_a, self.employe_a)
        self.make_plein(self.site_b, self.employe_b)
        self.login_admin()
        res = self.client.get(reverse('pleins-carburant-list'))
        self.assertEqual(len(res.data['results']), 2)


@override_settings(**CELERY_EAGER)
class ConsommationElectriqueApiTests(BaseAuthTestCase):

    def test_employe_declare_sa_consommation_et_declenche_detection(self):
        with patch('tracker.views.DetecteurAnomalieElectricite') as mock_detect:
            self.login_employe(self.employe_a)
            res = self.client.post(
                reverse('consommations-electricite-list'),
                {
                    'site': str(self.site_a.id),
                    'mois_annee': timezone.now().date().replace(day=1).isoformat(),
                    'consommation_kwh': 320,
                    'montant_facture_fcfa': 58000,
                },
                format='json',
            )
        self.assertEqual(res.status_code, 201, res.content)
        conso = ConsommationElectrique.objects.get(id=res.data['id'])
        self.assertEqual(conso.employe_id_declarant, self.employe_a)
        mock_detect.return_value.detecter.assert_called_once()

    def test_aucune_valeur_fournie_400(self):
        self.login_employe(self.employe_a)
        res = self.client.post(
            reverse('consommations-electricite-list'),
            {
                'site': str(self.site_a.id),
                'mois_annee': timezone.now().date().replace(day=1).isoformat(),
            },
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_mois_futur_400(self):
        self.login_employe(self.employe_a)
        futur = (timezone.now() + timedelta(days=45)).date().replace(day=1)
        res = self.client.post(
            reverse('consommations-electricite-list'),
            {'site': str(self.site_a.id), 'mois_annee': futur.isoformat(),
             'consommation_kwh': 100},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_admin_voit_toutes_les_consommations(self):
        mois = timezone.now().date().replace(day=1)
        ConsommationElectrique.objects.create(
            site=self.site_a, mois_annee=mois, consommation_kwh=300,
            employe_id_declarant=self.employe_a,
        )
        ConsommationElectrique.objects.create(
            site=self.site_b, mois_annee=mois, consommation_kwh=120,
            employe_id_declarant=self.employe_b,
        )
        self.login_admin()
        res = self.client.get(reverse('consommations-electricite-list'))
        self.assertEqual(len(res.data['results']), 2)


@override_settings(**CELERY_EAGER)
class AlertesResolveApiTests(BaseAuthTestCase):

    def _creer_alerte(self):
        return Alerte.objects.create(
            site=self.site_a,
            type_alerte=Alerte.TypeAlerte.CARBURANT,
            severite=Alerte.Severite.HAUT,
            motif_technique='Ratio hors norme',
            valeur_detectee=38.5,
            valeur_seuil=20.0,
        )

    def test_resolve_par_admin(self):
        alerte = self._creer_alerte()
        self.login_admin()
        res = self.client.patch(
            reverse('alertes-resolve', args=[alerte.id]),
            {'resolution_type': 'equipement_repare',
             'resolution_note': 'Injecteur nettoyé'},
            format='json',
        )
        self.assertEqual(res.status_code, 200, res.content)
        alerte.refresh_from_db()
        self.assertEqual(alerte.statut, 'resolu')
        self.assertEqual(alerte.resolu_par, self.admin)
        self.assertIsNotNone(alerte.date_resolution)

    def test_resolve_type_invalide_400(self):
        alerte = self._creer_alerte()
        self.login_admin()
        res = self.client.patch(
            reverse('alertes-resolve', args=[alerte.id]),
            {'resolution_type': 'je_sais_pas'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_resolve_sur_alerte_non_active_400(self):
        alerte = self._creer_alerte()
        alerte.statut = 'resolu'
        alerte.save()
        self.login_admin()
        res = self.client.patch(
            reverse('alertes-resolve', args=[alerte.id]),
            {'resolution_type': 'a_investiguer'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_employe_acces_liste_alertes_interdit(self):
        self.auth_as(self.employe_a)
        res = self.client.get(reverse('alertes-list'))
        self.assertEqual(res.status_code, 403)


@override_settings(**CELERY_EAGER)
class SeuilsAlerteApiTests(BaseAuthTestCase):

    SEUILS_URL = '/api/seuils-alerte/'

    def test_get_defauts_singleton(self):
        self.login_admin()
        res = self.client.get(self.SEUILS_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['seuil_carburant_pct'], 20.0)
        self.assertEqual(res.data['seuil_electricite_pct'], 30.0)

    def test_put_mise_a_jour_singleton(self):
        self.login_admin()
        res = self.client.put(self.SEUILS_URL, {
            'seuil_carburant_pct': 35,
            'seuil_electricite_pct': 25,
            'fenetre_historique_carburant_mois': 3,
            'fenetre_historique_electricite_mois': 2,
        }, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        seuils = SeuillAlerte.get_solo()
        self.assertEqual(seuils.seuil_carburant_pct, 35.0)
        self.assertEqual(SeuillAlerte.objects.count(), 1)
        self.assertEqual(seuils.modifie_par_id, self.admin.id)

    def test_put_seuil_hors_limite_400(self):
        self.login_admin()
        res = self.client.put(self.SEUILS_URL, {
            'seuil_carburant_pct': 150,
            'seuil_electricite_pct': 30,
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_employe_403(self):
        self.auth_as(self.employe_a)
        res = self.client.get(self.SEUILS_URL)
        self.assertEqual(res.status_code, 403)


@override_settings(**CELERY_EAGER)
class DashboardHistoriqueApiTests(BaseAuthTestCase):

    DASH_URL = '/api/dashboard/'
    HISTO_URL = '/api/historique-mensuel/'

    def _alimenter_le_mois(self):
        maintenant = timezone.now()
        self.make_plein(self.site_a, self.employe_a,
                        jours_arriere=0, litres=40)
        Coupure.objects.create(
            site=self.site_a,
            date_debut=maintenant - timedelta(hours=2),
            date_fin=maintenant,
            duree_heures=2.0,
            employe_id_declaration=self.employe_a,
            statut='fermee',
        )
        ConsommationElectrique.objects.create(
            site=self.site_a,
            mois_annee=maintenant.date().replace(day=1),
            consommation_kwh=300,
            employe_id_declarant=self.employe_a,
        )
        CalculRatioCarburant.objects.create(
            site=self.site_a,
            mois_annee=maintenant.date().replace(day=1),
            ratio_litres_par_heure=4.0, total_litres_periode=40,
            total_heures_groupe=10, nombre_pleins_periode=1,
            nombre_sessions_groupe=2, donnees_suffisantes=True,
        )

    def test_anonyme_401_et_employe_403(self):
        self.assertEqual(
            self.client.get(self.DASH_URL).status_code, 401)
        self.auth_as(self.employe_a)
        self.assertEqual(
            self.client.get(self.DASH_URL).status_code, 403)

    def test_admin_dashboard_structure_vide(self):
        self.login_admin()
        res = self.client.get(self.DASH_URL)
        self.assertEqual(res.status_code, 200)
        self.assertIn('sites_actifs', res.data)
        self.assertIn('statistiques_mensuelles', res.data)
        self.assertEqual(res.data['sites_actifs'], 1)  # seul le site A est actif

    def test_dashboard_reflete_les_donnees_du_mois(self):
        self._alimenter_le_mois()
        Coupure.objects.create(  # une coupure encore ouverte
            site=self.site_b, date_debut=timezone.now(),
            employe_id_declaration=self.employe_b, statut='ouverte',
        )
        Alerte.objects.create(
            site=self.site_a, type_alerte=Alerte.TypeAlerte.ELECTRICITE,
            motif_technique='test', valeur_detectee=99, valeur_seuil=30,
        )
        self.login_admin()
        data = self.client.get(self.DASH_URL).data
        stats = data['statistiques_mensuelles']
        self.assertEqual(stats['total_litres_carburant'], 40)
        self.assertEqual(stats['total_coupures_mois'], 2)  # fermée + ouverte
        self.assertAlmostEqual(
            float(stats['duree_totale_coupures_heures']), 2.0)
        self.assertEqual(float(stats['consommation_electricite_kwh']), 300)
        self.assertAlmostEqual(float(stats['ratio_moyen_carburant']), 4.0)
        self.assertEqual(len(data['coupures_actives']), 1)
        self.assertEqual(data['coupures_actives'][0]['nom_site'],
                         'Restaurant Yaoundé')
        self.assertEqual(len(data['alertes_non_resolues']), 1)

    def test_historique_sans_site_400(self):
        self.login_admin()
        res = self.client.get(self.HISTO_URL)
        self.assertEqual(res.status_code, 400)

    def test_historique_avec_site_et_mois(self):
        self._alimenter_le_mois()
        self.login_admin()
        res = self.client.get(self.HISTO_URL, {
            'site_id': str(self.site_a.id),
            'mois': timezone.now().strftime('%Y-%m'),
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('ratios_carburant', res.data)
        self.assertIn('consommations_electriques', res.data)
        self.assertEqual(len(res.data['ratios_carburant']), 1)
        self.assertEqual(res.data['statistiques_coupures']['total'], 1)

    def test_historique_mois_invalide_est_tolerant(self):
        self.login_admin()
        res = self.client.get(self.HISTO_URL, {
            'site_id': str(self.site_a.id), 'mois': 'pas-un-mois',
        })
        self.assertEqual(res.status_code, 200)

    def test_scores_et_audit_reserves_admin(self):
        self.auth_as(self.employe_a)
        self.assertEqual(
            self.client.get(reverse('scores-fiabilite-list')).status_code, 403)
        self.assertEqual(
            self.client.get(reverse('audit-list')).status_code, 403)
        self.login_admin()
        audit_filtré = self.client.get(
            reverse('audit-list'), {'table_cible': 'rien'})
        self.assertEqual(audit_filtré.data['results'], [])
        scores = self.client.get(reverse('scores-fiabilite-list'))
        self.assertEqual(scores.data['results'], [])


TELEGRAM_OFF = {
    **CELERY_EAGER,
    'TELEGRAM_BOT_TOKEN': '',      # force la coupure propre (pas de réseau)
    'TELEGRAM_ADMIN_CHAT_ID': '',
}


@override_settings(**TELEGRAM_OFF)
class CalculRatioServiceTests(BaseAuthTestCase):
    """Logique métier : CalculateurRatioCarburant."""

    def setUp(self):
        super().setUp()
        self.service = CalculateurRatioCarburant()
        self.mois = timezone.now().date().replace(day=1)

    def _seed_mois_complet(self, site=None, employe=None, litres=[40, 30]):
        site = site or self.site_a
        employe = employe or self.employe_a
        from datetime import datetime as dt
        for jour in (3, 5):
            self.make_session_fermee(
                site, employe,
                timezone.make_aware(dt.combine(
                    self.mois.replace(day=jour), dt.min.time())) + timedelta(hours=8),
                heures=5,
            )
        for i, litres_i in enumerate(litres):
            PleineCarburant.objects.create(
                site=site,
                quantite_litres=litres_i,
                prix_unitaire_fcfa=800,
                date_plein=(self.mois + timedelta(days=2 + i)),
                employe_id_declaration=employe,
            )

    def test_aucune_donnee_retourne_none(self):
        self.assertIsNone(
            self.service.calculer(self.site_a.id, self.mois))

    def test_une_session_seule_est_insuffisant(self):
        from datetime import datetime as dt
        self.make_session_fermee(
            self.site_a, self.employe_a,
            timezone.make_aware(dt.combine(self.mois, dt.min.time())),
            heures=5,
        )
        self.assertIsNone(
            self.service.calculer(self.site_a.id, self.mois))

    def test_deux_sessions_sans_plein_insuffisant(self):
        from datetime import datetime as dt
        for jour in (3, 5):
            self.make_session_fermee(
                self.site_a, self.employe_a,
                timezone.make_aware(dt.combine(
                    self.mois.replace(day=jour), dt.min.time())),
                heures=5,
            )
        self.assertIsNone(
            self.service.calculer(self.site_a.id, self.mois))

    def test_calcul_complet_idempotent(self):
        self._seed_mois_complet()
        ratio = self.service.calculer(self.site_a.id, self.mois)
        self.assertIsNotNone(ratio)
        # 70 L / 10 h de groupe = 7.0 L/h
        self.assertAlmostEqual(ratio.ratio_litres_par_heure, 7.0, delta=0.001)
        self.assertEqual(ratio.total_litres_periode, 70)
        self.assertAlmostEqual(ratio.total_heures_groupe, 10.0)
        self.assertTrue(ratio.donnees_suffisantes)

        ratio2 = self.service.calculer(self.site_a.id, self.mois)
        self.assertEqual(ratio2.pk, ratio.pk)  # update_or_create → pas de doublon
        self.assertEqual(CalculRatioCarburant.objects.count(), 1)

    def test_recalcul_tous_sites_ignore_les_inactifs(self):
        self._seed_mois_complet(site=self.site_b, employe=self.employe_b)
        resultats = self.service.recalculer_tous_sites(mois=self.mois)
        self.assertEqual(resultats, [])
        self.assertFalse(CalculRatioCarburant.objects.filter(
            site=self.site_b).exists())


@override_settings(**TELEGRAM_OFF)
class DetecteurCarburantServiceTests(BaseAuthTestCase):
    """Logique métier : DetecteurAnomalieCarburant."""

    def setUp(self):
        super().setUp()
        self.detecteur = DetecteurAnomalieCarburant()
        self.mois = timezone.now().date().replace(day=1)
        SeuillAlerte.get_solo()  # seuils par défaut : ±20 %

    def _ratio(self, site, mois, valeur):
        return CalculRatioCarburant.objects.create(
            site=site,
            mois_annee=mois,
            ratio_litres_par_heure=valeur,
            total_litres_periode=valeur * 10,
            total_heures_groupe=10,
            nombre_pleins_periode=2,
            nombre_sessions_groupe=2,
            donnees_suffisantes=True,
        )

    @staticmethod
    def _mois_recule(mois, k):
        return (mois - timedelta(days=32 * k)).replace(day=1)

    def test_anomalie_carburant_detectee_avec_severite_haut(self):
        self._ratio(self.site_a, self._mois_recule(self.mois, 2), 4.0)
        self._ratio(self.site_a, self._mois_recule(self.mois, 1), 4.0)
        self._ratio(self.site_a, self.mois, 6.0)  # écart = 50 % vs moyenne 4

        alertes = self.detecteur.detecter(
            site_id=self.site_a.id, mois=self.mois)
        self.assertEqual(len(alertes), 1)
        alerte = alertes[0]
        self.assertEqual(alerte.type_alerte, 'carburant_anomalie')
        self.assertEqual(alerte.severite, 'haut')      # 50 % > 40 % (seuil x2)
        self.assertAlmostEqual(alerte.valeur_detectee, 50.0, delta=0.01)
        self.assertEqual(alerte.valeur_seuil, 20.0)
        # Telegram non configuré → la tâche eager s'exécute sans réseau
        self.assertFalse(alerte.telegram_notification_sent)

    def test_ecart_sous_le_seuil_pas_dalerte(self):
        self._ratio(self.site_a, self._mois_recule(self.mois, 2), 4.0)
        self._ratio(self.site_a, self._mois_recule(self.mois, 1), 4.0)
        self._ratio(self.site_a, self.mois, 4.5)  # écart ≈ 12.5 % < 20 %
        self.assertEqual(
            len(self.detecteur.detecter(self.site_a.id, self.mois)), 0)

    def test_ratio_courant_insuffisant_pas_dalerte(self):
        ratio_partiel = self._ratio(
            self.site_a, self.mois, 6.0)
        ratio_partiel.donnees_suffisantes = False
        ratio_partiel.save()
        self.assertEqual(
            len(self.detecteur.detecter(self.site_a.id, self.mois)), 0)

    def test_sans_historique_pas_dalerte(self):
        self._ratio(self.site_a, self.mois, 6.0)
        self.assertEqual(
            len(self.detecteur.detecter(self.site_a.id, self.mois)), 0)

    def test_grille_de_severite(self):
        calc = DetecteurAnomalieCarburant._calculer_severite
        self.assertEqual(calc(50, 20), 'haut')
        self.assertEqual(calc(35, 20), 'moyen')
        self.assertEqual(calc(21, 20), 'bas')


@override_settings(**TELEGRAM_OFF)
class DetecteurElectriciteServiceTests(BaseAuthTestCase):
    """Logique métier : DetecteurAnomalieElectricite."""

    def setUp(self):
        super().setUp()
        self.detecteur = DetecteurAnomalieElectricite()
        self.mois = timezone.now().date().replace(day=1)
        SeuillAlerte.get_solo()  # ±30 %

    def _conso(self, mois, kwh):
        return ConsommationElectrique.objects.create(
            site=self.site_a, mois_annee=mois,
            consommation_kwh=kwh,
            employe_id_declarant=self.employe_a,
        )

    @staticmethod
    def _mois_recule(mois, k):
        return (mois - timedelta(days=32 * k)).replace(day=1)

    def test_historique_insuffisant_pas_dalerte(self):
        self._conso(self._mois_recule(self.mois, 1), 100)
        self._conso(self.mois, 300)  # 1 seul mois d'historique < 2
        self.assertEqual(
            len(self.detecteur.detecter(self.site_a.id, self.mois)), 0)

    def test_anomalie_electricite_detectee(self):
        self._conso(self._mois_recule(self.mois, 1), 100)
        self._conso(self._mois_recule(self.mois, 2), 100)
        conso = self._conso(self.mois, 300)  # écart = 200 %

        alertes = self.detecteur.detecter(
            site_id=self.site_a.id, mois=self.mois)
        self.assertEqual(len(alertes), 1)
        alerte = alertes[0]
        self.assertEqual(alerte.type_alerte, 'electricite_anomalie')
        self.assertEqual(alerte.severite, 'haut')
        self.assertAlmostEqual(alerte.valeur_detectee, 200.0, delta=0.01)
        self.assertEqual(alerte.employe_id_lien_id, self.employe_a.id)
        self.assertIn(str(conso.consommation_kwh), alerte.motif_technique)

    def test_consommation_normale_pas_dalerte(self):
        self._conso(self._mois_recule(self.mois, 1), 100)
        self._conso(self._mois_recule(self.mois, 2), 100)
        self._conso(self.mois, 115)  # écart 15 % < 30 %
        self.assertEqual(
            len(self.detecteur.detecter(self.site_a.id, self.mois)), 0)


@override_settings(**TELEGRAM_OFF)
class ScoreFiabiliteServiceTests(BaseAuthTestCase):
    """Logique métier : CalculateurScoreFiabilite."""

    def setUp(self):
        super().setUp()
        self.service = CalculateurScoreFiabilite()
        self.mois = timezone.now().date().replace(day=1)

    def _seed_operations(self, nombre=5):
        for i in range(nombre):
            self.make_plein(self.site_a, self.employe_a, jours_arriere=0,
                            litres=10)

    def _alerte(self, type_alerte):
        return Alerte.objects.create(
            site=self.site_a, type_alerte=type_alerte,
            motif_technique='x', valeur_detectee=99, valeur_seuil=20,
            employe_id_lien=self.employe_a,
        )

    def _score_de(self, employe, scores):
        return {str(s.employe_id): s for s in scores}[str(employe.id)]

    def test_moins_de_5_operations_score_insuffisant_100(self):
        scores = self.service.calculer_pour_mois(self.mois)
        self.assertEqual(len(scores), 2)  # les deux employés actifs
        score_a = self._score_de(self.employe_a, scores)
        self.assertEqual(score_a.score_final, 100)
        self.assertEqual(score_a.nombre_operations_mois, 0)
        self.assertTrue(score_a.detail_penalites.get('insuffisant'))

    def test_penalites_combines_corrigees(self):
        self._seed_operations(5)                    # 5 pleins enregistrés
        self._alerte('carburant_anomalie')          # −5
        self._alerte('electricite_anomalie')        # −3
        self.make_coupure_fermee(                   # coupure longue : −10
            self.site_a, self.employe_a,
            debut=self.mois.replace(day=2),
            heures=50,
        )
        scores = self.service.calculer_pour_mois(self.mois)
        score_a = self._score_de(self.employe_a, scores)
        self.assertEqual(score_a.total_penalites, 18)
        self.assertEqual(score_a.score_final, 82)
        self.assertEqual(score_a.detail_penalites['anomalie_carburant'], 1)
        self.assertEqual(score_a.detail_penalites['anomalie_electricite'], 1)
        self.assertEqual(score_a.detail_penalites['coupure_non_fermee'], 1)

    def test_le_score_ne_devient_jamais_negatif(self):
        self._seed_operations(5)
        for _ in range(30):                         # 30 × −5 = −150
            self._alerte('carburant_anomalie')
        scores = self.service.calculer_pour_mois(
            self.mois, employe_id=self.employe_a.id)
        self.assertEqual(scores[0].score_final, 0)


@override_settings(**TELEGRAM_OFF)
class TachesCeleryTests(BaseAuthTestCase):
    """Les tâches partagées s'exécutent de façon synchrone (mode eager)."""

    def setUp(self):
        super().setUp()
        self.mois = timezone.now().date().replace(day=1)

    def _seed_donnees_du_mois(self):
        from datetime import datetime as dt
        base = timezone.make_aware(dt.combine(self.mois, dt.min.time()))
        for jour in (3, 5):
            SessionGroupe.objects.create(
                site=self.site_a,
                timestamp_debut=base.replace(day=jour) + timedelta(hours=8),
                timestamp_fin=base.replace(day=jour) + timedelta(hours=13),
                duree_heures=5,
                employe_id_declaration=self.employe_a,
                statut='fermee',
            )
        PleineCarburant.objects.create(
            site=self.site_a, quantite_litres=70, prix_unitaire_fcfa=800,
            date_plein=self.mois + timedelta(days=6),
            employe_id_declaration=self.employe_a,
        )

    def test_tache_calcul_ratio_carburant(self):
        from .tasks.carburant import calculer_ratio_carburant
        self._seed_donnees_du_mois()
        resultat = calculer_ratio_carburant(
            str(self.site_a.id), self.mois.isoformat())
        self.assertIsNotNone(resultat)
        self.assertEqual(CalculRatioCarburant.objects.count(), 1)

    def test_tache_recalculer_tous_ratios_accepte_une_chaine(self):
        from .tasks.carburant import recalculer_tous_ratios
        self._seed_donnees_du_mois()
        resultats = recalculer_tous_ratios(self.mois.isoformat())
        self.assertEqual(len(resultats), 1)
        self.assertAlmostEqual(resultats[0].ratio_litres_par_heure, 7.0,
                               delta=0.001)

    def test_tache_detection_electricite(self):
        from .tasks.alertes import detecter_anomalies_electricite
        mois_prec = (self.mois - timedelta(days=32)).replace(day=1)
        mois_prec2 = (self.mois - timedelta(days=64)).replace(day=1)
        for m in (mois_prec, mois_prec2):
            ConsommationElectrique.objects.create(
                site=self.site_a, mois_annee=m, consommation_kwh=100,
                employe_id_declarant=self.employe_a,
            )
        ConsommationElectrique.objects.create(
            site=self.site_a, mois_annee=self.mois, consommation_kwh=400,
            employe_id_declarant=self.employe_a,
        )
        alertes = detecter_anomalies_electricite(
            site_id=str(self.site_a.id), mois=self.mois.isoformat())
        self.assertEqual(len(alertes), 1)


class TelegramTaskTests(BaseAuthTestCase):
    """Tâche de notification Telegram (réseau jamais touché ici)."""

    def _alerte(self):
        return Alerte.objects.create(
            site=self.site_a,
            type_alerte=Alerte.TypeAlerte.CARBURANT,
            severite=Alerte.Severite.HAUT,
            motif_technique='Ratio hors norme',
            valeur_detectee=38.5,
            valeur_seuil=20.0,
        )

    def test_alerte_introuvable_retourne_false(self):
        from .tasks.notifications import envoyer_alerte_telegram
        import uuid as uuid_mod
        self.assertIs(envoyer_alerte_telegram(uuid_mod.uuid4()), False)

    @override_settings(**TELEGRAM_OFF)
    def test_non_configure_ne_marque_pas_notifiee(self):
        from .tasks.notifications import envoyer_alerte_telegram
        alerte = self._alerte()
        self.assertIs(envoyer_alerte_telegram(alerte.id), False)
        alerte.refresh_from_db()
        self.assertFalse(alerte.telegram_notification_sent)

    def test_deja_notifiee_retourne_true_sans_requete(self):
        from unittest.mock import Mock
        from .tasks.notifications import envoyer_alerte_telegram
        alerte = self._alerte()
        alerte.telegram_notification_sent = True
        alerte.save()
        with patch('tracker.tasks.notifications.requests.post') as mock_post:
            mock_post.return_value = Mock(status_code=200)
            resultat = envoyer_alerte_telegram(alerte.id)
        self.assertIs(resultat, True)
        mock_post.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN='TEST-TOKEN',
                       TELEGRAM_ADMIN_CHAT_ID='42')
    def test_envoi_reussi_marque_l_alerte(self):
        from unittest.mock import Mock
        from .tasks.notifications import envoyer_alerte_telegram
        alerte = self._alerte()
        with patch('tracker.tasks.notifications.requests.post') as mock_post:
            mock_post.return_value = Mock(status_code=200)
            resultat = envoyer_alerte_telegram(alerte.id)
        self.assertIs(resultat, True)
        self.assertEqual(mock_post.call_count, 1)
        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(payload['chat_id'], '42')
        self.assertEqual(payload['parse_mode'], 'HTML')
        self.assertIn('ANOMALIE CARBURANT', payload['text'])
        alerte.refresh_from_db()
        self.assertTrue(alerte.telegram_notification_sent)
        self.assertIsNotNone(alerte.telegram_timestamp)


class AuditMiddlewareApiTests(BaseAuthTestCase):
    """Journalisation automatique des mutations."""

    SEUILS_URL = '/api/seuils-alerte/'

    def test_mutation_authentifiee_est_journalisee(self):
        self.login_admin()
        res = self.client.put(self.SEUILS_URL, {
            'seuil_carburant_pct': 40, 'seuil_electricite_pct': 25,
        }, format='json')
        self.assertEqual(res.status_code, 200)
        entree = AuditTrail.objects.filter(action__startswith='PUT').latest('timestamp')
        self.assertIn('/api/seuils-alerte', entree.action)
        self.assertEqual(entree.table_cible, 'request')
        self.assertEqual(entree.employe, self.admin)
        self.assertTrue(entree.adresse_ip)

    def test_login_public_journalise_sans_employe(self):
        self.client.post(reverse('admin-login'), {'email': 'x', 'password': 'y'},
                         format='json')
        entree = AuditTrail.objects.latest('timestamp')
        self.assertIn('/api/auth/login', entree.action)
        self.assertIsNone(entree.employe)

    def test_les_appels_vers_le_audit_sont_exclus(self):
        self.login_admin()
        self.client.post('/api/audit/', {}, format='json')
        self.assertFalse(
            AuditTrail.objects.filter(action__icontains='/api/audit').exists())


# FIN DE LA SUITE DE TESTS PowerTracker ✔
