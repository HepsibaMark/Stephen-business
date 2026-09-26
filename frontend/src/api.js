// Base URL of your FastAPI backend. Change this if you deploy the backend
// somewhere other than localhost.
const API_BASE = 'https://stephen-business.onrender.com'
export async function fetchProducts() {
  const res = await fetch(`${API_BASE}/products/`)
  if (!res.ok) throw new Error('Failed to load products')
  return res.json()
}

export async function createOrder(orderPayload) {
  const res = await fetch(`${API_BASE}/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderPayload),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to place order')
  }
  return res.json()
}

// ---------- Auth ----------
export async function requestOtp(email) {
  const res = await fetch(`${API_BASE}/auth/request-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  if (!res.ok) throw new Error('Failed to request OTP')
  return res.json() // { message, debug_otp } — debug_otp only present in test mode
}

export async function verifyOtp(email, code, name, phone) {
  const res = await fetch(`${API_BASE}/auth/verify-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code, name, phone }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Invalid or expired OTP')
  }
  return res.json() // { access_token, token_type, user }
}
