import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './Home.css'

const TOPICS = [
  'Machine Learning',
  'Artificial Intelligence',
  'Computer Vision',
  'Natural Language Processing',
  'Deep Learning',
  'Linear Algebra',
  'Statistics & Probability',
  'Data Science',
  'Reinforcement Learning',
  'Neural Networks',
  'Python Programming',
  'Data Structures & Algorithms',
  'Cloud Computing',
  'DevOps & MLOps',
  'Computer Graphics',
]

const FORMATS = [
  { id: 'beginner', icon: '📖', label: 'Beginner', desc: 'Start from the basics' },
  { id: 'intermediate', icon: '📄', label: 'Intermediate', desc: 'Build on prior knowledge' },
  { id: 'advanced', icon: '🗺️', label: 'Advanced', desc: 'Deep dive & mastery' },
]

const NAV_CREATE = [
  { id: 'plan', label: 'Plan' },
  { id: 'course', label: 'Course' },

  { id: 'quiz', label: 'Quiz' },
]

const NAV_LEARNING = [
  { id: 'enrolled', label: 'Currently enrolled plan' },
  { id: 'recommended', label: 'Recommended plans' },
]

export default function Home() {
  const navigate = useNavigate()
  const user = (() => { try { return JSON.parse(localStorage.getItem('user')) } catch { return null } })()

  const [activeNav, setActiveNav] = useState('course')
  const [createOpen, setCreateOpen] = useState(true)
  const [learningOpen, setLearningOpen] = useState(true)
  const [topic, setTopic] = useState('')
  const [format, setFormat] = useState('beginner')
  const [withQuestions, setWithQuestions] = useState(false)
  const [generating, setGenerating] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  const handleGenerate = async () => {
    if (!topic) return
    setGenerating(true)
    // TODO: wire up to backend AI service
    await new Promise((r) => setTimeout(r, 1800))
    setGenerating(false)
    alert(`Generating a ${format} course on "${topic}"! Backend integration coming soon.`)
  }

  return (
    <div className="home-layout">
      {/* ═══════════════════════════════ SIDEBAR ═══════════════════════════════ */}
      <aside className="sidebar">
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="brand-logo">LT</div>
          <div className="brand-info">
            <span className="brand-title">Learning Path Generator</span>
            <span className="brand-subtitle">by Lakshmi &amp; Thirumagal</span>
          </div>
        </div>

        <p className="sidebar-tagline">Your personalized learning companion</p>

        <div className="sidebar-divider" />

        {/* Create with AI */}
        <div className="nav-group">
          <button
            className="nav-group-header"
            onClick={() => setCreateOpen((v) => !v)}
            aria-expanded={createOpen}
          >
            <span>Create with AI</span>
            <span className={`nav-chevron ${createOpen ? 'open' : ''}`}>›</span>
          </button>

          {createOpen && (
            <ul className="nav-list">
              {NAV_CREATE.map((item) => (
                <li key={item.id}>
                  <button
                    className={`nav-item ${activeNav === item.id ? 'active' : ''}`}
                    onClick={() => setActiveNav(item.id)}
                  >
                    <span className="nav-indicator" />
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* My Learning */}
        <div className="nav-group">
          <button
            className="nav-group-header"
            onClick={() => setLearningOpen((v) => !v)}
            aria-expanded={learningOpen}
          >
            <span>My Learning</span>
            <span className={`nav-chevron ${learningOpen ? 'open' : ''}`}>›</span>
          </button>

          {learningOpen && (
            <ul className="nav-list">
              {NAV_LEARNING.map((item) => (
                <li key={item.id}>
                  <button className="nav-item nav-item-icon">
                    <span className="nav-item-emoji">{item.icon}</span>
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* User + Logout at bottom */}
        <div className="sidebar-footer">
          {user && (
            <div className="sidebar-user">
              <div className="user-avatar">{user.username?.[0]?.toUpperCase()}</div>
              <div className="user-info">
                <span className="user-name">{user.username}</span>
                <span className="user-email">{user.email}</span>
              </div>
            </div>
          )}
          <button className="sidebar-logout" onClick={handleLogout} title="Log out">⎋</button>
        </div>
      </aside>

      {/* ═══════════════════════════════ MAIN CONTENT ═══════════════════════════════ */}
      <main className="home-main">
        <div className="home-container">

          {/* Heading */}
          <h1 className="home-heading">What would you like to learn?</h1>
          <p className="home-subheading">
            Select from the topics below what you would like to learn
          </p>

          {/* Topic Input */}
          <div className="home-section">
            <label className="home-label" htmlFor="topic-select">
              What can I help you learn?
            </label>
            <div className="select-wrapper">
              <select
                id="topic-select"
                className="topic-select"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              >
                <option value="" disabled>Select a topic</option>
                {TOPICS.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <span className="select-arrow">▾</span>
            </div>
          </div>

          {/* Format Cards */}
          <div className="home-section">
            <p className="home-label">Choose the format</p>
            <div className="format-grid">
              {FORMATS.map((f) => (
                <button
                  key={f.id}
                  className={`format-card ${format === f.id ? 'selected' : ''}`}
                  onClick={() => setFormat(f.id)}
                  aria-pressed={format === f.id}
                >
                  <span className="format-icon">{f.icon}</span>
                  <span className="format-label">{f.label}</span>
                  <span className="format-desc">{f.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Optional Checkbox */}
          <div className="home-section checkbox-row">
            <label className="checkbox-label">
              <input
                type="checkbox"
                className="checkbox-input"
                checked={withQuestions}
                onChange={(e) => setWithQuestions(e.target.checked)}
                id="with-questions"
              />
              <span className="checkbox-custom" />
              Answer the following questions for a better course
            </label>
          </div>

          {/* Generate Button */}
          <div className="home-section">
            <button
              className="generate-btn"
              onClick={handleGenerate}
              disabled={!topic || generating}
              id="generate-btn"
            >
              {generating ? (
                <>
                  <span className="gen-spinner" />
                  Generating…
                </>
              ) : (
                <>
                  <span className="gen-sparkle">✦</span>
                  Generate
                </>
              )}
            </button>
            {!topic && (
              <p className="generate-hint">Please select a topic above to continue</p>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
