import React, { useState } from 'react'
import { requestOtp, verifyOtp } from '../api.js'

export default function Login({ onLoggedIn }) {
  const [step, setStep] = useState('email') // 'email' | 'otp'
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [debugOtp, setDebugOtp] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleRequestOtp = async () => {
    if (!email.includes('@')) {
      setError('Enter a valid email address')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const res = await requestOtp(email.trim())
      setDebugOtp(res.debug_otp || null) // only present in test mode
      setStep('otp')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async () => {
    if (code.trim().length !== 6) {
      setError('Enter the 6-digit code')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const res = await verifyOtp(
        email.trim(),
        code.trim(),
        name.trim() || undefined,
        phone.trim() || undefined
      )
      onLoggedIn(res.user, res.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>🥬 Grocery Delivery</h1>

        {step === 'email' ? (
          <>
            <label>Email address</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <button disabled={loading} onClick={handleRequestOtp}>
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </>
        ) : (
          <>
            {debugOtp && (
              <div className="test-mode-banner">
                TEST MODE — no real email was sent. Your code is:{' '}
                <strong>{debugOtp}</strong>
              </div>
            )}
            <label>Your name (first time only)</label>
            <input
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <label>Phone number (for delivery contact)</label>
            <input
              type="tel"
              placeholder="9876543210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              maxLength={10}
            />
            <label>Enter OTP</label>
            <input
              type="text"
              placeholder="6-digit code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              maxLength={6}
            />
            <button disabled={loading} onClick={handleVerifyOtp}>
              {loading ? 'Verifying...' : 'Verify & Continue'}
            </button>
            <button className="link-btn" onClick={() => setStep('email')}>
              ← Change email
            </button>
          </>
        )}

        {error && <div className="login-error">{error}</div>}
      </div>
    </div>
  )
}
