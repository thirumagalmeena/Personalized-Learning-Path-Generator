import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import './ResultPage.css'

// ─── Helpers ─────────────────────────────────────────────────────
function getYouTubeEmbedUrl(url) {
  if (!url) return null
  try {
    const u = new URL(url)
    if (u.hostname.includes('youtube.com')) {
      const v = u.searchParams.get('v')
      return v ? `https://www.youtube.com/embed/${v}?rel=0` : null
    }
    if (u.hostname === 'youtu.be') {
      return `https://www.youtube.com/embed${u.pathname}?rel=0`
    }
  } catch { /* not a URL */ }
  return null
}

const DIFFICULTY_META = {
  Beginner: { label: 'Beginner', cls: 'diff-beginner' },
  Intermediate: { label: 'Intermediate', cls: 'diff-intermediate' },
  Advanced: { label: 'Advanced', cls: 'diff-advanced' },
}

// ─── Resource Cards ───────────────────────────────────────────────
function VideoResource({ title, url }) {
  const embed = getYouTubeEmbedUrl(url)
  if (embed) {
    return (
      <div className="resource-video">
        <p className="resource-label">🎬 {title}</p>
        <div className="video-wrapper">
          <iframe
            src={embed}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </div>
    )
  }
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="resource-btn resource-btn-video">
      Watch Video
    </a>
  )
}

function BookResource({ title, estimatedTime, url }) {
  return (
    <div className="resource-book">
      <div className="book-cover">
        <span className="book-icon">📘</span>
      </div>
      <div className="book-info">
        <p className="book-title">{title}</p>
        {estimatedTime && (
          <p className="book-time">⏱ ~{estimatedTime} hours</p>
        )}
        <a href={url} target="_blank" rel="noopener noreferrer" className="resource-btn resource-btn-book">
          Read Book →
        </a>
      </div>
    </div>
  )
}

function ArticleResource({ title, url }) {
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="resource-link">
      📄 {title} <span className="link-arrow">→</span>
    </a>
  )
}

function CourseResource({ title, url }) {
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="resource-btn resource-btn-course">
      Start Course: {title}
    </a>
  )
}

function ResourceCard({ type, title, url, estimatedTime }) {
  const t = (type || '').toLowerCase()
  if (t === 'video') return <VideoResource title={title} url={url} />
  if (t === 'book') return <BookResource title={title} url={url} estimatedTime={estimatedTime} />
  if (t === 'article') return <ArticleResource title={title} url={url} />
  if (t === 'course') return <CourseResource title={title} url={url} />
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="resource-btn resource-btn-default">
      🔗 {title}
    </a>
  )
}

// ─── Step Card ────────────────────────────────────────────────────
function StepCard({ step, index, isLast }) {
  const [completed, setCompleted] = useState(false)
  const diff = DIFFICULTY_META[step.difficulty] || { label: step.difficulty || '—', cls: 'diff-default' }

  return (
    <div className="timeline-item" style={{ animationDelay: `${index * 0.1}s` }}>
      {/* Connector */}
      <div className="timeline-connector">
        <div className={`timeline-dot ${completed ? 'done' : ''}`}>
          {completed ? '✓' : step.step_number}
        </div>
        {!isLast && <div className="timeline-line" />}
      </div>

      {/* Card */}
      <div className={`step-card ${completed ? 'step-card-done' : ''}`}>
        <div className="step-card-header">
          <div className="step-card-title-row">
            <h3 className="step-skill-title">{step.skill}</h3>
            <span className={`diff-badge ${diff.cls}`}>{diff.label}</span>
          </div>
          <div className="step-card-meta">
            {step.estimated_learning_hours && (
              <span className="meta-chip">⏱ {step.estimated_learning_hours}h to learn</span>
            )}
            {step.resource_type && (
              <span className="meta-chip meta-chip-type">
                {step.resource_type}
              </span>
            )}
          </div>
        </div>

        {/* Resource */}
        {step.resource_title && (
          <div className="step-card-resource">
            <ResourceCard
              type={step.resource_type}
              title={step.resource_title}
              url={step.url}
              estimatedTime={step.estimated_time}
            />
          </div>
        )}

        {/* Mark complete */}
        <label className="complete-toggle">
          <input
            type="checkbox"
            checked={completed}
            onChange={(e) => setCompleted(e.target.checked)}
          />
          <span className="complete-toggle-box" />
          <span className="complete-toggle-label">Mark as completed</span>
        </label>
      </div>
    </div>
  )
}

// ─── Main Result Page ─────────────────────────────────────────────
export default function ResultPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    // Trigger fade-in after mount
    const t = setTimeout(() => setVisible(true), 80)
    return () => clearTimeout(t)
  }, [])

  if (!state?.result) {
    return (
      <div className="result-empty">
        <p>No learning path found.</p>
        <button className="btn-back" onClick={() => navigate('/home')}>← Back to Generator</button>
      </div>
    )
  }

  const { result } = state
  const steps = result.learning_path || []
  const totalHours = steps.reduce((sum, s) => sum + (s.estimated_learning_hours || 0), 0)
  const completedCount = 0 // could be stateful

  return (
    <div className={`result-page ${visible ? 'result-visible' : ''}`}>

      {/* ── Sidebar (same brand strip) ── */}
      <aside className="result-sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">LT</div>
          <div className="brand-info">
            <span className="brand-title">Learning Path Generator</span>
            <span className="brand-subtitle">by Lakshmi &amp; Thirumagal</span>
          </div>
        </div>
        <p className="sidebar-tagline">Your personalized learning companion</p>
        <div className="sidebar-divider" />
        <button className="btn-back-sidebar" onClick={() => navigate('/home')}>
          ← Generate New Path
        </button>
      </aside>

      {/* ── Main ── */}
      <main className="result-main">
        <div className="result-container">

          {/* Header */}
          <div className="result-header">
            <div>
              <h1 className="result-goal-title">{result.goal}</h1>
              <div className="result-stats">
                <span className="result-stat">
                  {result.total_steps ?? steps.length} Steps
                </span>
                {totalHours > 0 && (
                  <span className="result-stat">
                    <span className="stat-icon">⏱</span>
                    ~{totalHours} Hours
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Progress bar */}
          {steps.length > 0 && (
            <div className="progress-bar-wrap">
              <div className="progress-bar-track">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${(completedCount / steps.length) * 100}%` }}
                />
              </div>
              <span className="progress-label">{completedCount}/{steps.length} completed</span>
            </div>
          )}

          {/* Timeline */}
          {steps.length === 0 ? (
            <div className="result-empty-state">
              <p> You already know all the skills for this goal!!</p>
              <button className="btn-back" onClick={() => navigate('/home')}>← Try Another Goal</button>
            </div>
          ) : (
            <div className="timeline">
              {steps.map((step, i) => (
                <StepCard
                  key={step.step_number}
                  step={step}
                  index={i}
                  isLast={i === steps.length - 1}
                />
              ))}
            </div>
          )}

        </div>
      </main>
    </div>
  )
}
