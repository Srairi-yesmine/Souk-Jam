import { useState, useEffect } from 'react'
import { jamAPI } from '../api'
import { getImageUrl } from '../utils/imageUrl'
import styles from './JamDiscovery.module.css'

export default function JamDiscovery() {
  const [musicians, setMusicians] = useState([])
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('discover')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (tab === 'discover') {
      fetchMusicians()
    } else {
      fetchMatches()
    }
  }, [tab])

  const fetchMusicians = async () => {
    setLoading(true)
    try {
      const response = await jamAPI.discover(50)
      setMusicians(response.data || [])
      setCurrentIndex(0)
    } catch (error) {
      console.error('Error fetching musicians:', error)
      setMusicians([])
    } finally {
      setLoading(false)
    }
  }

  const fetchMatches = async () => {
    setLoading(true)
    try {
      const response = await jamAPI.getMatches()
      setMatches(response.data || [])
    } catch (error) {
      console.error('Error fetching matches:', error)
      setMatches([])
    } finally {
      setLoading(false)
    }
  }

  const handleSendRequest = async () => {
    if (musicians.length === 0 || currentIndex >= musicians.length) {
      console.warn('No musician available at current index')
      return
    }
    const musician = musicians[currentIndex]
    if (!musician || !musician.id) {
      console.error('Invalid musician data:', musician)
      return
    }
    try {
      console.log('Sending jam request to musician ID:', musician.id, 'Musician data:', musician)
      const response = await jamAPI.sendRequest(musician.id)
      console.log('Request sent successfully:', response)
      alert('Jam request sent successfully!')
      handleNextCard()
    } catch (error) {
      console.error('Error sending request:', error.response?.data || error.message)
      alert(`Failed to send jam request: ${error.response?.data?.message || error.message}. Please try again.`)
    }
  }

  const handleSkipUser = async () => {
    if (musicians.length === 0) return
    const musician = musicians[currentIndex]
    try {
      await jamAPI.skipUser(musician.id)
      handleNextCard()
    } catch (error) {
      console.error('Error skipping user:', error)
    }
  }

  const handleNextCard = () => {
    setCurrentIndex(prev => prev + 1)
  }

  const currentMusician = musicians.length > 0 ? musicians[currentIndex] : null

  return (
    <div className={styles.discovery}>
      <div className={styles.header}>
        <h2>Find Musicians to Jam With</h2>
        <p>Swipe right to send a jam request, left to skip</p>
      </div>

      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${tab === 'discover' ? styles.active : ''}`}
          onClick={() => setTab('discover')}
        >
          Discover Musicians
        </button>
        <button
          className={`${styles.tab} ${tab === 'matches' ? styles.active : ''}`}
          onClick={() => setTab('matches')}
        >
          Mutual Matches
        </button>
      </div>

      {loading ? (
        <div className={styles.loading}>Loading...</div>
      ) : tab === 'discover' ? (
        <div className={styles.swipeContainer}>
          {currentMusician ? (
            <div className={styles.swipeCard}>
              <div className={styles.cardContent}>
                <div className={styles.avatar}>
                  {currentMusician.profile_photo_url ? (
                    <img 
                      src={getImageUrl(currentMusician.profile_photo_url)}
                      alt={currentMusician.name} 
                      onError={(e) => {e.target.style.display = 'none'}}
                    />
                  ) : (
                    <div className={styles.placeholder}>
                      {currentMusician.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>

                <div className={styles.info}>
                  <h2>{currentMusician.name}</h2>
                  <p className={styles.location}>{currentMusician.location_name}</p>

                  <div className={styles.genres}>
                    <strong>Genres:</strong>
                    <div className={styles.tags}>
                      {currentMusician.genres_enjoyed?.slice(0, 4).map((genre, i) => (
                        <span key={i} className={styles.tag}>{genre}</span>
                      ))}
                    </div>
                  </div>

                  <div className={styles.instruments}>
                    <strong>Plays:</strong>
                    <div className={styles.tags}>
                      {currentMusician.instruments_played?.slice(0, 4).map((inst, i) => (
                        <span key={i} className={styles.tag}>
                          {typeof inst === 'string' ? inst : inst.instrument_type}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className={styles.cardActions}>
                <button
                  className={styles.skipBtn}
                  onClick={handleSkipUser}
                  title="Skip (← Left)"
                >
                  ← Skip
                </button>
                <span className={styles.counter}>{currentIndex + 1} / {musicians.length}</span>
                <button
                  className={styles.jamBtn}
                  onClick={handleSendRequest}
                  title="Send Request (→ Right)"
                >
                  Send Request →
                </button>
              </div>
            </div>
          ) : (
            <div className={styles.empty}>
              {musicians.length === 0 ? 'No musicians found nearby' : 'No more musicians to explore'}
            </div>
          )}
        </div>
      ) : (
        <div className={styles.matchesList}>
          {matches.length > 0 ? (
            matches.map(match => (
              <div key={match.id} className={styles.matchCard}>
                <div className={styles.avatar}>
                  {match.profile_photo_url ? (
                    <img 
                      src={getImageUrl(match.profile_photo_url)}
                      alt={match.name}
                      onError={(e) => {e.target.style.display = 'none'}}
                    />
                  ) : (
                    <div className={styles.placeholder}>
                      {match.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>

                <div className={styles.matchInfo}>
                  <h3>{match.name}</h3>
                  <p>{match.location_name}</p>
                  <p className={styles.mutualMatch}>Mutual Match</p>
                </div>
              </div>
            ))
          ) : (
            <div className={styles.empty}>No mutual matches yet. Send requests to start matching!</div>
          )}
        </div>
      )}
    </div>
  )
}
