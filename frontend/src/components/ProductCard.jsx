import React, { useState } from 'react'

// Renders one catalog item. Quantity selection logic differs by unit_type:
// - kg: shows weight buttons (250g/500g/750g/1kg) from product.weight_options
// - piece / kattu: shows a simple +/- counter
export default function ProductCard({ product, onAddToCart }) {
  const isWeightBased = product.unit_type === 'kg'
  const [grams, setGrams] = useState(0)
  const [count, setCount] = useState(0)

  const handleAdd = () => {
    if (isWeightBased) {
      if (grams <= 0) return
      onAddToCart(product, grams / 1000, 'kg')
      setGrams(0)
    } else {
      if (count <= 0) return
      onAddToCart(product, count, product.unit_type)
      setCount(0)
    }
  }

  return (
    <div className="product-card">
      {product.image_url ? (
        <img src={product.image_url} alt={product.name_en} className="product-image" />
      ) : (
        <div className="product-image placeholder" />
      )}

      <div className="product-info">
        <div className="product-name-en">{product.name_en}</div>
        {product.name_ta && <div className="product-name-ta">{product.name_ta}</div>}
        <div className="product-price">
          ₹{Number(product.price_per_unit).toFixed(2)}
          <span className="unit-label"> / {product.unit_type}</span>
        </div>
      </div>

      {isWeightBased ? (
        <div className="weight-options">
          {(product.weight_options?.length
            ? product.weight_options.map((w) => w.grams)
            : [250, 500, 750, 1000]
          ).map((g) => (
            <button
              key={g}
              className={grams === g ? 'weight-btn selected' : 'weight-btn'}
              onClick={() => setGrams(g)}
            >
              {g >= 1000 ? `${g / 1000}kg` : `${g}g`}
            </button>
          ))}
        </div>
      ) : (
        <div className="counter">
          <button onClick={() => setCount((c) => Math.max(0, c - 1))}>−</button>
          <span>{count}</span>
          <button onClick={() => setCount((c) => c + 1)}>+</button>
        </div>
      )}

      <button
        className="add-btn"
        disabled={isWeightBased ? grams <= 0 : count <= 0}
        onClick={handleAdd}
      >
        Add to cart
      </button>
    </div>
  )
}
