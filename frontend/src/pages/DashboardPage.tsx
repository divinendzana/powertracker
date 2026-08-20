import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { dashboardService } from '../services/data.service';
import { DashboardData } from '../types';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      const result = await dashboardService.get();
      setData(result);
    } catch {
      // géré par intercepteur
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login-admin');
  };

  if (loading || !data) {
    return <div style={styles.loading}>Chargement du tableau de bord...</div>;
  }

  const stats = data.statistiques_mensuelles;

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.brand}>CAMTEL PowerTracker</h1>
          <span>Bienvenue, {user?.prenom} {user?.nom}</span>
        </div>
        <div style={styles.headerActions}>
          <button onClick={() => navigate('/historique')} style={styles.navBtn}>Historique</button>
          <button onClick={() => navigate('/parametres')} style={styles.navBtn}>Paramètres</button>
          <button onClick={handleLogout} style={styles.logoutBtn}>Déconnexion</button>
        </div>
      </header>

      <main style={styles.main}>
        {/* Statistiques rapides */}
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{data.coupures_actives.length}</div>
            <div style={styles.statLabel}>Coupures actives</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{data.groupes_actifs.length}</div>
            <div style={styles.statLabel}>Groupes actifs</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{data.alertes_non_resolues.length}</div>
            <div style={styles.statLabel}>Alertes actives</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{data.sites_actifs}</div>
            <div style={styles.statLabel}>Sites actifs</div>
          </div>
        </div>

        {/* Alertes actives */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>🔴 Alertes Actives</h2>
          {data.alertes_non_resolues.length === 0 ? (
            <p style={styles.emptyState}>Aucune alerte active ✅</p>
          ) : (
            <div style={styles.alertList}>
              {data.alertes_non_resolues.map((alerte) => (
                <div key={alerte.alerte_id} style={styles.alertItem}>
                  <span style={styles.alertIcon}>
                    {alerte.severite === 'haut' ? '🚨' : '⚠️'}
                  </span>
                  <div style={styles.alertContent}>
                    <div style={styles.alertTitle}>
                      {alerte.type === 'carburant_anomalie' ? 'ANOMALIE CARBURANT' : 'ANOMALIE ÉLECTRICITÉ'}
                    </div>
                    <div><strong>Site:</strong> {alerte.site}</div>
                    <div style={styles.alertDetail}>{alerte.motif_technique}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* États des sites */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>🏢 États des Sites</h2>
          <div style={styles.statsGrid}>
            {data.coupures_actives.map((c) => (
              <div key={c.site_id} style={{ ...styles.siteCard, borderLeft: '5px solid #f44336' }}>
                <div style={styles.siteName}>⚡ {c.nom_site}</div>
                <div style={styles.siteDetail}>Coupure depuis {c.duree_actuelle_heures}h</div>
                <div style={styles.siteDetail}>Déclaré par: {c.employe}</div>
              </div>
            ))}
            {data.groupes_actifs.map((g) => (
              <div key={g.site_id} style={{ ...styles.siteCard, borderLeft: '5px solid #ff9800' }}>
                <div style={styles.siteName}>🔧 {g.nom_site}</div>
                <div style={styles.siteDetail}>Groupe actif {g.duree_actuelle_heures}h</div>
              </div>
            ))}
          </div>
        </section>

        {/* Scores fiabilité */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>📊 Scores Fiabilité Équipes</h2>
          <div style={styles.scoreList}>
            {data.scores_fiabilite_employes.length === 0 ? (
              <p style={styles.emptyState}>Scores pas encore calculés pour ce mois</p>
            ) : (
              data.scores_fiabilite_employes.map((score) => {
                const prev = score.score_mois_precedent;
                const evolution = prev === null ? '' : score.score_mois_courant > prev ? '⬆️' : score.score_mois_courant < prev ? '⬇️' : '➡️';
                return (
                  <div key={score.employe_id} style={styles.scoreItem}>
                    <span style={styles.scoreName}>{score.prenom} {score.nom} {evolution}</span>
                    <span style={{ color: score.score_mois_courant >= 90 ? '#2e7d32' : score.score_mois_courant >= 75 ? '#ff9800' : '#c62828' }}>
                      {score.score_mois_courant}/100
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </section>

        {/* Statistiques mensuelles */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>📈 Statistiques Mensuelles</h2>
          <div style={styles.monthlyStats}>
            <div style={styles.monthlyStatItem}>Coupures: {stats.total_coupures_mois}</div>
            <div style={styles.monthlyStatItem}>Durée coupures: {stats.duree_totale_coupures_heures}h</div>
            <div style={styles.monthlyStatItem}>Carburant: {stats.total_litres_carburant} L</div>
            <div style={styles.monthlyStatItem}>Ratio moyen: {stats.ratio_moyen_carburant.toFixed(2)} L/h</div>
            <div style={styles.monthlyStatItem}>Électricité: {stats.consommation_electricite_kwh} kWh</div>
          </div>
        </section>
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { minHeight: '100vh', background: '#f5f5f5' },
  loading: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', fontSize: '18px' },
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
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '16px',
    marginBottom: '24px',
  },
  statCard: {
    background: 'white',
    borderRadius: '10px',
    padding: '20px',
    textAlign: 'center',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  statValue: { fontSize: '32px', fontWeight: 'bold', color: '#1a237e' },
  statLabel: { fontSize: '14px', color: '#666', marginTop: '4px' },
  section: { background: 'white', borderRadius: '10px', padding: '20px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' },
  sectionTitle: { fontSize: '18px', margin: '0 0 16px', color: '#333' },
  emptyState: { color: '#888', textAlign: 'center', padding: '20px' },
  alertList: { display: 'flex', flexDirection: 'column', gap: '12px' },
  alertItem: {
    display: 'flex',
    gap: '12px',
    padding: '12px',
    borderRadius: '8px',
    background: '#fff3e0',
    borderLeft: '5px solid #ff9800',
  },
  alertIcon: { fontSize: '24px' },
  alertContent: { flex: 1 },
  alertTitle: { fontWeight: 'bold', color: '#e65100' },
  alertDetail: { fontSize: '13px', color: '#666', marginTop: '4px' },
  siteCard: {
    background: '#fafafa',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
  },
  siteName: { fontWeight: 'bold', marginBottom: '8px' },
  siteDetail: { fontSize: '13px', color: '#666', marginBottom: '4px' },
  scoreList: { display: 'flex', flexDirection: 'column', gap: '10px' },
  scoreItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px',
    borderRadius: '8px',
    background: '#f5f5f5',
  },
  scoreName: { fontWeight: '500' },
  monthlyStats: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' },
  monthlyStatItem: {
    background: '#e8eaf6',
    borderRadius: '8px',
    padding: '12px',
    textAlign: 'center',
    fontSize: '14px',
    color: '#1a237e',
  },
};