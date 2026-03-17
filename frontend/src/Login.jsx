import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

export default function Login() {
    const navigate = useNavigate()

    const [form, setForm] = useState({ email: '', password: '' })
    const [errors, setErrors] = useState({})
    const [apiError, setApiError] = useState('')
    const [apiSuccess, setApiSuccess] = useState('')
    const [loading, setLoading] = useState(false)
    const [showPassword, setShowPassword] = useState(false)

    const handleChange = (e) => {
        const { name, value } = e.target
        setForm((prev) => ({ ...prev, [name]: value }))
        setErrors((prev) => ({ ...prev, [name]: '' }))
        setApiError('')
    }

    const validate = () => {
        const errs = {}
        if (!form.email.trim()) errs.email = 'Email is required.'
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
            errs.email = 'Enter a valid email address.'
        if (!form.password) errs.password = 'Password is required.'
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
            const { data } = await axios.post(`${API_BASE}/login`, {
                email: form.email.trim(),
                password: form.password,
            })

            // Persist token and user info
            localStorage.setItem('access_token', data.access_token)
            localStorage.setItem('user', JSON.stringify(data.user))

            setApiSuccess(`Welcome back, ${data.user.username}! Redirecting…`)
            setTimeout(() => navigate('/home'), 2000)
        } catch (err) {
            const detail = err.response?.data?.detail
            if (Array.isArray(detail)) {
                setApiError(detail.map((d) => d.msg).join(' '))
            } else {
                setApiError(detail || 'Login failed. Please check your credentials.')
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

                <h1 className="auth-title">Welcome back</h1>
                <p className="auth-subtitle">Sign in to continue your learning journey.</p>

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
                    {/* Email */}
                    <div className="form-group">
                        <label className="form-label" htmlFor="login-email">Email Address</label>
                        <div className="input-wrapper">
                            <input
                                id="login-email"
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
                        <label className="form-label" htmlFor="login-password">Password</label>
                        <div className="input-wrapper">
                            <input
                                id="login-password"
                                className={`form-input${errors.password ? ' input-error' : ''}`}
                                type={showPassword ? 'text' : 'password'}
                                name="password"
                                placeholder="Enter your password"
                                value={form.password}
                                onChange={handleChange}
                                autoComplete="current-password"
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
                        {errors.password && <p className="field-error">⚠ {errors.password}</p>}
                    </div>

                    <button
                        type="submit"
                        className="btn-primary"
                        disabled={loading}
                        id="login-submit-btn"
                    >
                        {loading ? (
                            <>
                                <span className="spinner" /> Signing in…
                            </>
                        ) : (
                            'Sign In →'
                        )}
                    </button>
                </form>

                <div className="auth-divider" />

                <p className="auth-footer">
                    Don't have an account?{' '}
                    <Link to="/register" className="auth-link">
                        Create one
                    </Link>
                </p>
            </div>
        </div>
    )
}
