import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { sitesService, dashboardService } from '../services/data.service';
import { Site, CalculRatioCarburant, ConsommationElectrique } from '../types';

interface HistoriqueData {
  ratios_carburant: CalculRatioCarburant[];
  consommations_electriques: ConsommationElectrique[];
  statistiques_coupures: {
    total: number;
    duree_totale_heures: number;
    par_mois: { date_debut__month: number; total: number; duree: number | null }[];
  };
}

export default function HistoriquePage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [selectedSite, setSelectedSite] = useState('');
  const [data, setData] = useState<HistoriqueData | null>(null);
  const [loading, setLoading] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSites = async () => {
      try {
        const result = await sitesService.list({ actif: 'true' });
        setSites(result.results);
        if (result.results.length > 0) {
          setSelectedSite(result.results[0].id);
        }
      } catch {
        // Ignorer
      }
    };
    fetchSites();
  }, []);

  useEffect(() => {
    if (!selectedSite) return;
    const fetchHistorique = async () => {
      setLoading(true);
      try {
        const result = await dashboardService.historiqueMensuel(selectedSite);
        setData(result);
      } catch {
        // Ignorer
      } finally {
        setLoading(false);
      }
    };
    fetchHistorique();
  }, [selectedSite]);

  const handleLogout = () => {
    logout();
    navigate('/login-admin');
  };

  const formatMois = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' });
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.brand}>CAMTEL PowerTracker</h1>
          <span>📊 Historique mensuel</span>
        </div>
        <div style={styles.headerActions}>
          <button onClick={() => navigate('/dashboard')} style={styles.navBtn}>Dashboard</button>
          <button onClick={() => navigate('/parametres')} style={styles.navBtn}>Paramètres</button>
          <button onClick={handleLogout} style={styles.logoutBtn}>Déconnexion</button>
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.filters}>
          <label style={styles.label}>Site :</label>
          <select
            value={selectedSite}
            onChange={(e) => setSelectedSite(e.target.value)}
            style={styles.select}
          >
            {sites.map((site) => (
              <option key={site.id} value={site.id}>{site.nom}</option>
            ))}
          </select>
        </div>

        {loading && <div style={styles.loading}>Chargement...</div>}

        {data && !loading && (
          <>
            {/* Statistiques coupures */}
            <section style={styles.section}>
              <h2 style={styles.sectionTitle}>⚡ Statistiques Coupures</h2>
              <div style={styles.statsGrid}>
                <div style={styles.statCard}>
                  <div style={styles.statValue}>{data.statistiques_coupures.total}</div>
                  <div style={styles.statLabel}>Coupures</div>
                </div>
                <div style={styles.statCard}>
                  <div style={styles.statValue}>{data.statistiques_coupures.duree_totale_heures}h</div>
                  <div style={styles.statLabel}>Durée totale</div>
                </div>
              </div>
            </section>

            {/* Ratios carburant */}
            <section style={styles.section}>
              <h2 style={styles.sectionTitle}>⛽ Ratios Carburant (L/h)</h2>
              {data.ratios_carburant.length === 0 ? (
                <p style={styles.emptyState}>Aucun ratio calculé</p>
              ) : (
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Mois</th>
                      <th style={styles.th}>Ratio (L/h)</th>
                      <th style={styles.th}>Total litres</th>
                      <th style={styles.th}>Heures groupe</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.ratios_carburant.map((ratio) => (
                      <tr key={ratio.id}>
                        <td style={styles.td}>{formatMois(ratio.mois_annee)}</td>
                        <td style={styles.td}><strong>{ratio.ratio_litres_par_heure}</strong></td>
                        <td style={styles.td}>{ratio.total_litres_periode}</td>
                        <td style={styles.td}>{ratio.total_heures_groupe}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>

            {/* Consommation électrique */}
            <section style={styles.section}>
              <h2 style={styles.sectionTitle}>💡 Consommation Électrique</h2>
              {data.consommations_electriques.length === 0 ? (
                <p style={styles.emptyState}>Aucune consommation enregistrée</p>
              ) : (
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Mois</th>
                      <th style={styles.th}>kWh</th>
                      <th style={styles.th}>Montant facture</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.consommations_electriques.map((conso) => (
                      <tr key={conso.id}>
                        <td style={styles.td}>{formatMois(conso.mois_annee)}</td>
                        <td style={styles.td}>{conso.consommation_kwh ?? '-'}</td>
                        <td style={styles.td}>
                          {conso.montant_facture_fcfa
                            ? `${conso.montant_facture_fcfa.toLocaleString('fr-FR')} FCFA`
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { minHeight: '100vh', background: '#f5f5f5' },
  header: {
    background: '#1a237e',
    color: 'white',
    padding: '20px 30px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  brand: { margin: 0, fontSize: '22px' },
  headerActions: { display: 'flex', gap: '10px' },
  navBtn: {
    background: 'rgba(255,255,255,0.1)',
    color: 'white',
    border: '1px solid rgba(255,255,255,0.3)',
    padding: '8px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  logoutBtn: {
    background: '#c62828',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  main: { padding: '20px 30px', maxWidth: '1100px', margin: '0 auto' },
  filters: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px', background: 'white', padding: '16px', borderRadius: '10px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' },
  label: { fontSize: '14px', fontWeight: 'bold', color: '#333' },
  select: { flex: 1, padding: '10px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '14px' },
  loading: { textAlign: 'center', padding: '40px', fontSize: '16px', color: '#666' },
  section: { background: 'white', borderRadius: '10px', padding: '20px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' },
  sectionTitle: { fontSize: '18px', margin: '0 0 16px', color: '#333' },
  emptyState: { color: '#888', textAlign: 'center', padding: '20px' },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '16px',
  },
  statCard: {
    background: '#e8eaf6',
    borderRadius: '8px',
    padding: '16px',
    textAlign: 'center',
  },
  statValue: { fontSize: '24px', fontWeight: 'bold', color: '#1a237e' },
  statLabel: { fontSize: '13px', color: '#666', marginTop: '4px' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '14px' },
  th: { textAlign: 'left', padding: '12px', borderBottom: '2px solid #e0e0e0', color: '#333', background: '#fafafa' },
  td: { padding: '12px', borderBottom: '1px solid #eee' },
};