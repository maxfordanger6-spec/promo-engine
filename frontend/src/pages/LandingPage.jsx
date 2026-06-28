import React, { useState, useEffect } from 'react';
import { FaSpotify, FaYoutube, FaInstagram, FaTiktok, FaSoundcloud, FaApple, FaMusic, FaEnvelope } from 'react-icons/fa';
import toast from 'react-hot-toast';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || '';

const PLATFORM_ICONS = {
  spotify: FaSpotify,
  youtube: FaYoutube,
  instagram: FaInstagram,
  tiktok: FaTiktok,
  soundcloud: FaSoundcloud,
  applemusic: FaApple,
  default: FaMusic,
};

function LandingPage() {
  const [artist, setArtist] = useState(null);
  const [links, setLinks] = useState([]);
  const [subCount, setSubCount] = useState(0);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadArtist();
  }, []);

  const loadArtist = async () => {
    try {
      const { data } = await axios.get(`${API}/api/artist`);
      setArtist(data.artist);
      setLinks(data.links || []);
      setSubCount(data.subscriber_count || 0);
    } catch (err) {
      console.error('Failed to load artist:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (!email || !email.includes('@')) {
      toast.error('Email invalide');
      return;
    }
    try {
      const { data } = await axios.post(`${API}/api/email-capture`, { email, source: 'landing' });
      toast.success(data.message || 'Bienvenue ! 🔥');
      setEmail('');
      setSubCount(data.total_subscribers || subCount + 1);
    } catch (err) {
      toast.error('Erreur, réessaie...');
    }
  };

  if (loading) {
    return (
      <div className="landing-page">
        <div style={{ marginTop: '40vh', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem' }}>🎵</div>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="landing-page">
      <div className="hero">
        {artist?.image_url ? (
          <img src={artist.image_url} alt={artist.name} className="hero-avatar" />
        ) : (
          <div className="hero-avatar" style={{
            background: 'linear-gradient(135deg, #FF6B35, #FFD166)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '3rem', margin: '0 auto 1.5rem'
          }}>
            🎤
          </div>
        )}
        <h1>{artist?.name || 'Mrmakmax'}</h1>
        <p className="tagline">{artist?.genre || 'Afro Pop'} • nonamesbeats</p>
        <p className="bio">{artist?.bio || 'Afro pop singer. Born to make the world dance.'}</p>
      </div>

      {/* Music Player Placeholder */}
      <div className="music-player">
        <h3>🎧 Dernier son</h3>
        <p style={{ opacity: 0.6, fontSize: '0.9rem' }}>
          Retrouve mes morceaux sur toutes les plateformes ⬇️
        </p>
      </div>

      {/* Links */}
      <div className="links-section">
        {links.map((link) => {
          const Icon = PLATFORM_ICONS[link.platform?.toLowerCase()] || PLATFORM_ICONS.default;
          return (
            <a
              key={link.platform}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="link-button"
            >
              <span className="link-icon"><Icon /></span>
              <span className="link-label">{link.label || link.platform}</span>
            </a>
          );
        })}

        {links.length === 0 && (
          <p style={{ textAlign: 'center', opacity: 0.5, padding: '2rem' }}>
            Liens à venir... 🚀
          </p>
        )}
      </div>

      {/* Email Capture */}
      <div className="email-section">
        <h3>🔥 Rejoins la famille</h3>
        <p>Sois le premier à savoir quand je drop un nouveau son !</p>
        <form className="email-form" onSubmit={handleEmailSubmit}>
          <input
            type="email"
            placeholder="Ton email..."
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button type="submit">Je m'inscris</button>
        </form>
        <p className="sub-count">
          {subCount > 0 ? `👥 ${subCount} membres dans la famille` : ''}
        </p>
      </div>

      <div className="footer">
        <p>© {new Date().getFullYear()} Mrmakmax • nonamesbeats</p>
        <p>Powered by Promo Engine 🚀</p>
      </div>
    </div>
  );
}

export default LandingPage;
