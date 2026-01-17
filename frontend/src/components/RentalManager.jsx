import { useState, useEffect } from 'react'
import { rentalsAPI } from '../api'
import styles from './RentalManager.module.css'

export default function RentalManager({ user }) {
  const [rentals, setRentals] = useState([])
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('all')
  const [selectedRental, setSelectedRental] = useState(null)
  const [counterOffer, setCounterOffer] = useState('')

  useEffect(() => {
    fetchRentals()
  }, [tab])

  const fetchRentals = async () => {
    setLoading(true)
    try {
      const response = await rentalsAPI.getAll({
        limit: 50
      })
      // Show all rentals where user is either owner or renter
      let filtered = response.data.filter(
        r => r.owner_id === user?.id || r.renter_id === user?.id
      )

      if (tab === 'pending') {
        // Show pending and counter_offer status (active negotiations)
        filtered = filtered.filter(r => r.owner_response === 'pending' || r.owner_response === 'counter_offer')
      } else if (tab === 'confirmed') {
        // Show confirmed rentals
        filtered = filtered.filter(r => r.status === 'confirmed')
      }

      setRentals(filtered)
    } catch (error) {
      console.error('Error fetching rentals:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCounterOffer = async (rentalId) => {
    try {
      await rentalsAPI.counterOffer(rentalId, {
        negotiated_price: parseFloat(counterOffer)
      })
      setCounterOffer('')
      setSelectedRental(null)
      fetchRentals()
    } catch (error) {
      console.error('Error sending counter-offer:', error?.response?.data || error?.message || error)
      alert(`Failed to send counter-offer: ${error?.response?.data?.message || error?.message}`)
    }
  }

  const handleAccept = async (rentalId) => {
    try {
      await rentalsAPI.accept(rentalId)
      fetchRentals()
    } catch (error) {
      console.error('Error accepting rental:', error)
    }
  }

  const handleReject = async (rentalId) => {
    try {
      await rentalsAPI.reject(rentalId)
      fetchRentals()
    } catch (error) {
      console.error('Error rejecting rental:', error)
    }
  }

  return (
    <div className={styles.manager}>
      <div className={styles.header}>
        <h2>Rentals & Negotiations</h2>
        <p>Manage your rental requests and price negotiations</p>
      </div>

      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${tab === 'all' ? styles.active : ''}`}
          onClick={() => setTab('all')}
        >
          All Rentals
        </button>
        <button
          className={`${styles.tab} ${tab === 'pending' ? styles.active : ''}`}
          onClick={() => setTab('pending')}
        >
          Pending
        </button>
        <button
          className={`${styles.tab} ${tab === 'confirmed' ? styles.active : ''}`}
          onClick={() => setTab('confirmed')}
        >
          Confirmed
        </button>
      </div>

      {loading ? (
        <div className={styles.loading}>Loading rentals...</div>
      ) : (
        <div className={styles.list}>
          {rentals.length > 0 ? (
            rentals.map(rental => (
              <div key={rental.id} className={styles.rentalCard}>
                <div className={styles.cardHeader}>
                  <div className={styles.info}>
                    <h3>{rental.instrument_name}</h3>
                    <p className={styles.dates}>
                      {rental.start_date} to {rental.end_date}
                    </p>
                  </div>
                  <span className={`${styles.status} ${styles[rental.status]}`}>
                    {rental.status.toUpperCase()}
                  </span>
                </div>

                {rental.comment && (
                  <div className={styles.comment}>
                    <p><strong>Message:</strong> {rental.comment}</p>
                  </div>
                )}

                <div className={styles.priceInfo}>
                  <div className={styles.priceRow}>
                    <span>Original Price:</span>
                    <span>{rental.total_price.toFixed(2)} TND</span>
                  </div>
                  {rental.negotiated_price && (
                    <div className={styles.priceRow}>
                      <span>
                        {rental.owner_response === 'counter_offer' ? '💰 Negotiated Price:' : 'Negotiated Price:'}
                      </span>
                      <span className={styles.negotiated}>
                        {rental.negotiated_price.toFixed(2)} TND
                        {rental.owner_response === 'counter_offer' && rental.owner_id === user?.id && (
                          <span style={{ marginLeft: '8px', fontSize: '0.9em', color: '#ff9800' }}>
                            (waiting for your response)
                          </span>
                        )}
                      </span>
                    </div>
                  )}
                </div>

                {rental.owner_id === user?.id ? (
                  // Owner view: show action buttons for incoming requests
                  <>
                    {rental.owner_response === 'pending' && (
                      <div className={styles.actions}>
                        <button
                          className={styles.acceptBtn}
                          onClick={() => handleAccept(rental.id)}
                        >
                          Accept
                        </button>
                        <button
                          className={styles.counterBtn}
                          onClick={() => setSelectedRental(rental.id)}
                        >
                          Counter Offer
                        </button>
                        <button
                          className={styles.rejectBtn}
                          onClick={() => handleReject(rental.id)}
                        >
                          Reject
                        </button>
                      </div>
                    )}

                    {rental.owner_response === 'counter_offer' && (
                      <div className={styles.actions}>
                        <button
                          className={styles.acceptBtn}
                          onClick={() => handleAccept(rental.id)}
                        >
                          Accept Offer
                        </button>
                        <button
                          className={styles.counterBtn}
                          onClick={() => setSelectedRental(rental.id)}
                        >
                          Make Counter Offer
                        </button>
                        <button
                          className={styles.rejectBtn}
                          onClick={() => handleReject(rental.id)}
                        >
                          Reject
                        </button>
                      </div>
                    )}

                    {selectedRental === rental.id && (
                      <div className={styles.counterOfferForm}>
                        <input
                          type="number"
                          placeholder="New price (TND)"
                          value={counterOffer}
                          onChange={(e) => setCounterOffer(e.target.value)}
                          min="0"
                          step="0.01"
                        />
                        <button
                          onClick={() => handleCounterOffer(rental.id)}
                          className={styles.sendBtn}
                        >
                          Send Offer
                        </button>
                        <button
                          onClick={() => {
                            setSelectedRental(null)
                            setCounterOffer('')
                          }}
                          className={styles.cancelBtn}
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  // Renter view: show status and counter-offer option
                  <div className={styles.renterSection}>
                    <div className={styles.renterStatus}>
                      <p>
                        <strong>Status:</strong>{' '}
                        <span className={`${styles.statusBadge} ${styles[rental.owner_response]}`}>
                          {rental.owner_response === 'pending'
                            ? 'Waiting for response'
                            : rental.owner_response === 'accepted'
                            ? 'Accepted'
                            : rental.owner_response === 'counter_offer'
                            ? 'Counter Offer'
                            : 'Rejected'}
                        </span>
                      </p>
                    </div>

                    {rental.owner_response === 'pending' && (
                      <div className={styles.actions}>
                        <button
                          className={styles.counterBtn}
                          onClick={() => setSelectedRental(rental.id)}
                        >
                          Counter Offer
                        </button>
                      </div>
                    )}

                    {rental.owner_response === 'counter_offer' && (
                      <div className={styles.actions}>
                        <button
                          className={styles.acceptBtn}
                          onClick={() => handleAccept(rental.id)}
                        >
                          Accept Counter
                        </button>
                        <button
                          className={styles.counterBtn}
                          onClick={() => setSelectedRental(rental.id)}
                        >
                          Make Counter Offer
                        </button>
                        <button
                          className={styles.rejectBtn}
                          onClick={() => handleReject(rental.id)}
                        >
                          Reject
                        </button>
                      </div>
                    )}

                    {selectedRental === rental.id && (
                      <div className={styles.counterOfferForm}>
                        <input
                          type="number"
                          placeholder="New price (TND)"
                          value={counterOffer}
                          onChange={(e) => setCounterOffer(e.target.value)}
                          min="0"
                          step="0.01"
                        />
                        <button
                          onClick={() => handleCounterOffer(rental.id)}
                          className={styles.sendBtn}
                        >
                          Send Offer
                        </button>
                        <button
                          onClick={() => {
                            setSelectedRental(null)
                            setCounterOffer('')
                          }}
                          className={styles.cancelBtn}
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className={styles.empty}>
              No rental requests yet.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
