import { useState, useEffect } from 'react'
import { rentalsAPI } from '../api'
import { getImageUrl } from '../utils/imageUrl'
import styles from './RentalModal.module.css'

export default function RentalModal({ instrument, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    start_date: '',
    end_date: '',
    proposed_price: '',
    comment: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [totalPrice, setTotalPrice] = useState(0)

  useEffect(() => {
    calculatePrice()
  }, [formData.start_date, formData.end_date])

  const calculatePrice = () => {
    if (formData.start_date && formData.end_date) {
      const start = new Date(formData.start_date)
      const end = new Date(formData.end_date)
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
      const price = Math.max(0, days * instrument.price_per_day)
      setTotalPrice(price)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await rentalsAPI.create({
        instrument_id: instrument.id,
        start_date: formData.start_date,
        end_date: formData.end_date,
        proposed_price: formData.proposed_price ? parseFloat(formData.proposed_price) : null,
        comment: formData.comment
      })
      onSuccess?.()
      onClose()
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create rental')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.modal}>
      <div className={styles.backdrop} onClick={onClose} />
      <div className={styles.content}>
        <button className={styles.close} onClick={onClose}>✕</button>

        <h2>Rent: {instrument.name}</h2>

        <div className={styles.instrumentInfo}>
          {instrument.photo_url && (
            <img src={getImageUrl(instrument.photo_url)} alt={instrument.name} />
          )}
          <div>
            <p><strong>{instrument.brand}</strong></p>
            <p className={styles.price}>{instrument.price_per_day} TND/day</p>
            <p className={styles.location}>📍 {instrument.location_name}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.formGroup}>
            <label>Start Date</label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleChange}
              required
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className={styles.formGroup}>
            <label>End Date</label>
            <input
              type="date"
              name="end_date"
              value={formData.end_date}
              onChange={handleChange}
              required
              min={formData.start_date || new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Proposed Daily Price (Optional)</label>
            <input
              type="number"
              name="proposed_price"
              value={formData.proposed_price}
              onChange={handleChange}
              placeholder="Leave empty to accept asking price"
              step="0.01"
              min="0"
            />
            {formData.proposed_price && (
              <small>Suggested price: {formData.proposed_price} TND/day</small>
            )}
          </div>

          <div className={styles.formGroup}>
            <label>Message to Owner</label>
            <textarea
              name="comment"
              value={formData.comment}
              onChange={handleChange}
              placeholder="Tell the owner why you want to rent this instrument..."
              rows={4}
            />
          </div>

          {totalPrice > 0 && (
            <div className={styles.priceBreakdown}>
              <div className={styles.row}>
                <span>Daily Rate:</span>
                <span>{instrument.price_per_day} TND</span>
              </div>
              <div className={styles.row}>
                <span>Duration:</span>
                <span>
                  {formData.start_date && formData.end_date 
                    ? Math.ceil((new Date(formData.end_date) - new Date(formData.start_date)) / (1000 * 60 * 60 * 24))
                    : 0
                  } days
                </span>
              </div>
              <div className={styles.totalRow}>
                <span>Total:</span>
                <span>{totalPrice.toFixed(2)} TND</span>
              </div>
            </div>
          )}

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? 'Sending Request...' : 'Send Rental Request'}
          </button>
        </form>
      </div>
    </div>
  )
}
