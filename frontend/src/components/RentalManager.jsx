import { useState, useEffect } from 'react'
import { rentalsAPI } from '../api'
import styles from './RentalManager.module.css'

export default function RentalManager({ user }) {
  const [rentals, setRentals] = useState([])
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('all')
  const [selectedRental, setSelectedRental] = useState(null)
  const [counterOffer, setCounterOffer] = useState('')

  // Determine if viewing as owner or renter
  const isOwner = user?.role === 'owner'

  useEffect(() => {
    fetchRentals()
  }, [tab])

  const fetchRentals = async () => {
    setLoading(true)
    try {
      const response = await rentalsAPI.getAll({
        limit: 50
      })
      let filtered = response.data

      if (isOwner) {
        // Show incoming rental requests (where user is the owner)
        filtered = filtered.filter(r => r.owner_id === user?.id)
      } else {
        // Show sent rental requests (where user is the renter)
        filtered = filtered.filter(r => r.renter_id === user?.id)
      }

      if (tab === 'pending') {
        filtered = filtered.filter(r => r.owner_response === 'pending')
      } else if (tab === 'confirmed') {
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
      console.error('Error sending counter-offer:', error)
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
        <h2>{isOwner ? 'Rental Requests' : 'My Rentals'}</h2>
        <p>
          {isOwner
            ? 'Manage incoming rental requests for your instruments'
            : 'View your rental requests and negotiations'}
        </p>
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
                      <span>Negotiated Price:</span>
                      <span className={styles.negotiated}>
                        {rental.negotiated_price.toFixed(2)} TND
                      </span>
                    </div>
                  )}
                </div>

                {isOwner ? (
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
                  // Renter view: show status only, no action buttons
                  <div className={styles.renterStatus}>
                    <p>
                      <strong>Status:</strong>{' '}
                      <span className={`${styles.statusBadge} ${styles[rental.owner_response]}`}>
                        {rental.owner_response === 'pending'
                          ? 'Waiting for response'
                          : rental.owner_response === 'accepted'
                          ? 'Accepted'
                          : 'Rejected'}
                      </span>
                    </p>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className={styles.empty}>
              {isOwner
                ? 'No rental requests yet. List more instruments to receive requests!'
                : 'No rental requests yet. Start by renting an instrument!'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
