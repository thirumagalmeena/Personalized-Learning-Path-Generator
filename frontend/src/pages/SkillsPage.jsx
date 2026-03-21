import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiSend, FiArrowRight, FiCheckCircle, FiTarget } from 'react-icons/fi';
import { extractSkills } from '../api/user';

const EXAMPLE_TEXTS = [
  "I've been working with Python for a year and know some Pandas. I want to learn Machine Learning and Deep Learning.",
  "I've built static sites with HTML, CSS, and JavaScript. I'm transitioning to a frontend role and need to learn React and Tailwind.",
  "I'm comfortable with SQL and data analysis. I want to get into cloud engineering with AWS and Kubernetes.",
];

export default function SkillsPage() {
  const navigate = useNavigate();
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) { setError('Please describe your skills first.'); return; }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await extractSkills(text);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Skill extraction failed. Is your backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container">
        <div style={{ marginBottom: 36 }}>
          <h1 style={{ fontSize: '1.9rem', marginBottom: 8 }}>Skill Assessment 🔍</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>
            Tell us about yourself in plain English — what you know and what you want to learn.
          </p>
        </div>

        {/* Input Card */}
        <div className="card" style={{ marginBottom: 24 }}>
          <form onSubmit={handleSubmit}>
            <div className="input-group" style={{ marginBottom: 16 }}>
              <label>Describe your current skills and learning goals</label>
              <textarea
                value={text}
                onChange={(e) => { setText(e.target.value); setError(''); }}
                placeholder="e.g. I have been working with Python for a year and know some Pandas. I want to learn Machine Learning and Deep Learning next..."
                style={{ minHeight: 140 }}
              />
            </div>

            {/* Example chips */}
            <div style={{ marginBottom: 16 }}>
              <p style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Try an example:
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {EXAMPLE_TEXTS.map((ex, i) => (
                  <button
                    key={i}
                    type="button"
                    className="badge badge-accent"
                    onClick={() => setText(ex)}
                    style={{ cursor: 'pointer', border: 'none', padding: '6px 14px', fontSize: '0.8rem' }}
                  >
                    Example {i + 1}
                  </button>
                ))}
              </div>
            </div>

            {error && <div className="alert alert-error" style={{ marginBottom: 12 }}>{error}</div>}

            <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%' }}>
              {loading ? (
                <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Analyzing skills...</>
              ) : (
                <><FiSend size={16} /> Analyze My Skills</>
              )}
            </button>
          </form>
        </div>

        {/* Results */}
        {result && (
          <>
            <div className="skills-grid" style={{ marginBottom: 24 }}>
              {/* Known Skills */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                  <FiCheckCircle size={20} color="var(--color-success)" />
                  <h3 style={{ fontSize: '1rem' }}>Skills You Know</h3>
                  <span className="badge badge-primary" style={{ marginLeft: 'auto' }}>{result.extracted_skills.length}</span>
                </div>
                {result.extracted_skills.length === 0 && (
                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem' }}>No existing skills detected.</p>
                )}
                {result.extracted_skills.map((s, i) => (
                  <div key={i} className="skill-item">
                    <span className="skill-name">{s.skill_name}</span>
                    <div className="confidence-bar">
                      <div className="confidence-fill" style={{ width: `${Math.round(s.confidence * 100)}%` }} />
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', minWidth: 32 }}>
                      {Math.round(s.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>

              {/* Desired Skills */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                  <FiTarget size={20} color="var(--color-primary)" />
                  <h3 style={{ fontSize: '1rem' }}>Skills You Want to Learn</h3>
                  <span className="badge badge-accent" style={{ marginLeft: 'auto' }}>{result.desired_skills.length}</span>
                </div>
                {result.desired_skills.length === 0 && (
                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem' }}>No desired skills detected. Try mentioning what you want to learn!</p>
                )}
                {result.desired_skills.map((s, i) => (
                  <div key={i} className="skill-item">
                    <span className="skill-name">{s.skill_name}</span>
                    <span className="badge badge-accent" style={{ fontSize: '0.75rem' }}>Desired</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              className="btn btn-primary"
              onClick={() => navigate('/roadmap')}
              style={{ width: '100%', padding: '16px', fontSize: '1rem' }}
            >
              Generate My Roadmap <FiArrowRight size={18} />
            </button>
          </>
        )}
      </div>
    </div>
  );
}
