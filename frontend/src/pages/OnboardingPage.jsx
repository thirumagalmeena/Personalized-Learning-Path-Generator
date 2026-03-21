import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiArrowRight, FiPlus, FiMap } from 'react-icons/fi';
import { getGoals, updateProfile } from '../api/user';
import LoadingSpinner from '../components/LoadingSpinner';

const CATEGORY_EMOJI = {
  'AI & Data Career': '🤖', 'Web Development Career': '🌐',
  'Data Science': '📊', 'Cloud Career': '☁️',
  'Security Career': '🔐', 'Software Engineering': '⚙️',
  'Programming Career': '💻', 'Programming Advanced': '🧩',
  'Data Engineering': '🔧', 'AI Research': '🔬',
  'Mathematics Foundation': '📐', 'Finance': '💹',
  'Product & AI': '🎯', 'Cloud & DevOps Career': '🚀',
  'Data Analytics': '📈', 'Security & Dev': '🛡️',
};

const EXPERIENCE_OPTS = ['beginner', 'intermediate', 'advanced'];
const STYLE_OPTS = ['visual', 'reading', 'interactive'];
const HOURS_OPTS = [5, 10, 15, 20, 30];

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [goals, setGoals] = useState([]);
  const [loadingGoals, setLoadingGoals] = useState(true);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [experience, setExperience] = useState('beginner');
  const [style, setStyle] = useState('visual');
  const [hours, setHours] = useState(10);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);

  // Check if returning user (has goal_id in their profile)
  // We'll check via localStorage flag set during login flow
  const isReturningUser = localStorage.getItem('has_plan') === 'true';

  useEffect(() => {
    getGoals()
      .then((res) => setGoals(res.data))
      .catch(() => setError('Could not load goals. Is your backend running?'))
      .finally(() => setLoadingGoals(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedGoal) { setError('Please select a learning goal.'); return; }
    setSubmitting(true);
    setError('');
    try {
      await updateProfile({
        goal_id: String(selectedGoal.goal_id),
        experience_level: experience,
        available_hours_per_week: hours,
        learning_style: style,
      });
      localStorage.setItem('has_plan', 'true');
      navigate('/skills');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingGoals) return <LoadingSpinner message="Loading goals..." />;

  // Returning user choice screen
  if (isReturningUser && !showForm) {
    return (
      <div className="page-center" style={{ background: 'linear-gradient(135deg, #F5E4D7, #E5D1D6)' }}>
        <div className="container-sm" style={{ width: '100%' }}>
          <div className="card" style={{ textAlign: 'center' }}>
            <h2 style={{ marginBottom: 8 }}>Welcome back! 🎉</h2>
            <p style={{ color: 'var(--color-text-muted)', marginBottom: 32 }}>
              What would you like to do today?
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <button className="btn btn-primary" style={{ width: '100%', padding: '16px' }} onClick={() => navigate('/roadmap')}>
                <FiMap size={18} /> View My Existing Roadmap
              </button>
              <button className="btn btn-outline" style={{ width: '100%', padding: '16px' }} onClick={() => setShowForm(true)}>
                <FiPlus size={18} /> Create a New Plan
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page" style={{ background: 'linear-gradient(135deg, #F5E4D7, #E5D1D6)', minHeight: '100vh' }}>
      <div className="container">
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <h1 style={{ fontSize: '2rem', marginBottom: 8 }}>Build Your Learning Plan 🗺️</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Choose your goal and we'll generate a personalized roadmap just for you.</p>
        </div>

        {/* Goal Grid */}
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 4 }}>What do you want to achieve?</h3>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem', marginBottom: 20 }}>Select a career goal — we'll map it to a focused learning path.</p>
          {error && <div className="alert alert-error" style={{ marginBottom: 16 }}>{error}</div>}
          <div className="goals-grid">
            {goals.map((g) => (
              <div
                key={g.goal_id}
                className={`goal-card ${selectedGoal?.goal_id === g.goal_id ? 'selected' : ''}`}
                onClick={() => { setSelectedGoal(g); setError(''); }}
              >
                <div className="goal-emoji">{CATEGORY_EMOJI[g.category] || '🎓'}</div>
                <div className="goal-name">{g.goal_name}</div>
                <div className="goal-category">{g.category}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Preferences */}
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 20 }}>Customize your learning experience</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20 }}>
            <div className="input-group">
              <label>Experience Level</label>
              <select value={experience} onChange={(e) => setExperience(e.target.value)}>
                {EXPERIENCE_OPTS.map((o) => (
                  <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="input-group">
              <label>Learning Style</label>
              <select value={style} onChange={(e) => setStyle(e.target.value)}>
                {STYLE_OPTS.map((o) => (
                  <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="input-group">
              <label>Hours Available Per Week</label>
              <select value={hours} onChange={(e) => setHours(Number(e.target.value))}>
                {HOURS_OPTS.map((h) => (
                  <option key={h} value={h}>{h} hours/week</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {selectedGoal && (
          <div className="alert alert-success" style={{ marginBottom: 16 }}>
            ✓ Selected: <strong>{selectedGoal.goal_name}</strong>
          </div>
        )}

        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={submitting || !selectedGoal}
          style={{ width: '100%', padding: '16px', fontSize: '1rem' }}
        >
          {submitting ? 'Saving...' : (<>Continue to Skill Assessment <FiArrowRight size={18} /></>)}
        </button>
      </div>
    </div>
  );
}
