import { useEffect, useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  seuilsService,
  sitesService,
  employesService,
} from '../services/data.service';
import { SeuilsAlerte, Site, Employe } from '../types';

type TabId = 'seuils' | 'employes' | 'sites';

export default function ParametresPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabId>('seuils');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Seuils
  const [seuils, setSeuils] = useState<SeuilsAlerte | null>(null);
  const [seuilCarburant, setSeuilCarburant] = useState('');
  const [seuilElectricite, setSeuilElectricite] = useState('');
  const [fenetreCarburant, setFenetreCarburant] = useState('');
  const [fenetreElectricite, setFenetreElectricite] = useState('');

  // Employés
  const [employes, setEmployes] = useState<Employe[]>([]);
  const [newEmploye, setNewEmploye] = useState({
    prenom: '',
    nom: '',
    site: '',
    pin: '',
    email: '',
  });

  // Sites
  const [sites, setSites] = useState<Site[]>([]);
  const [newSite, setNewSite] = useState({
    nom: '',
    adresse: '',
    type_carburant: 'essence',
    type_groupe: '',
    puissance_kva: '',
  });

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const fetchSeuils = async () => {
    try {
      const data = await seuilsService.get();
      setSeuils(data);
      setSeuilCarburant(String(data.seuil_carburant_pct));
      setSeuilElectricite(String(data.seuil_electricite_pct));
      setFenetreCarburant(String(data.fenetre_historique_carburant_mois));
      setFenetreElectricite(String(data.fenetre_historique_electricite_mois));
    } catch {
      // Ignorer
    }
  };

  const fetchEmployes = async () => {
    try {
      const data = await employesService.list();
      setEmployes(data.results);
    } catch {
      // Ignorer
    }
  };

  const fetchSites = async () => {
    try {
      const data = await sitesService.list();
      setSites(data.results);
    } catch {
      // Ignorer
    }
  };

  useEffect(() => {
    fetchSeuils();
    fetchEmployes();
    fetchSites();
  }, []);

  const handleSaveSeuils = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await seuilsService.update({
        seuil_carburant_pct: parseFloat(seuilCarburant),
        seuil_electricite_pct: parseFloat(seuilElectricite),
        fenetre_historique_carburant_mois: parseInt(fenetreCarburant),
        fenetre_historique_electricite_mois: parseInt(fenetreElectricite),
      });
      showMessage('success', '✅ Seuils mis à jour avec succès');
      fetchSeuils();
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur lors de la mise à jour');
    }
  };

  const handleCreateEmploye = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await employesService.create({
        prenom: newEmploye.prenom,
        nom: newEmploye.nom,
        site: newEmploye.site,
        pin: newEmploye.pin,
        email: newEmploye.email || undefined,
      });
      setNewEmploye({ prenom: '', nom: '', site: '', pin: '', email: '' });
      showMessage('success', '✅ Employé créé avec succès');
      fetchEmployes();
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleCreateSite = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await sitesService.create({
        nom: newSite.nom,
        adresse: newSite.adresse,
        type_carburant: newSite.type_carburant as 'essence' | 'gazoil',
        type_groupe: newSite.type_groupe || undefined,
        puissance_kva: newSite.puissance_kva ? parseFloat(newSite.puissance_kva) : undefined,
      });
      setNewSite({ nom: '', adresse: '', type_carburant: 'essence', type_groupe: '', puissance_kva: '' });
      showMessage('success', '✅ Site créé avec succès');
      fetchSites();
    } catch (err: any) {
      showMessage('error', err.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login-admin');
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: 'seuils', label: '⚙️ Seuils d\'alerte' },
    { id: 'employes', label: '👥 Employés' },
    { id: 'sites', label: '🏢 Sites' },
  ];

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.brand}>CAMTEL PowerTracker</h1>
          <span>⚙️ Paramètres</span>
        </div>
        <div style={styles.headerActions}>
          <button onClick={() => navigate('/dashboard')} style={styles.navBtn}>Dashboard</button>
          <button onClick={() => navigate('/historique')} style={styles.navBtn}>Historique</button>
          <button onClick={handleLogout} style={styles.logoutBtn}>Déconnexion</button>
        </div>
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

        {message && (
          <div style={{
            ...styles.message,
            ...(message.type === 'error' ? styles.messageError : styles.messageSuccess)
          }}>
            {message.text}
          </div>
        )}

        {/* TAB Seuils */}
        {activeTab === 'seuils' && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>Configuration des seuils d'alerte</h2>
            <form onSubmit={handleSaveSeuils} style={styles.form}>
              <div style={styles.formGrid}>
                <div>
                  <label style={styles.label}>Seuil écart carburant (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={seuilCarburant}
                    onChange={(e) => setSeuilCarburant(e.target.value)}
                    style={styles.input}
                    required
                  />
                  <p style={styles.hint}>{`Alerte si ratio s'écarte > ${seuilCarburant}% moyenne`}</p>
                </div>
                <div>
                  <label style={styles.label}>Fenêtre historique carburant (mois)</label>
                  <input
                    type="number"
                    min="1"
                    value={fenetreCarburant}
                    onChange={(e) => setFenetreCarburant(e.target.value)}
                    style={styles.input}
                    required
                  />
                </div>
                <div>
                  <label style={styles.label}>Seuil écart électricité (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={seuilElectricite}
                    onChange={(e) => setSeuilElectricite(e.target.value)}
                    style={styles.input}
                    required
                  />
                  <p style={styles.hint}>{`Alerte si consommation s'écarte > ±${seuilElectricite}%`}</p>
                </div>
                <div>
                  <label style={styles.label}>Fenêtre historique électricité (mois)</label>
                  <input
                    type="number"
                    min="1"
                    value={fenetreElectricite}
                    onChange={(e) => setFenetreElectricite(e.target.value)}
                    style={styles.input}
                    required
                  />
                </div>
              </div>
              <button type="submit" style={styles.primaryBtn}>Enregistrer les changements</button>
            </form>
          </section>
        )}

        {/* TAB Employés */}
        {activeTab === 'employes' && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>Gestion des employés</h2>
            <form onSubmit={handleCreateEmploye} style={styles.form}>
              <h3 style={styles.subTitle}>Ajouter un employé</h3>
              <div style={styles.formGrid}>
                <div>
                  <label style={styles.label}>Prénom</label>
                  <input type="text" value={newEmploye.prenom} onChange={(e) => setNewEmploye({ ...newEmploye, prenom: e.target.value })} style={styles.input} required />
                </div>
                <div>
                  <label style={styles.label}>Nom</label>
                  <input type="text" value={newEmploye.nom} onChange={(e) => setNewEmploye({ ...newEmploye, nom: e.target.value })} style={styles.input} required />
                </div>
                <div>
                  <label style={styles.label}>Site</label>
                  <select value={newEmploye.site} onChange={(e) => setNewEmploye({ ...newEmploye, site: e.target.value })} style={styles.input} required>
                    <option value="">Sélectionner</option>
                    {sites.map((site) => (
                      <option key={site.id} value={site.id}>{site.nom}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={styles.label}>PIN (4 chiffres)</label>
                  <input
                    type="password"
                    maxLength={4}
                    pattern="[0-9]*"
                    value={newEmploye.pin}
                    onChange={(e) => setNewEmploye({ ...newEmploye, pin: e.target.value.replace(/\D/g, '') })}
                    style={styles.input}
                    required
                  />
                </div>
              </div>
              <button type="submit" style={styles.primaryBtn}>Créer employé</button>
            </form>

            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Nom</th>
                  <th style={styles.th}>Site</th>
                  <th style={styles.th}>Actif</th>
                </tr>
              </thead>
              <tbody>
                {employes.map((emp) => (
                  <tr key={emp.id}>
                    <td style={styles.td}>{emp.prenom} {emp.nom}</td>
                    <td style={styles.td}>{emp.site_nom || '-'}</td>
                    <td style={styles.td}>{emp.actif ? '✓' : '✗'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {/* TAB Sites */}
        {activeTab === 'sites' && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>Gestion des sites</h2>
            <form onSubmit={handleCreateSite} style={styles.form}>
              <h3 style={styles.subTitle}>Ajouter un site</h3>
              <div style={styles.formGrid}>
                <div>
                  <label style={styles.label}>Nom</label>
                  <input type="text" value={newSite.nom} onChange={(e) => setNewSite({ ...newSite, nom: e.target.value })} style={styles.input} required />
                </div>
                <div>
                  <label style={styles.label}>Adresse</label>
                  <input type="text" value={newSite.adresse} onChange={(e) => setNewSite({ ...newSite, adresse: e.target.value })} style={styles.input} required />
                </div>
                <div>
                  <label style={styles.label}>Type carburant</label>
                  <select
                    value={newSite.type_carburant}
                    onChange={(e) => setNewSite({ ...newSite, type_carburant: e.target.value })}
                    style={styles.input}
                  >
                    <option value="essence">Essence</option>
                    <option value="gazoil">Gazoil</option>
                  </select>
                </div>
                <div>
                  <label style={styles.label}>Modèle groupe</label>
                  <input type="text" value={newSite.type_groupe} onChange={(e) => setNewSite({ ...newSite, type_groupe: e.target.value })} style={styles.input} placeholder="Caterpillar C9" />
                </div>
              </div>
              <button type="submit" style={styles.primaryBtn}>Créer site</button>
            </form>

            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Nom</th>
                  <th style={styles.th}>Adresse</th>
                  <th style={styles.th}>Carburant</th>
                  <th style={styles.th}>Actif</th>
                </tr>
              </thead>
              <tbody>
                {sites.map((site) => (
                  <tr key={site.id}>
                    <td style={styles.td}>{site.nom}</td>
                    <td style={styles.td}>{site.adresse}</td>
                    <td style={styles.td}>{site.type_carburant}</td>
                    <td style={styles.td}>{site.actif ? '✓' : '✗'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
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
  tabs: {
    display: 'flex',
    gap: '8px',
    marginBottom: '20px',
  },
  tab: {
    padding: '10px 20px',
    borderRadius: '8px',
    border: '1px solid #ddd',
    background: 'white',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  tabActive: {
    background: '#1a237e',
    color: 'white',
    borderColor: '#1a237e',
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
  section: { background: 'white', borderRadius: '10px', padding: '20px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' },
  sectionTitle: { fontSize: '18px', margin: '0 0 16px', color: '#333' },
  subTitle: { fontSize: '15px', color: '#555', margin: '0 0 16px' },
  form: { marginBottom: '24px', borderBottom: '1px solid #eee', paddingBottom: '24px' },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '16px',
  },
  label: { display: 'block', fontSize: '14px', marginBottom: '6px', color: '#555' },
  input: {
    width: '100%',
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #ddd',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  hint: { fontSize: '12px', color: '#888', marginTop: '4px' },
  primaryBtn: {
    padding: '12px 24px',
    background: '#1a237e',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 'bold',
    cursor: 'pointer',
  },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '14px' },
  th: { textAlign: 'left', padding: '12px', borderBottom: '2px solid #e0e0e0', color: '#333', background: '#fafafa' },
  td: { padding: '12px', borderBottom: '1px solid #eee' },
};