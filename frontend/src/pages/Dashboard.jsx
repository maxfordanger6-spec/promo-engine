import React, { useState, useEffect } from 'react';
import { FaPlus, FaChartLine, FaLink, FaImage, FaUsers, FaBullseye, FaEnvelope, FaMusic, FaHandshake, FaHashtag, FaFire, FaCopy } from 'react-icons/fa';
import toast from 'react-hot-toast';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || '';

function Dashboard() {
  const [links, setLinks] = useState([]);
  const [analytics, setAnalytics] = useState([]);
  const [content, setContent] = useState([]);
  const [subCount, setSubCount] = useState(0);
  const [newLink, setNewLink] = useState({ platform: '', url: '', label: '' });
  const [activeTab, setActiveTab] = useState('links');
  
  // Growth module states
  const [targeting, setTargeting] = useState(null);
  const [emailSeq, setEmailSeq] = useState(null);
  const [playlists, setPlaylists] = useState(null);
  const [collabs, setCollabs] = useState(null);
  const [hashtags, setHashtags] = useState(null);
  const [pitchText, setPitchText] = useState('');
  const [pitchSong, setPitchSong] = useState('');

  useEffect(() => {
    loadBase();
    loadGrowthModules();
  }, []);

  const loadBase = async () => {
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
    } catch (err) {}
  };

  const loadGrowthModules = async () => {
    try {
      const [t, e, p, c, h] = await Promise.all([
        axios.get(`${API}/api/targeting/daily`),
        axios.get(`${API}/api/email/sequences?type=report`),
        axios.get(`${API}/api/playlists/targets?genre=strategy`),
        axios.get(`${API}/api/collabs/strategy`),
        axios.get(`${API}/api/hashtags/set`),
      ]);
      setTargeting(t.data || {});
      setEmailSeq(e.data || {});
      setPlaylists(p.data || {});
      setCollabs(c.data || {});
      setHashtags(h.data || {});
    } catch (err) {}
  };

  const addLink = async (e) => {
    e.preventDefault();
    if (!newLink.platform || !newLink.url) return toast.error('Plateforme et URL requis');
    try {
      await axios.post(`${API}/api/links`, newLink);
      toast.success('Lien ajouté !');
      setNewLink({ platform: '', url: '', label: '' });
      loadBase();
    } catch (err) { toast.error('Erreur...'); }
  };

  const generatePitch = async () => {
    if (!pitchSong) return toast.error('Titre du son requis');
    try {
      const { data } = await axios.get(`${API}/api/playlists/pitch?song=${encodeURIComponent(pitchSong)}&style=personal`);
      setPitchText(data.pitch);
      toast.success('Pitch généré !');
    } catch (err) { toast.error('Erreur...'); }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copié !');
  };

  const latestAnalytics = analytics?.[0] || {};

  const tabs = [
    { id: 'links', icon: FaLink, label: 'Liens' },
    { id: 'analytics', icon: FaChartLine, label: 'Stats' },
    { id: 'targeting', icon: FaBullseye, label: 'Ciblage' },
    { id: 'playlists', icon: FaMusic, label: 'Playlists' },
    { id: 'collabs', icon: FaHandshake, label: 'Collabs' },
    { id: 'hashtags', icon: FaHashtag, label: 'Hashtags' },
    { id: 'email', icon: FaEnvelope, label: 'Emails' },
    { id: 'content', icon: FaImage, label: 'Contenu' },
  ];

  return (
    <div className="dashboard">
      <h1>🎛️ Dashboard — Mrmakmax</h1>

      {/* Quick Stats */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        {[
          { icon: FaUsers, color: 'var(--primary)', value: subCount, label: 'Fans email' },
          { icon: FaLink, color: 'var(--secondary)', value: links.length, label: 'Liens' },
          { icon: FaBullseye, color: 'var(--accent)', value: targeting?.targets_artists?.length || '—', label: 'Cibles/jour' },
          { icon: FaMusic, color: '#EF476F', value: playlists?.phases?.[0]?.targets?.length || '8', label: 'Playlists' },
        ].map((stat, i) => (
          <div key={i} className="dash-card" style={{ flex: 1, minWidth: '140px', textAlign: 'center' }}>
            <stat.icon style={{ fontSize: '2rem', color: stat.color }} />
            <h2 style={{ margin: '0.5rem 0' }}>{stat.value}</h2>
            <p style={{ opacity: 0.7, fontSize: '0.85rem' }}>{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.3rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '0.85rem',
              background: activeTab === id ? 'var(--gradient)' : 'var(--card)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Icon /> {label}
          </button>
        ))}
      </div>

      {/* === LINKS TAB === */}
      {activeTab === 'links' && (
        <div className="dash-grid">
          <div className="dash-card">
            <h3>➕ Ajouter un lien</h3>
            <form className="add-link-form" onSubmit={addLink}>
              <input placeholder="Plateforme (spotify, youtube...)" value={newLink.platform}
                onChange={(e) => setNewLink({ ...newLink, platform: e.target.value })} />
              <input placeholder="URL" value={newLink.url}
                onChange={(e) => setNewLink({ ...newLink, url: e.target.value })} />
              <input placeholder="Label (optionnel)" value={newLink.label}
                onChange={(e) => setNewLink({ ...newLink, label: e.target.value })} />
              <button type="submit"><FaPlus /> Ajouter</button>
            </form>
          </div>
          <div className="dash-card">
            <h3>🔗 Liens actuels</h3>
            {links.map((link) => (
              <div key={link.platform} className="stat-row">
                <span className="stat-label">{link.label || link.platform}</span>
                <a href={link.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)', fontSize: '0.85rem' }}>
                  {link.url?.substring(0, 35)}...
                </a>
              </div>
            ))}
            {links.length === 0 && <p style={{ opacity: 0.5 }}>Aucun lien</p>}
          </div>
        </div>
      )}

      {/* === ANALYTICS TAB === */}
      {activeTab === 'analytics' && (
        <div className="dash-card">
          <h3>📊 Historique (7 jours)</h3>
          {analytics.length === 0 ? (
            <p style={{ opacity: 0.5 }}>Pas encore de données. Configure SPOTIFY_CLIENT_ID dans Railway pour les vraies stats.</p>
          ) : (
            analytics.map((snap) => (
              <div key={snap.date} className="stat-row">
                <span className="stat-label">{snap.date}</span>
                <span className="stat-value">{snap.spotify_monthly_listeners?.toLocaleString() || 0} listeners</span>
              </div>
            ))
          )}
        </div>
      )}

      {/* === TARGETING TAB === */}
      {activeTab === 'targeting' && (
        <div className="dash-grid">
          <div className="dash-card" style={{ gridColumn: '1/-1' }}>
            <h3>🎯 Stratégie d'engagement — {targeting?.date || 'Aujourd\'hui'}</h3>
            <p style={{ opacity: 0.7, marginBottom: '1rem' }}>{targeting?.strategy}</p>
            {targeting?.engagement_schedule && (
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                {Object.entries(targeting.engagement_schedule).map(([k, v]) => (
                  <div key={k} className="dash-card" style={{ flex: 1, minWidth: '200px' }}>
                    <strong style={{ textTransform: 'capitalize', color: 'var(--secondary)' }}>{k}</strong>
                    <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>{v}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="dash-card">
            <h3>🎵 Artistes à engager</h3>
            {(targeting?.targets_artists || []).slice(0, 8).map((a, i) => (
              <div key={i} className="stat-row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.3rem', padding: '0.8rem 0' }}>
                <span><strong>{a.name}</strong> <span style={{ opacity: 0.5, fontSize: '0.8rem' }}>{a.handle}</span></span>
                <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>💡 {a.engagement_tip}</span>
              </div>
            ))}
          </div>
          <div className="dash-card">
            <h3>📢 Comptes niche</h3>
            {(targeting?.targets_curators || []).slice(0, 8).map((a, i) => (
              <div key={i} className="stat-row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.3rem', padding: '0.8rem 0' }}>
                <span><strong>{a.name}</strong> <span style={{ opacity: 0.5, fontSize: '0.8rem' }}>{a.handle}</span> <span style={{ color: 'var(--accent)', fontSize: '0.75rem' }}>{a.followers}</span></span>
                <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>💡 {a.engagement_tip}</span>
              </div>
            ))}
          </div>
          {targeting?.rules && (
            <div className="dash-card" style={{ borderColor: 'var(--primary)' }}>
              <h3>⚠️ Règles d'or</h3>
              {targeting.rules.map((r, i) => (
                <p key={i} style={{ fontSize: '0.85rem', padding: '0.3rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>{r}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* === PLAYLISTS TAB === */}
      {activeTab === 'playlists' && (
        <div className="dash-grid">
          <div className="dash-card" style={{ gridColumn: '1/-1' }}>
            <h3>🎵 Playlist Pitching — {playlists?.song || 'Stratégie'}</h3>
          </div>
          {(playlists?.phases || []).map((phase, i) => (
            <div key={i} className="dash-card">
              <h3 style={{ color: 'var(--accent)' }}>📍 Phase {phase.phase}: {phase.name}</h3>
              <p style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>{phase.action}</p>
              <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>{phase.pitch?.substring(0, 120)}...</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--secondary)', marginTop: '0.5rem' }}>
                {(phase.targets || []).slice(0, 3).map(t => t.name).join(', ')}
              </p>
            </div>
          ))}
          <div className="dash-card">
            <h3>✍️ Générer un pitch</h3>
            <div className="add-link-form">
              <input placeholder="Titre du son..." value={pitchSong}
                onChange={(e) => setPitchSong(e.target.value)} />
              <button onClick={generatePitch}>Générer</button>
            </div>
            {pitchText && (
              <div style={{ marginTop: '1rem', position: 'relative' }}>
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px' }}>{pitchText}</pre>
                <button onClick={() => copyToClipboard(pitchText)} style={{
                  position: 'absolute', top: '0.5rem', right: '0.5rem',
                  background: 'var(--primary)', border: 'none', borderRadius: '6px',
                  color: '#fff', padding: '0.3rem 0.6rem', cursor: 'pointer', fontSize: '0.8rem'
                }}><FaCopy /> Copier</button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* === COLLABS TAB === */}
      {activeTab === 'collabs' && (
        <div className="dash-grid">
          {(collabs?.strategy?.phases || []).map((phase, i) => (
            <div key={i} className="dash-card">
              <h3 style={{ color: 'var(--accent)' }}>📍 Phase {phase.phase}: {phase.name}</h3>
              <p style={{ fontSize: '0.9rem' }}>{phase.action}</p>
              <p style={{ fontSize: '0.8rem', opacity: 0.7, marginTop: '0.5rem' }}>{phase.why}</p>
              <div style={{ marginTop: '0.5rem' }}>
                {(phase.targets || []).slice(0, 4).map((t, j) => (
                  <span key={j} style={{
                    display: 'inline-block', background: 'rgba(255,107,53,0.2)',
                    padding: '0.2rem 0.6rem', borderRadius: '6px', margin: '0.2rem',
                    fontSize: '0.75rem'
                  }}>{t.name}</span>
                ))}
              </div>
            </div>
          ))}
          {collabs?.daily && (
            <div className="dash-card" style={{ borderColor: 'var(--secondary)' }}>
              <h3>📅 Actions quotidiennes</h3>
              {(collabs.daily.daily_actions || []).map((a, i) => (
                <p key={i} style={{ fontSize: '0.85rem', padding: '0.3rem 0' }}>{a}</p>
              ))}
            </div>
          )}
          {collabs?.strategy?.budget_estimate && (
            <div className="dash-card">
              <h3>💰 Budget estimé</h3>
              {Object.entries(collabs.strategy.budget_estimate).map(([k, v]) => (
                <div key={k} className="stat-row">
                  <span className="stat-label" style={{ textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</span>
                  <span className="stat-value">{v}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* === HASHTAGS TAB === */}
      {activeTab === 'hashtags' && (
        <div className="dash-grid">
          <div className="dash-card" style={{ gridColumn: '1/-1' }}>
            <h3>🏷️ Hashtags optimisés — {hashtags?.platform || 'Instagram'} ({hashtags?.content_type || 'new_release'})</h3>
            <div style={{ position: 'relative' }}>
              <p style={{
                background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px',
                fontSize: '0.9rem', wordBreak: 'break-word'
              }}>
                {hashtags?.hashtag_string || 'Chargement...'}
              </p>
              <button onClick={() => copyToClipboard(hashtags?.hashtag_string || '')} style={{
                position: 'absolute', top: '0.5rem', right: '0.5rem',
                background: 'var(--primary)', border: 'none', borderRadius: '6px',
                color: '#fff', padding: '0.3rem 0.6rem', cursor: 'pointer'
              }}><FaCopy /> Copier</button>
            </div>
            <p style={{ fontSize: '0.8rem', opacity: 0.6, marginTop: '0.5rem' }}>📌 {hashtags?.strategy}</p>
          </div>
          <div className="dash-card">
            <h3>📋 Hashtags individuels</h3>
            {(hashtags?.hashtags || []).map((tag, i) => (
              <span key={i} onClick={() => copyToClipboard(tag)} style={{
                display: 'inline-block', background: 'rgba(6,214,160,0.15)',
                padding: '0.3rem 0.7rem', borderRadius: '8px', margin: '0.2rem',
                fontSize: '0.8rem', cursor: 'pointer'
              }}>{tag}</span>
            ))}
          </div>
          <div className="dash-card">
            <h3>💡 Best Practices</h3>
            {(hashtags?.best_practices || []).map((tip, i) => (
              <p key={i} style={{ fontSize: '0.85rem', padding: '0.3rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>{tip}</p>
            ))}
          </div>
        </div>
      )}

      {/* === EMAIL TAB === */}
      {activeTab === 'email' && (
        <div className="dash-grid">
          <div className="dash-card" style={{ gridColumn: '1/-1' }}>
            <h3>📧 Email Nurture</h3>
          </div>
          {emailSeq?.active_sequences ? (
            <div className="dash-card" style={{ gridColumn: '1/-1' }}>
              <h3>📁 Séquences actives</h3>
              {Object.entries(emailSeq.active_sequences).map(([name, desc]) => (
                <div key={name} className="stat-row" style={{ flexDirection: 'column', alignItems: 'flex-start', padding: '0.6rem 0' }}>
                  <strong style={{ textTransform: 'capitalize', color: 'var(--secondary)' }}>{name}</strong>
                  <span style={{ fontSize: '0.85rem', opacity: 0.7 }}>{desc}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="dash-card">
              <h3>Welcome Sequence (3 emails / 7 jours)</h3>
              <p style={{ fontSize: '0.85rem' }}>Configurer SMTP_USERNAME et SMTP_PASSWORD dans les variables Railway pour activer l'envoi automatique.</p>
            </div>
          )}
          <div className="dash-card">
            <h3>💡 Actions recommandées</h3>
            {(emailSeq?.recommended_actions || [
              "Configurer SMTP_USERNAME et SMTP_PASSWORD",
              "Connecter SendGrid ou Brevo pour délivrabilité",
              "Ajouter UTM tags pour tracker les clics"
            ]).map((a, i) => (
              <p key={i} style={{ fontSize: '0.85rem', padding: '0.3rem 0' }}>• {a}</p>
            ))}
          </div>
          <div className="dash-card">
            <h3>📊 Best Practices</h3>
            {(emailSeq?.best_practices || []).map((b, i) => (
              <p key={i} style={{ fontSize: '0.85rem', padding: '0.3rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>{b}</p>
            ))}
          </div>
        </div>
      )}

      {/* === CONTENT TAB === */}
      {activeTab === 'content' && (
        <div className="dash-card">
          <h3>🎨 Contenu généré</h3>
          {content.length === 0 ? (
            <p style={{ opacity: 0.5 }}>Pas encore de contenu. La Content Factory tourne toutes les 6h — premier drop bientôt !</p>
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
