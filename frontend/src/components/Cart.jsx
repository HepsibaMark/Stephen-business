import React from 'react'

export default function Cart({ items, onRemove, onCheckout, isPlacingOrder }) {
  const total = items.reduce((sum, item) => sum + item.lineTotal, 0)

  return (
    <div className="cart">
      <h2>Your Cart</h2>

      {items.length === 0 ? (
        <p className="cart-empty">No items yet — add something from the catalog.</p>
      ) : (
        <>
          <ul className="cart-list">
            {items.map((item, idx) => (
              <li key={idx} className="cart-item">
                <div>
                  <div className="cart-item-name">{item.product.name_en}</div>
                  <div className="cart-item-qty">
                    {item.unitType === 'kg'
                      ? `${item.quantity * 1000}g`
                      : `${item.quantity} ${item.unitType}`}
                  </div>
                </div>
                <div className="cart-item-price">₹{item.lineTotal.toFixed(2)}</div>
                <button className="remove-btn" onClick={() => onRemove(idx)}>
                  ✕
                </button>
              </li>
            ))}
          </ul>

          <div className="cart-total">
            <span>Total</span>
            <span>₹{total.toFixed(2)}</span>
          </div>

          <button
            className="checkout-btn"
            onClick={onCheckout}
            disabled={isPlacingOrder}
          >
            {isPlacingOrder ? 'Placing order...' : 'Checkout'}
          </button>
        </>
      )}
    </div>
  )
}
