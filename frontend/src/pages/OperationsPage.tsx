import { useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  coupuresService,
  groupesService,
  carburantService,
  electriciteService,
} from '../services/data.service';
import { Coupure, SessionGroupe } from '../types';

type TabId = 'coupure' | 'groupe' | 'carburant' | 'electricite';

export default function OperationsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabId>('coupure');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  // Coupure
  const [coupureOuverte, setCoupureOuverte] = useState<Coupure | null>(null);
  const [dateDebut, setDateDebut] = useState('');
  const [cause, setCause] = useState('');

  // Groupe
  const [sessionOuverte, setSessionOuverte] = useState<SessionGroupe | null>(null);

  // Carburant
  const [litres, setLitres] = useState('');
  const [prix, setPrix] = useState('');
  const [datePlein, setDatePlein] = useState('');

  // Électricité
  const [mois, setMois] = useState('');
  const [kwh, setKwh] = useState('');
  const [montant, setMontant] = useState('');

  const siteId = user?.site_id || '';

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const fetchEtatCourant = async () => {
    try {
      const coupures = await coupuresService.list({ statut: 'ouverte', site_id: siteId });
      setCoupureOuverte(coupures.results[0] || null);

      const sessions = await groupesService.list({ statut: 'en_cours', site_id: siteId });
      setSessionOuverte(sessions.results[0] || null);
    } catch {
      // Ignorer erreurs réseau
    }
  };

  useEffect(() => {
    if (siteId) {
      fetchEtatCourant();
    }
  }, [siteId]);

  const nowIso = () => new Date().toISOString();

  // ─── Déclarer coupure ───
  const handleDeclarerCoupure = async (e: FormEvent) => {
    e.preventDefault();
    if (!dateDebut) return;
    setLoading(true);
    try {
      await coupuresService.create({
        site: siteId,
        date_debut: new Date(dateDebut).toISOString(),
        cause_descriptif: cause,
      });
      setDateDebut('');
      setCause('');
      showMessage('success', '✅ Coupure déclarée avec succès');
      fetchEtatCourant();
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur lors de la déclaration');
    } finally {
      setLoading(false);
    }
  };

  const handleFermerCoupure = async () => {
    if (!coupureOuverte) return;
    setLoading(true);
    try {
      await coupuresService.close(coupureOuverte.id, nowIso());
      setCoupureOuverte(null);
      showMessage('success', '✅ Coupure fermée');
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur');
    } finally {
      setLoading(false);
    }
  };

  // ─── Déclarer groupe ───
  const handleDemarrerGroupe = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await groupesService.start({
        site: siteId,
        timestamp_debut: new Date(dateDebut).toISOString(),
      });
      setDateDebut('');
      showMessage('success', '✅ Groupe démarré');
      fetchEtatCourant();
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur');
    } finally {
      setLoading(false);
    }
  };

  const handleArreterGroupe = async () => {
    if (!sessionOuverte) return;
    setLoading(true);
    try {
      await groupesService.stop(sessionOuverte.id, nowIso());
      setSessionOuverte(null);
      showMessage('success', '✅ Groupe arrêté');
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur');
    } finally {
      setLoading(false);
    }
  };

  // ─── Enregistrer plein ───
  const handleEnregistrerPlein = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await carburantService.createPlein({
        site: siteId,
        quantite_litres: parseFloat(litres),
        prix_unitaire_fcfa: parseFloat(prix),
        date_plein: datePlein || new Date().toISOString().split('T')[0],
      });
      setLitres('');
      setPrix('');
      setDatePlein('');
      showMessage('success', '✅ Plein enregistré');
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur');
    } finally {
      setLoading(false);
    }
  };

  // ─── Enregistrer consommation ───
  const handleEnregistrerConsommation = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await electriciteService.create({
        site: siteId,
        mois_annee: mois + '-01',
        consommation_kwh: kwh ? parseFloat(kwh) : undefined,
        montant_facture_fcfa: montant ? parseFloat(montant) : undefined,
      });
      setKwh('');
      setMontant('');
      showMessage('success', '✅ Consommation enregistrée');
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login-employe');
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: 'coupure', label: '⚡ Coupure' },
    { id: 'groupe', label: '🔧 Groupe' },
    { id: 'carburant', label: '⛽ Carburant' },
    { id: 'electricite', label: '💡 Électricité' },
  ];

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.brand}>CAMTEL PowerTracker</h1>
        <span>👤 {user?.prenom} {user?.nom}</span>
        <button onClick={handleLogout} style={styles.logoutBtn}>Déconnexion</button>
      </header>

      <main style={styles.main}>
        {/* Onglets */}
        <div style={styles.tabs}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{ ...styles.tab, ...(activeTab === tab.id ? styles.tabActive : {}) }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Messages */}
        {message && (
          <div style={{
            ...styles.message,
            ...(message.type === 'error' ? styles.messageError : styles.messageSuccess)
          }}>
            {message.text}
          </div>
        )}

        {/* TAB Coupure */}
        {activeTab === 'coupure' && (
          <div style={styles.tabContent}>
            {coupureOuverte ? (
              <div style={styles.cardState}>
                <h3 style={styles.title}>⚡ Coupure en cours</h3>
                <p>Début : {new Date(coupureOuverte.date_debut).toLocaleString('fr-FR')}</p>
                <button onClick={handleFermerCoupure} style={styles.stopBtn} disabled={loading}>
                  {loading ? '...' : 'Fermer cette coupure'}
                </button>
              </div>
            ) : (
              <form onSubmit={handleDeclarerCoupure} style={styles.form}>
                <h3 style={styles.title}>Déclarer une nouvelle coupure</h3>
                <label style={styles.label}>Date / heure début</label>
                <input
                  type="datetime-local"
                  value={dateDebut}
                  onChange={(e) => setDateDebut(e.target.value)}
                  style={styles.input}
                  required
                />
                <label style={styles.label}>Cause (optionnel)</label>
                <input
                  type="text"
                  value={cause}
                  onChange={(e) => setCause(e.target.value)}
                  style={styles.input}
                  placeholder="Ex: Maintenance réseau"
                />
                <button type="submit" style={styles.primaryBtn} disabled={loading}>
                  {loading ? '...' : 'Déclarer coupure'}
                </button>
              </form>
            )}
          </div>
        )}

        {/* TAB: Groupe */}
        {activeTab === 'groupe' && (
          <div style={styles.tabContent}>
            {sessionOuverte ? (
              <div style={styles.cardState}>
                <h3 style={styles.title}>🔧 Groupe actif</h3>
                <p>Démarré à : {new Date(sessionOuverte.timestamp_debut).toLocaleString('fr-FR')}</p>
                <button style={styles.stopBtn} onClick={handleArreterGroupe} disabled={loading}>
                  {loading ? '...' : 'Arrêter le groupe'}
                </button>
              </div>
            ) : (
              <form onSubmit={handleDemarrerGroupe} style={styles.form}>
                <h3 style={styles.title}>Démarrer groupe électrogène</h3>
                <label style={styles.label}>Date / heure début</label>
                <input
                  type="datetime-local"
                  value={dateDebut}
                  onChange={(e) => setDateDebut(e.target.value)}
                  style={styles.input}
                  required
                />
                <button type="submit" style={styles.primaryBtn} disabled={loading}>
                  {loading ? '...' : 'Démarrer groupe'}
                </button>
              </form>
            )}
          </div>
        )}

        {/* TAB: Carburant */}
        {activeTab === 'carburant' && (
          <div style={styles.tabContent}>
            <form onSubmit={handleEnregistrerPlein} style={styles.form}>
              <h3 style={styles.title}>⛽ Enregistrer un plein</h3>
              <label style={styles.label}>Quantité (litres)</label>
              <input type="number" min="0" value={litres} onChange={(e) => setLitres(e.target.value)} style={styles.input} placeholder="500" required />
              <label style={styles.label}>Prix unitaire (FCFA/L)</label>
              <input type="number" min="0" value={prix} onChange={(e) => setPrix(e.target.value)} style={styles.input} placeholder="625" required />
              <label style={styles.label}>Date du plein</label>
              <input type="date" value={datePlein} onChange={(e) => setDatePlein(e.target.value)} style={styles.input} required />
              {litres && prix && (
                <p style={styles.totalLabel}>Montant total : {(parseFloat(litres) * parseFloat(prix)).toLocaleString('fr-FR')} FCFA</p>
              )}
              <button type="submit" style={styles.primaryBtn} disabled={loading}>
                {loading ? '...' : 'Enregistrer plein'}
              </button>
            </form>
          </div>
        )}

        {/* TAB: Électricité */}
        {activeTab === 'electricite' && (
          <div style={styles.tabContent}>
            <form onSubmit={handleEnregistrerConsommation} style={styles.form}>
              <h3 style={styles.title}>💡 Consommation électrique mensuelle</h3>
              <label style={styles.label}>Mois</label>
              <input type="month" value={mois} onChange={(e) => setMois(e.target.value)} style={styles.input} required />
              <label style={styles.label}>Consommation (kWh)</label>
              <input type="number" min="0" value={kwh} onChange={(e) => setKwh(e.target.value)} style={styles.input} placeholder="2500" />
              <label style={styles.label}>Ou montant facture (FCFA)</label>
              <input type="number" min="0" value={montant} onChange={(e) => setMontant(e.target.value)} style={styles.input} placeholder="500000" />
              <button type="submit" style={styles.primaryBtn} disabled={loading}>
                {loading ? '...' : 'Enregistrer'}
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { minHeight: '100vh', background: '#f5f5f5' },
  header: {
    background: '#263238',
    color: 'white',
    padding: '16px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  brand: { margin: 0, fontSize: '20px' },
  logoutBtn: {
    background: '#c62828',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  main: { padding: '20px', maxWidth: '600px', margin: '0 auto' },
  tabs: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '8px',
    marginBottom: '20px',
  },
  tab: {
    padding: '12px 8px',
    borderRadius: '8px',
    border: '1px solid #ddd',
    background: 'white',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 'bold',
    textAlign: 'center',
  },
  tabActive: {
    background: '#263238',
    color: 'white',
    borderColor: '#263238',
  },
  tabContent: { animation: 'fadeIn 0.3s' },
  form: {
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  title: { margin: '0 0 16px', fontSize: '18px', color: '#333' },
  label: { display: 'block', fontSize: '14px', marginBottom: '6px', color: '#555' },
  input: {
    width: '100%',
    padding: '14px',
    borderRadius: '8px',
    border: '1px solid #ddd',
    fontSize: '16px',
    marginBottom: '16px',
    boxSizing: 'border-box',
    minHeight: '44px',
  },
  primaryBtn: {
    width: '100%',
    padding: '16px',
    background: '#263238',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    minHeight: '48px',
  },
  stopBtn: {
    width: '100%',
    padding: '14px',
    background: '#c62828',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '10px',
  },
  cardState: {
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  message: {
    padding: '12px',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '14px',
    textAlign: 'center',
  },
  messageSuccess: { background: '#e8f5e9', color: '#2e7d32' },
  messageError: { background: '#ffebee', color: '#c62828' },
  totalLabel: {
    background: '#e8eaf6',
    padding: '12px',
    borderRadius: '8px',
    textAlign: 'center',
    fontWeight: 'bold',
    color: '#1a237e',
    marginBottom: '16px',
  },
};