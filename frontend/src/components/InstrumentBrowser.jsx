import { useState, useEffect } from 'react'
import { instrumentsAPI } from '../api'
import InstrumentCard from './InstrumentCard'
import styles from './InstrumentBrowser.module.css'

const SORT_OPTIONS = [
  { value: 'price_asc', label: 'Price (Low to High)', sortBy: 'price_per_day', order: 'asc' },
  { value: 'price_desc', label: 'Price (High to Low)', sortBy: 'price_per_day', order: 'desc' },
  { value: 'newest', label: 'Newest First', sortBy: 'newest', order: 'desc' },
  { value: 'distance', label: 'Closest to Me', sortBy: 'distance', order: 'asc' },
  { value: 'owner_id', label: 'By Owner', sortBy: 'owner_id', order: 'asc' }
]

export default function InstrumentBrowser({ user, onRentClick }) {
  const [instruments, setInstruments] = useState([])
  const [loading, setLoading] = useState(false)
  const [sortValue, setSortValue] = useState('distance')
  const [priceRange, setPriceRange] = useState([0, 100])
  const [selectedType, setSelectedType] = useState('')

  useEffect(() => {
    fetchInstruments()
  }, [sortValue, priceRange, selectedType])

  const fetchInstruments = async () => {
    setLoading(true)
    try {
      const selected = SORT_OPTIONS.find(opt => opt.value === sortValue)
      const params = {
        sort_by: selected.sortBy,
        sort_order: selected.order,
        price_min: priceRange[0],
        price_max: priceRange[1],
        type: selectedType || undefined,
        limit: 20
      }
      
      // Add user location for distance sorting
      if (user?.location_lat && user?.location_lng) {
        params.user_lat = user.location_lat
        params.user_lng = user.location_lng
      }
      
      const response = await instrumentsAPI.getAll(params)
      setInstruments(response.data)
    } catch (error) {
      console.error('Error fetching instruments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSortChange = (e) => {
    setSortValue(e.target.value)
  }

  return (
    <div className={styles.browser}>
      <div className={styles.header}>
        <h2>Browse Instruments</h2>
        <p>Find the perfect instrument for your next jam session</p>
      </div>

      <div className={styles.filters}>
        <div className={styles.filterGroup}>
          <label>Sort By</label>
          <select value={sortValue} onChange={handleSortChange}>
            {SORT_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label>Price Range: {priceRange[0]} - {priceRange[1]} TND</label>
          <input
            type="range"
            min="0"
            max="100"
            value={priceRange[1]}
            onChange={(e) => setPriceRange([0, parseInt(e.target.value)])}
            className={styles.slider}
          />
        </div>

        <div className={styles.filterGroup}>
          <label>Instrument Type</label>
          <input
            type="text"
            placeholder="e.g., Guitar, Piano..."
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className={styles.input}
          />
        </div>
      </div>

      {loading ? (
        <div className={styles.loading}>Loading instruments...</div>
      ) : (
        <div className={styles.grid}>
          {instruments.length > 0 ? (
            instruments.map(instrument => (
              <InstrumentCard
                key={instrument.id}
                instrument={instrument}
                onRent={() => onRentClick(instrument)}
              />
            ))
          ) : (
            <div className={styles.empty}>No instruments found</div>
          )}
        </div>
      )}
    </div>
  )
}
