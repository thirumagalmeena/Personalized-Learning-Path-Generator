import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

// Password requirement definitions
const REQUIREMENTS = [
    { id: 'length', label: 'At least 8 characters', test: (p) => p.length >= 8 },
    { id: 'uppercase', label: 'At least 1 uppercase letter', test: (p) => /[A-Z]/.test(p) },
    { id: 'lowercase', label: 'At least 1 lowercase letter', test: (p) => /[a-z]/.test(p) },
    { id: 'number', label: 'At least 1 number', test: (p) => /\d/.test(p) },
    { id: 'special', label: 'At least 1 special character', test: (p) => /[!@#$%^&*(),.?":{}|<>_\-]/.test(p) },
]

function getStrength(password) {
    const metCount = REQUIREMENTS.filter((r) => r.test(password)).length
    if (metCount <= 1) return { score: 1, label: 'Weak', className: 'weak' }
    if (metCount === 2) return { score: 2, label: 'Fair', className: 'fair' }
    if (metCount === 3) return { score: 3, label: 'Good', className: 'good' }
    if (metCount === 4) return { score: 4, label: 'Strong', className: 'good' }
    return { score: 5, label: 'Strong', className: 'strong' }
}

export default function Register() {
    const navigate = useNavigate()

    const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' })
    const [errors, setErrors] = useState({})
    const [apiError, setApiError] = useState('')
    const [apiSuccess, setApiSuccess] = useState('')
    const [loading, setLoading] = useState(false)
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirm, setShowConfirm] = useState(false)

    const strength = form.password ? getStrength(form.password) : null

    const handleChange = (e) => {
        const { name, value } = e.target
        setForm((prev) => ({ ...prev, [name]: value }))
        // Clear field error on change
        setErrors((prev) => ({ ...prev, [name]: '' }))
        setApiError('')
    }

    const validate = () => {
        const errs = {}
        if (!form.username.trim()) errs.username = 'Username is required.'
        else if (form.username.trim().length < 3) errs.username = 'Username must be at least 3 characters.'

        if (!form.email.trim()) errs.email = 'Email is required.'
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Enter a valid email address.'

        if (!form.password) errs.password = 'Password is required.'
        else {
            const unmetReqs = REQUIREMENTS.filter((r) => !r.test(form.password))
            if (unmetReqs.length > 0) errs.password = `Password doesn't meet all requirements.`
        }

        if (!form.confirmPassword) errs.confirmPassword = 'Please confirm your password.'
        else if (form.password !== form.confirmPassword) errs.confirmPassword = 'Passwords do not match.'

        return errs
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        const errs = validate()
        if (Object.keys(errs).length > 0) {
            setErrors(errs)
            return
        }

        setLoading(true)
        setApiError('')
        setApiSuccess('')

        try {
            await axios.post(`${API_BASE}/register`, {
                username: form.username.trim(),
                email: form.email.trim(),
                password: form.password,
            })
            setApiSuccess('Account created successfully! Redirecting to login…')
            setTimeout(() => navigate('/login'), 2000)
        } catch (err) {
            const detail = err.response?.data?.detail
            if (Array.isArray(detail)) {
                setApiError(detail.map((d) => d.msg).join(' '))
            } else {
                setApiError(detail || 'Registration failed. Please try again.')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                {/* Branding */}
                <div className="auth-logo">
                    <span className="auth-logo-text">Learning Path Generator</span>
                </div>

                <h1 className="auth-title">Create account</h1>
                <p className="auth-subtitle">Start your personalized learning journey today.</p>

                {/* API Banners */}
                {apiError && (
                    <div className="alert alert-error" role="alert">
                        <span></span> {apiError}
                    </div>
                )}
                {apiSuccess && (
                    <div className="alert alert-success" role="alert">
                        <span></span> {apiSuccess}
                    </div>
                )}

                <form onSubmit={handleSubmit} noValidate>
                    {/* Username */}
                    <div className="form-group">
                        <label className="form-label" htmlFor="reg-username">Username</label>
                        <div className="input-wrapper">
                            <input
                                id="reg-username"
                                className={`form-input${errors.username ? ' input-error' : ''}`}
                                type="text"
                                name="username"
                                placeholder="johndoe"
                                value={form.username}
                                onChange={handleChange}
                                autoComplete="username"
                                required
                            />
                        </div>
                        {errors.username && <p className="field-error">⚠ {errors.username}</p>}
                    </div>

                    {/* Email */}
                    <div className="form-group">
                        <label className="form-label" htmlFor="reg-email">Email Address</label>
                        <div className="input-wrapper">
                            <input
                                id="reg-email"
                                className={`form-input${errors.email ? ' input-error' : ''}`}
                                type="email"
                                name="email"
                                placeholder="you@example.com"
                                value={form.email}
                                onChange={handleChange}
                                autoComplete="email"
                                required
                            />
                        </div>
                        {errors.email && <p className="field-error">⚠ {errors.email}</p>}
                    </div>

                    {/* Password */}
                    <div className="form-group">
                        <label className="form-label" htmlFor="reg-password">Password</label>
                        <div className="input-wrapper">
                            <input
                                id="reg-password"
                                className={`form-input${errors.password ? ' input-error' : ''}`}
                                type={showPassword ? 'text' : 'password'}
                                name="password"
                                placeholder="Create a strong password"
                                value={form.password}
                                onChange={handleChange}
                                autoComplete="new-password"
                                required
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowPassword((v) => !v)}
                                aria-label={showPassword ? 'Hide password' : 'Show password'}
                            >
                                {showPassword ? '🙈' : '👁️'}
                            </button>
                        </div>

                        {/* Strength bar */}
                        {form.password && strength && (
                            <div className="strength-bar-wrapper">
                                <div className="strength-bars" role="progressbar" aria-label="Password strength">
                                    {[1, 2, 3, 4, 5].map((seg) => (
                                        <div
                                            key={seg}
                                            className={`strength-bar-segment${strength.score >= seg ? ` filled-${strength.className}` : ''
                                                }`}
                                        />
                                    ))}
                                </div>
                                <span className={`strength-label ${strength.className}`}>
                                    {strength.label}
                                </span>
                            </div>
                        )}

                        {/* Requirements checklist */}
                        {form.password && (
                            <ul className="password-requirements" aria-label="Password requirements">
                                {REQUIREMENTS.map((req) => {
                                    const met = req.test(form.password)
                                    return (
                                        <li key={req.id} className={`req-item${met ? ' met' : ''}`}>
                                            <span className="req-dot" />
                                            {req.label}
                                        </li>
                                    )
                                })}
                            </ul>
                        )}
                        {errors.password && <p className="field-error">⚠ {errors.password}</p>}
                    </div>

                    {/* Confirm Password */}
                    <div className="form-group">
                        <label className="form-label" htmlFor="reg-confirm">Confirm Password</label>
                        <div className="input-wrapper">
                            <input
                                id="reg-confirm"
                                className={`form-input${errors.confirmPassword ? ' input-error' : ''}`}
                                type={showConfirm ? 'text' : 'password'}
                                name="confirmPassword"
                                placeholder="Repeat your password"
                                value={form.confirmPassword}
                                onChange={handleChange}
                                autoComplete="new-password"
                                required
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowConfirm((v) => !v)}
                                aria-label={showConfirm ? 'Hide confirm password' : 'Show confirm password'}
                            >
                                {showConfirm ? '🙈' : '👁️'}
                            </button>
                        </div>
                        {errors.confirmPassword && <p className="field-error">⚠ {errors.confirmPassword}</p>}
                    </div>

                    <button type="submit" className="btn-primary" disabled={loading} id="register-submit-btn">
                        {loading ? (
                            <>
                                <span className="spinner" /> Creating account…
                            </>
                        ) : (
                            'Create Account →'
                        )}
                    </button>
                </form>

                <div className="auth-divider" />

                <p className="auth-footer">
                    Already have an account?{' '}
                    <Link to="/login" className="auth-link">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    )
}
