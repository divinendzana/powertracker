import { useState, FormEvent, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { sitesService } from '../services/data.service';
import { Site } from '../types';

export default function LoginEmployePage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [selectedSite, setSelectedSite] = useState('');
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { loginEmploye } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSites = async () => {
      try {
        const data = await sitesService.list({ actif: 'true' });
        setSites(data.results);
        if (data.results.length > 0) {
          const stored = localStorage.getItem('last_site_id');
          setSelectedSite(stored && data.results.some(s => s.id === stored) ? stored : data.results[0].id);
        }
      } catch {
        // Ignorer, le site sélecteur restera vide
      }
    };
    fetchSites();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginEmploye(pin, selectedSite);
      localStorage.setItem('last_site_id', selectedSite);
      navigate('/operations');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'PIN invalide');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.logoContainer}>
          <h1 style={styles.brand}>CAMTEL</h1>
          <p style={styles.brandSub}>PowerTracker</p>
        </div>
        <h2 style={styles.title}>Connexion Employé</h2>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>Site</label>
            <select
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value)}
              style={styles.input}
              required
            >
              {sites.length === 0 && <option value="">Chargement...</option>}
              {sites.map((site) => (
                <option key={site.id} value={site.id}>{site.nom}</option>
              ))}
            </select>
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Code PIN (4 chiffres)</label>
            <input
              type="password"
              inputMode="numeric"
              maxLength={4}
              pattern="[0-9]*"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
              style={{ ...styles.input, textAlign: 'center', fontSize: '24px', letterSpacing: '8px' }}
              placeholder="••••"
              required
            />
          </div>
          <button type="submit" style={{ ...styles.button, opacity: loading ? 0.7 : 1 }} disabled={loading}>
            {loading ? 'Connexion...' : 'Accéder'}
          </button>
        </form>
        <div style={styles.footer}>
          <Link to="/login-admin" style={styles.link}>Administratrice ? Connexion email</Link>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #263238 0%, #37474f 100%)',
    padding: '20px',
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '40px',
    width: '100%',
    maxWidth: '400px',
    boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
  },
  logoContainer: {
    textAlign: 'center',
    marginBottom: '20px',
  },
  brand: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#37474f',
    margin: 0,
  },
  brandSub: {
    color: '#666',
    fontSize: '14px',
    margin: 0,
  },
  title: {
    textAlign: 'center',
    fontSize: '18px',
    color: '#333',
    marginBottom: '20px',
  },
  field: {
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    fontSize: '14px',
    marginBottom: '6px',
    color: '#555',
  },
  input: {
    width: '100%',
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #ddd',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  button: {
    width: '100%',
    padding: '14px',
    background: '#37474f',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '10px',
  },
  error: {
    background: '#ffebee',
    color: '#c62828',
    padding: '10px',
    borderRadius: '8px',
    fontSize: '14px',
    marginBottom: '16px',
  },
  footer: {
    textAlign: 'center',
    marginTop: '20px',
  },
  link: {
    color: '#37474f',
    textDecoration: 'none',
    fontSize: '14px',
  },
};