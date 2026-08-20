// ─────────────── MODÈLES API ───────────────

export interface Site {
  id: string;
  nom: string;
  adresse: string;
  latitude: number | null;
  longitude: number | null;
  type_carburant: 'essence' | 'gazoil';
  type_groupe: string | null;
  puissance_kva: number | null;
  actif: boolean;
  date_creation: string;
  date_modification: string;
}

export interface Employe {
  id: string;
  site: string | null;
  site_nom: string | null;
  prenom: string;
  nom: string;
  email: string | null;
  role: 'employe' | 'administratrice';
  telephone: string | null;
  telegram_user_id: number | null;
  date_embauche: string | null;
  actif: boolean;
  date_creation: string;
}

export interface Coupure {
  id: string;
  site: string;
  site_nom: string;
  date_debut: string;
  date_fin: string | null;
  duree_heures: number | null;
  employe_id_declaration: string;
  cause_descriptif: string | null;
  statut: 'ouverte' | 'fermee';
  date_creation: string;
}

export interface SessionGroupe {
  id: string;
  site: string;
  site_nom: string;
  timestamp_debut: string;
  timestamp_fin: string | null;
  duree_heures: number | null;
  employe_id_declaration: string;
  statut: 'en_cours' | 'fermee';
  date_creation: string;
}

export interface PleineCarburant {
  id: string;
  site: string;
  site_nom: string;
  quantite_litres: number;
  prix_unitaire_fcfa: number;
  montant_total_fcfa: number;
  date_plein: string;
  employe_id_declaration: string;
  date_creation: string;
}

export interface ConsommationElectrique {
  id: string;
  site: string;
  site_nom: string;
  mois_annee: string;
  consommation_kwh: number | null;
  montant_facture_fcfa: number | null;
  employe_id_declarant: string;
  date_creation: string;
}

export interface CalculRatioCarburant {
  id: string;
  site: string;
  site_nom: string;
  mois_annee: string;
  ratio_litres_par_heure: number;
  total_litres_periode: number;
  total_heures_groupe: number;
  nombre_pleins_periode: number;
  nombre_sessions_groupe: number;
  donnees_suffisantes: boolean;
  notes_calcul: string | null;
  timestamp_calcul: string;
}

export interface Alerte {
  id: string;
  site: string;
  site_nom: string;
  type_alerte: 'carburant_anomalie' | 'electricite_anomalie';
  severite: 'bas' | 'moyen' | 'haut';
  motif_technique: string;
  valeur_detectee: number;
  valeur_seuil: number;
  employe_id_lien: string | null;
  employe_nom: string | null;
  statut: 'actif' | 'resolu' | 'ignoree';
  resolution_type: string | null;
  resolution_note: string | null;
  resolu_par: string | null;
  date_resolution: string | null;
  timestamp_creation: string;
  telegram_notification_sent: boolean;
  telegram_timestamp: string | null;
}

export interface SeuilsAlerte {
  seuil_carburant_pct: number;
  seuil_electricite_pct: number;
  fenetre_historique_carburant_mois: number;
  fenetre_historique_electricite_mois: number;
  date_modification: string;
}

export interface ScoreFiabilite {
  id: string;
  employe: string;
  employe_nom: string;
  employe_prenom: string;
  mois_annee: string;
  score_base: number;
  total_penalites: number;
  score_final: number;
  detail_penalites: Record<string, number | boolean> | null;
  nombre_operations_mois: number;
  date_calcul: string;
}

export interface DashboardData {
  sites_actifs: number;
  coupures_actives: {
    site_id: string;
    nom_site: string;
    date_debut: string;
    duree_actuelle_heures: number;
    employe: string;
  }[];
  groupes_actifs: {
    site_id: string;
    nom_site: string;
    timestamp_debut: string;
    duree_actuelle_heures: number;
  }[];
  alertes_non_resolues: {
    alerte_id: string;
    type: string;
    site: string;
    timestamp: string;
    severite: string;
    motif_technique: string;
  }[];
  scores_fiabilite_employes: {
    employe_id: string;
    nom: string;
    prenom: string;
    score_mois_courant: number;
    score_mois_precedent: number | null;
    nombre_operations_mois: number;
  }[];
  statistiques_mensuelles: {
    total_coupures_mois: number;
    duree_totale_coupures_heures: number;
    total_litres_carburant: number;
    ratio_moyen_carburant: number;
    consommation_electricite_kwh: number;
  };
}

export interface AuthUser {
  id: string;
  email?: string;
  prenom: string;
  nom: string;
  role: 'employe' | 'administratrice';
  site_id?: string;
}