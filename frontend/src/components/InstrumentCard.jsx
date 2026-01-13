import styles from './InstrumentCard.module.css'
import { getImageUrl } from '../utils/imageUrl'

export default function InstrumentCard({ instrument, onRent }) {
  const imageUrl = getImageUrl(instrument.photo_url)

  return (
    <div className={styles.card}>
      <div className={styles.imageContainer}>
        {imageUrl ? (
          <img src={imageUrl} alt={instrument.name} onError={(e) => {e.target.style.display = 'none'}} />
        ) : (
          <div className={styles.imagePlaceholder}>No Image</div>
        )}
        <div className={styles.overlay}>
          <span className={styles.status}>
            {instrument.status === 'available' ? 'Available' : 'Unavailable'}
          </span>
        </div>
      </div>

      <div className={styles.content}>
        <h3>{instrument.name}</h3>
        <p className={styles.brand}>{instrument.brand}</p>
        
        <div className={styles.details}>
          <span className={styles.type}>{instrument.type}</span>
          <span className={styles.price}>{instrument.price_per_day} TND/day</span>
        </div>

        <p className={styles.description}>
          {instrument.description?.substring(0, 80)}...
        </p>

        <div className={styles.location}>
          {instrument.location_name}
        </div>

        {instrument.tags && instrument.tags.length > 0 && (
          <div className={styles.tags}>
            {instrument.tags.map((tag, i) => (
              <span key={i}>{tag}</span>
            ))}
          </div>
        )}

        <button 
          className={styles.rentBtn}
          onClick={onRent}
          disabled={instrument.status !== 'available'}
        >
          Rent Now
        </button>
      </div>
    </div>
  )
}
