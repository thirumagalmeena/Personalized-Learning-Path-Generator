import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiExternalLink, FiBook, FiCode, FiStar, FiX, FiRefreshCw } from 'react-icons/fi';
import { generateRoadmap, submitFeedback } from '../api/roadmap';
import LoadingSpinner from '../components/LoadingSpinner';

function StarRating({ value, onChange }) {
  const [hovered, setHovered] = useState(0);
  return (
    <div className="star-rating">
      {[1,2,3,4,5].map((s) => (
        <span
          key={s}
          className={`star ${s <= (hovered || value) ? 'active' : ''}`}
          onMouseEnter={() => setHovered(s)}
          onMouseLeave={() => setHovered(0)}
          onClick={() => onChange(s)}
        >★</span>
      ))}
    </div>
  );
}

function FeedbackModal({ resource, onClose }) {
  const [rating, setRating] = useState(0);
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const handleSubmit = async () => {
    if (!rating) return;
    setSubmitting(true);
    try {
      await submitFeedback({
        content_id: resource.url || resource.title,
        content_type: resource.type || 'resource',
        rating,
        comments,
      });
      setDone(true);
      setTimeout(onClose, 1500);
    } catch {
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(45,58,53,0.4)', backdropFilter: 'blur(4px)', zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div className="card" style={{ maxWidth: 440, width: '100%', position: 'relative' }}>
        <button onClick={onClose} style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}>
          <FiX size={20} />
        </button>
        {done ? (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>🎉</div>
            <h3>Thanks for your feedback!</h3>
          </div>
        ) : (
          <>
            <h3 style={{ marginBottom: 4 }}>Rate this resource</h3>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem', marginBottom: 20 }}>{resource.title}</p>
            <StarRating value={rating} onChange={setRating} />
            <div className="input-group" style={{ marginTop: 16, marginBottom: 20 }}>
              <label>Comments (optional)</label>
              <textarea value={comments} onChange={(e) => setComments(e.target.value)} placeholder="What did you think?" style={{ minHeight: 80 }} />
            </div>
            <button className="btn btn-primary" style={{ width: '100%' }} disabled={!rating || submitting} onClick={handleSubmit}>
              {submitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default function RoadmapPage() {
  const navigate = useNavigate();
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [feedbackResource, setFeedbackResource] = useState(null);

  const fetchRoadmap = async () => {
    setLoading(true);
    setError('');
    setRoadmap(null);
    try {
      const res = await generateRoadmap();
      setRoadmap(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (err.response?.status === 400 || (detail && detail.includes('profile'))) {
        navigate('/onboarding');
      } else {
        setError(detail || 'Failed to generate roadmap. Make sure Ollama is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRoadmap(); }, []);

  if (loading) return <LoadingSpinner message="Generating your personalized roadmap... This may take up to 30 seconds ☕" />;

  if (error) return (
    <div className="page">
      <div className="container-sm" style={{ textAlign: 'center', paddingTop: 60 }}>
        <div style={{ fontSize: '3rem', marginBottom: 16 }}>⚠️</div>
        <h2 style={{ marginBottom: 8 }}>Couldn't generate roadmap</h2>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: 24 }}>{error}</p>
        <button className="btn btn-primary" onClick={fetchRoadmap}><FiRefreshCw size={16} /> Try Again</button>
      </div>
    </div>
  );

  const phases = roadmap?.phases || [];

  return (
    <div className="page">
      {feedbackResource && <FeedbackModal resource={feedbackResource} onClose={() => setFeedbackResource(null)} />}

      <div className="container">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 36, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ fontSize: '1.9rem', marginBottom: 6 }}>Your Learning Roadmap 🗺️</h1>
            <p style={{ color: 'var(--color-text-muted)' }}>
              {phases.length} phases • Personalized just for you
            </p>
          </div>
          <button className="btn btn-outline" onClick={fetchRoadmap} style={{ gap: 8 }}>
            <FiRefreshCw size={16} /> Regenerate
          </button>
        </div>

        {phases.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: 60 }}>
            <p style={{ color: 'var(--color-text-muted)' }}>No phases returned. Try adding more skills first!</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => navigate('/skills')}>
              Add Skills
            </button>
          </div>
        ) : (
          <div className="timeline">
            {phases.map((phase, i) => (
              <div key={i} className="phase-card" style={{ animationDelay: `${i * 0.08}s` }}>
                <div className="card">
                  <div className="phase-header">
                    <span className="badge badge-primary">Phase {i + 1}</span>
                    <h3 className="phase-title">{phase.title}</h3>
                    {phase.duration && (
                      <span className="badge badge-accent" style={{ marginLeft: 'auto' }}>⏱ {phase.duration}</span>
                    )}
                  </div>

                  {/* Skill Tags */}
                  {phase.skills?.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
                      {phase.skills.map((sk, si) => (
                        <span key={si} className="badge badge-surface">{sk}</span>
                      ))}
                    </div>
                  )}

                  <div className="phase-body">
                    {/* Resources */}
                    {phase.resources?.length > 0 && (
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                          <FiBook size={15} color="var(--color-primary)" />
                          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Resources</span>
                        </div>
                        {phase.resources.map((r, ri) => (
                          <div key={ri} className="resource-item">
                            <FiExternalLink size={14} className="resource-icon" />
                            <div style={{ flex: 1 }}>
                              <a href={r.url} target="_blank" rel="noreferrer" style={{ fontSize: '0.88rem', fontWeight: 500, color: 'var(--color-text)', display: 'block' }}>
                                {r.title}
                              </a>
                              {r.type && <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{r.type}</span>}
                            </div>
                            <button
                              onClick={() => setFeedbackResource(r)}
                              title="Rate this resource"
                              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 4 }}
                            >
                              <FiStar size={15} />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Projects */}
                    {phase.projects?.length > 0 && (
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                          <FiCode size={15} color="var(--color-primary)" />
                          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Projects</span>
                        </div>
                        {phase.projects.map((p, pi) => (
                          <div key={pi} className="resource-item">
                            <FiCode size={14} className="resource-icon" />
                            <div>
                              <p style={{ fontSize: '0.88rem', fontWeight: 600, marginBottom: 2 }}>{p.title}</p>
                              <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{p.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
