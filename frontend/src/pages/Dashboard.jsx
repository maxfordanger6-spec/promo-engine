import React, { useState, useEffect } from 'react';
import { FaPlus, FaTrash, FaChartLine, FaLink, FaImage, FaUsers } from 'react-icons/fa';
import toast from 'react-hot-toast';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || '';

function Dashboard() {
  const [links, setLinks] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [content, setContent] = useState([]);
  const [subCount, setSubCount] = useState(0);
  const [newLink, setNewLink] = useState({ platform: '', url: '', label: '' });
  const [activeTab, setActiveTab] = useState('links');

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [linksRes, analyticsRes, contentRes, countRes] = await Promise.all([
        axios.get(`${API}/api/links`),
        axios.get(`${API}/api/analytics?days=7`),
        axios.get(`${API}/api/content?limit=10`),
        axios.get(`${API}/api/subscribers/count`),
      ]);
      setLinks(linksRes.data || []);
      setAnalytics(analyticsRes.data?.history || []);
      setContent(contentRes.data?.content || []);
      setSubCount(countRes.data?.count || 0);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  };

  const addLink = async (e) => {
    e.preventDefault();
    if (!newLink.platform || !newLink.url) {
      toast.error('Plateforme et URL requis');
      return;
    }
    try {
      await axios.post(`${API}/api/links`, newLink);
      toast.success('Lien ajouté !');
      setNewLink({ platform: '', url: '', label: '' });
      loadAll();
    } catch (err) {
      toast.error('Erreur...');
    }
  };

  const latestAnalytics = analytics?.[0] || {};

  return (
    <div className="dashboard">
      <h1>🎛️ Dashboard — Mrmakmax</h1>

      {/* Quick Stats */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        <div className="dash-card" style={{ flex: 1, minWidth: '160px', textAlign: 'center' }}>
          <FaUsers style={{ fontSize: '2rem', color: 'var(--primary)' }} />
          <h2 style={{ margin: '0.5rem 0' }}>{subCount}</h2>
          <p style={{ opacity: 0.7, fontSize: '0.9rem' }}>Fans email</p>
        </div>
        <div className="dash-card" style={{ flex: 1, minWidth: '160px', textAlign: 'center' }}>
          <FaLink style={{ fontSize: '2rem', color: 'var(--secondary)' }} />
          <h2 style={{ margin: '0.5rem 0' }}>{links.length}</h2>
          <p style={{ opacity: 0.7, fontSize: '0.9rem' }}>Liens actifs</p>
        </div>
        <div className="dash-card" style={{ flex: 1, minWidth: '160px', textAlign: 'center' }}>
          <FaImage style={{ fontSize: '2rem', color: 'var(--accent)' }} />
          <h2 style={{ margin: '0.5rem 0' }}>{content.length}</h2>
          <p style={{ opacity: 0.7, fontSize: '0.9rem' }}>Contenus générés</p>
        </div>
        <div className="dash-card" style={{ flex: 1, minWidth: '160px', textAlign: 'center' }}>
          <FaChartLine style={{ fontSize: '2rem', color: '#EF476F' }} />
          <h2 style={{ margin: '0.5rem 0' }}>
            {latestAnalytics.spotify_monthly_listeners?.toLocaleString() || '—'}
          </h2>
          <p style={{ opacity: 0.7, fontSize: '0.9rem' }}>Listeners Spotify</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        {['links', 'analytics', 'content'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '0.6rem 1.2rem',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 600,
              background: activeTab === tab ? 'var(--gradient)' : 'var(--card)',
              color: '#fff',
              textTransform: 'capitalize',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'links' && (
        <div className="dash-grid">
          <div className="dash-card">
            <h3>➕ Ajouter un lien</h3>
            <form className="add-link-form" onSubmit={addLink}>
              <input
                placeholder="Plateforme (spotify, youtube...)"
                value={newLink.platform}
                onChange={(e) => setNewLink({ ...newLink, platform: e.target.value })}
              />
              <input
                placeholder="URL"
                value={newLink.url}
                onChange={(e) => setNewLink({ ...newLink, url: e.target.value })}
              />
              <input
                placeholder="Label (optionnel)"
                value={newLink.label}
                onChange={(e) => setNewLink({ ...newLink, label: e.target.value })}
              />
              <button type="submit"><FaPlus /> Ajouter</button>
            </form>
          </div>

          <div className="dash-card">
            <h3>🔗 Liens actuels</h3>
            {links.map((link) => (
              <div key={link.platform} className="stat-row">
                <span className="stat-label">{link.label || link.platform}</span>
                <a href={link.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)', fontSize: '0.85rem' }}>
                  {link.url?.substring(0, 30)}...
                </a>
              </div>
            ))}
            {links.length === 0 && <p style={{ opacity: 0.5 }}>Aucun lien</p>}
          </div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="dash-card">
          <h3>📊 Historique (7 jours)</h3>
          {analytics.length === 0 ? (
            <p style={{ opacity: 0.5 }}>Pas encore de données. Le tracking automatique va bientôt commencer.</p>
          ) : (
            analytics.map((snap) => (
              <div key={snap.date} className="stat-row">
                <span className="stat-label">{snap.date}</span>
                <span className="stat-value">
                  {snap.spotify_monthly_listeners?.toLocaleString() || 0} listeners
                </span>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'content' && (
        <div className="dash-card">
          <h3>🎨 Contenu généré</h3>
          {content.length === 0 ? (
            <p style={{ opacity: 0.5 }}>Pas encore de contenu. La Content Factory va bientôt tourner !</p>
          ) : (
            content.map((item) => (
              <div key={item._id} className="stat-row">
                <span className="stat-label">{item.type}</span>
                <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                  {new Date(item.created_at).toLocaleDateString('fr')}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
