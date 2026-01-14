import { useState, useEffect } from 'react'
import Auth from './components/Auth'
import Navigation from './components/Navigation'
import InstrumentBrowser from './components/InstrumentBrowser'
import InstrumentCreate from './components/InstrumentCreate'
import InstrumentManagement from './components/InstrumentManagement'
import RentalModal from './components/RentalModal'
import RentalManager from './components/RentalManager'
import JamDiscovery from './components/JamDiscovery'
import Profile from './components/Profile'
import { authAPI } from './api'
import styles from './App.module.css'

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState(null)
  const [currentPage, setCurrentPage] = useState('browse')
  const [selectedInstrument, setSelectedInstrument] = useState(null)
  const [refreshCounter, setRefreshCounter] = useState(0)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUser()
    }
  }, [])

  const fetchUser = async () => {
    try {
      const userId = localStorage.getItem('user_id')
      const response = await authAPI.getUser(userId)
      setUser(response.data)
      setIsLoggedIn(true)
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_id')
    }
  }

  const handleLoginSuccess = async () => {
    await fetchUser()
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    setIsLoggedIn(false)
    setUser(null)
    setCurrentPage('browse')
  }

  const handleRentClick = (instrument) => {
    setSelectedInstrument(instrument)
  }

  const handleRentalSuccess = () => {
    setRefreshCounter(prev => prev + 1)
  }

  if (!isLoggedIn) {
    return <Auth onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <div className={styles.app}>
      <Navigation 
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        user={user}
      />

      {currentPage === 'browse' && (
        <div className={styles.hero}>
          <div className={styles.heroContent}>
            <div className={styles.heroText}>
              <h1 className={styles.heroTitle}>Find Your Perfect Instrument</h1>
              <p className={styles.heroSubtitle}>Discover high-quality instruments available for rent in your area</p>
            </div>
            <img src="/uploads/musician-playing-electric-guitar.jpg" alt="Musician" className={styles.heroImage} />
          </div>
        </div>
      )}

      <main className={styles.main}>
        {currentPage === 'browse' && (
          <InstrumentBrowser onRentClick={handleRentClick} />
        )}
        {currentPage === 'create' && (
          <InstrumentCreate />
        )}
        {currentPage === 'manage' && user && (
          <InstrumentManagement user={user} token={localStorage.getItem('access_token')} onNavigate={setCurrentPage} />
        )}
        {currentPage === 'rentals' && (
          <RentalManager key={refreshCounter} user={user} />
        )}
        {currentPage === 'jam' && (
          <JamDiscovery />
        )}
        {currentPage === 'profile' && (
          <Profile user={user} onLogout={handleLogout} />
        )}
      </main>

      {selectedInstrument && (
        <RentalModal
          instrument={selectedInstrument}
          onClose={() => setSelectedInstrument(null)}
          onSuccess={handleRentalSuccess}
        />
      )}
    </div>
  )
}
