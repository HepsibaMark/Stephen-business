import React, { useEffect, useState } from 'react'
import ProductCard from './components/ProductCard.jsx'
import Cart from './components/Cart.jsx'
import Login from './components/Login.jsx'
import { fetchProducts, createOrder } from './api.js'

export default function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('grocery_user')
    return saved ? JSON.parse(saved) : null
  })
  const [products, setProducts] = useState([])
  const [cartItems, setCartItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isPlacingOrder, setIsPlacingOrder] = useState(false)
  const [orderResult, setOrderResult] = useState(null)
  const [address, setAddress] = useState('')

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleLoggedIn = (loggedInUser, token) => {
    localStorage.setItem('grocery_user', JSON.stringify(loggedInUser))
    localStorage.setItem('grocery_token', token)
    setUser(loggedInUser)
  }

  const handleLogout = () => {
    localStorage.removeItem('grocery_user')
    localStorage.removeItem('grocery_token')
    setUser(null)
  }

  if (!user) {
    return <Login onLoggedIn={handleLoggedIn} />
  }

  const handleAddToCart = (product, quantity, unitType) => {
    const lineTotal = Number(product.price_per_unit) * quantity
    setCartItems((prev) => [...prev, { product, quantity, unitType, lineTotal }])
  }

  const handleRemove = (idx) => {
    setCartItems((prev) => prev.filter((_, i) => i !== idx))
  }

  const handleCheckout = async () => {
    if (!address.trim()) {
      alert('Please enter a delivery address before checking out.')
      return
    }
    setIsPlacingOrder(true)
    setError(null)
    try {
      const payload = {
        customer_id: user.id,
        delivery_address: address,
        payment_method: 'cod',
        items: cartItems.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
          unit_type: item.unitType,
        })),
      }
      const order = await createOrder(payload)
      setOrderResult(order)
      setCartItems([])
    } catch (err) {
      setError(err.message)
    } finally {
      setIsPlacingOrder(false)
    }
  }

  if (orderResult) {
    return (
      <div className="order-success">
        <h1>Order placed! 🎉</h1>
        <p>Order #{orderResult.id}</p>
        <p>Total: ₹{Number(orderResult.total_amount).toFixed(2)}</p>
        <p>Status: {orderResult.status}</p>
        <button onClick={() => setOrderResult(null)}>Place another order</button>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🥬 Grocery Delivery</h1>
        <div className="header-right">
          <span>Hi, {user.name}</span>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="app-body">
        <main className="catalog">
          {loading ? (
            <p>Loading catalog...</p>
          ) : products.length === 0 ? (
            <p>No products yet — add some via the backend's /docs page first.</p>
          ) : (
            <div className="product-grid">
              {products.map((p) => (
                <ProductCard key={p.id} product={p} onAddToCart={handleAddToCart} />
              ))}
            </div>
          )}
        </main>

        <aside className="cart-sidebar">
          <div className="address-field">
            <label htmlFor="address">Delivery address</label>
            <textarea
              id="address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="House no, street, area..."
            />
          </div>
          <Cart
            items={cartItems}
            onRemove={handleRemove}
            onCheckout={handleCheckout}
            isPlacingOrder={isPlacingOrder}
          />
        </aside>
      </div>
    </div>
  )
}
