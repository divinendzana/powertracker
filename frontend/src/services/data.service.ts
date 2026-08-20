import api from './api';
import {
  Site,
  Employe,
  Coupure,
  SessionGroupe,
  PleineCarburant,
  ConsommationElectrique,
  CalculRatioCarburant,
  Alerte,
  SeuilsAlerte,
  ScoreFiabilite,
  DashboardData,
} from '../types';

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const sitesService = {
  async list(params?: Record<string, unknown>): Promise<PaginatedResponse<Site>> {
    const response = await api.get('/sites/', { params });
    return response.data;
  },
  async create(data: Partial<Site>): Promise<Site> {
    const response = await api.post('/sites/', data);
    return response.data;
  },
  async update(id: string, data: Partial<Site>): Promise<Site> {
    const response = await api.put(`/sites/${id}/`, data);
    return response.data;
  },
  async remove(id: string): Promise<void> {
    await api.delete(`/sites/${id}/`);
  },
};

export const employesService = {
  async list(params?: Record<string, unknown>): Promise<PaginatedResponse<Employe>> {
    const response = await api.get('/employes/', { params });
    return response.data;
  },
  async create(data: Partial<Employe> & { pin: string }): Promise<Employe> {
    const response = await api.post('/employes/', data);
    return response.data;
  },
  async update(id: string, data: Partial<Employe>): Promise<Employe> {
    const response = await api.put(`/employes/${id}/`, data);
    return response.data;
  },
  async remove(id: string): Promise<void> {
    await api.delete(`/employes/${id}/`);
  },
  async resetPin(id: string, pin: string): Promise<void> {
    await api.post(`/employes/${id}/reset_pin/`, { pin });
  },
};

export const coupuresService = {
  async list(params?: Record<string, unknown>): Promise<PaginatedResponse<Coupure>> {
    const response = await api.get('/coupures/', { params });
    return response.data;
  },
  async create(data: { site: string; date_debut: string; cause_descriptif?: string }): Promise<Coupure> {
    const response = await api.post('/coupures/', data);
    return response.data;
  },
  async close(id: string, date_fin: string): Promise<Coupure> {
    const response = await api.patch(`/coupures/${id}/close/`, { date_fin });
    return response.data;
  },
};

export const groupesService = {
  async list(params?: Record<string, unknown>): Promise<PaginatedResponse<SessionGroupe>> {
    const response = await api.get('/sessions-groupe/', { params });
    return response.data;
  },
  async start(data: { site: string; timestamp_debut: string }): Promise<SessionGroupe> {
    const response = await api.post('/sessions-groupe/', data);
    return response.data;
  },
  async stop(id: string, timestamp_fin: string): Promise<SessionGroupe> {
    const response = await api.patch(`/sessions-groupe/${id}/stop/`, { timestamp_fin });
    return response.data;
  },
};

export const carburantService = {
  async listPleins(params?: Record<string, unknown>): Promise<PaginatedResponse<PleineCarburant>> {
    const response = await api.get('/pleins-carburant/', { params });
    return response.data;
  },
  async createPlein(data: { site: string; quantite_litres: number; prix_unitaire_fcfa: number; date_plein: string }): Promise<PleineCarburant> {
    const response = await api.post('/pleins-carburant/', data);
    return response.data;
  },
  async listRatios(params?: Record<string, unknown>): Promise<PaginatedResponse<CalculRatioCarburant>> {
    const response = await api.get('/ratios-carburant/', { params });
    return response.data;
  },
};

export const electriciteService = {
  async list(params?: Record<string, unknown>): Promise<PaginatedResponse<ConsommationElectrique>> {
    const response = await api.get('/consommations-electricite/', { params });
    return response.data;
  },
  async create(data: { site: string; mois_annee: string; consommation_kwh?: number; montant_facture_fcfa?: number }): Promise<ConsommationElectrique> {
    const response = await api.post('/consommations-electricite/', data);
    return response.data;
  },
};

export const alertesService = {
  async list(params?: Record<string, unknown>): Promise<PaginatedResponse<Alerte>> {
    const response = await api.get('/alertes/', { params });
    return response.data;
  },
  async resolve(id: string, data: { resolution_type: string; resolution_note?: string }): Promise<Alerte> {
    const response = await api.patch(`/alertes/${id}/resolve/`, data);
    return response.data;
  },
};

export const seuilsService = {
  async get(): Promise<SeuilsAlerte> {
    const response = await api.get('/seuils-alerte/');
    return response.data;
  },
  async update(data: Partial<SeuilsAlerte>): Promise<SeuilsAlerte> {
    const response = await api.put('/seuils-alerte/', data);
    return response.data;
  },
};

export const scoresService = {
  async list(params?: Record<string, unknown>): Promise<PaginatedResponse<ScoreFiabilite>> {
    const response = await api.get('/scores-fiabilite/', { params });
    return response.data;
  },
};

export const dashboardService = {
  async get(): Promise<DashboardData> {
    const response = await api.get('/dashboard/');
    return response.data;
  },
  async historiqueMensuel(site_id: string, mois?: string) {
    const response = await api.get('/historique-mensuel/', { params: { site_id, mois } });
    return response.data;
  },
};