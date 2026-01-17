import { useState } from 'react'
import { authAPI } from '../api'
import { getImageUrl } from '../utils/imageUrl'
import styles from './Auth.module.css'

export default function Auth({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    location_name: '',
    role: 'jammer',
    genres_enjoyed: [],
    instruments_played: [],
    instruments_owned: [],
    is_active_for_jam: true
  })

  const genres = [
    // Western Genres
    'Rock', 'Jazz', 'Blues', 'Classical', 'Pop', 'Hip-Hop', 'Electronic', 'Folk', 'Metal', 'R&B',
    // Tunisian/North African Genres
    'Malouf', 'Malouf Tunisien', 'Mezoued', 'Stambali', 'Raï', 'Mahjouz', 'Andalusian', 'Gnawa', 'Chaâbi', 'Taksim'
  ]
  const instrumentOptions = ['Guitar', 'Drums', 'Bass', 'Vocals', 'Keyboard', 'Violin', 'Saxophone', 'Trumpet', 'Percussion', 'Flute', 'Oud', 'Ney', 'Darbuka', 'Bendir']
  const skillLevels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const toggleGenre = (genre) => {
    setFormData(prev => ({
      ...prev,
      genres_enjoyed: prev.genres_enjoyed.includes(genre)
        ? prev.genres_enjoyed.filter(g => g !== genre)
        : [...prev.genres_enjoyed, genre]
    }))
  }

  const handleInstrumentChange = (index, field, value) => {
    setFormData(prev => {
      const updated = [...prev.instruments_played]
      if (!updated[index]) updated[index] = { instrument_type: '', skill_level: 'beginner' }
      updated[index][field] = value
      return { ...prev, instruments_played: updated }
    })
  }

  const addInstrument = () => {
    setFormData(prev => ({
      ...prev,
      instruments_played: [...prev.instruments_played, { instrument_type: '', skill_level: 'beginner' }]
    }))
  }

  const removeInstrument = (index) => {
    setFormData(prev => ({
      ...prev,
      instruments_played: prev.instruments_played.filter((_, i) => i !== index)
    }))
  }

  const toggleJamActivity = () => {
    setFormData(prev => ({ ...prev, is_active_for_jam: !prev.is_active_for_jam }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      let response
      if (isLogin) {
        response = await authAPI.login(formData.email, formData.password)
      } else {
        response = await authAPI.register(formData)
      }

      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user_id', response.data.id)
      onLoginSuccess()
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <div className={styles.logoSection}>
          <img src="http://localhost:5000/uploads/logo%20SJ.png" alt="Souk'Jam" className={styles.logoImg} />
          <h1>Souk'Jam</h1>
          <p>Connect Musicians • Rent Instruments</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.formGroup}>
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />
          </div>

          {!isLogin && (
            <>
              <div className={styles.formGroup}>
                <label>Full Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="John Musician"
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label>Location</label>
                <input
                  type="text"
                  name="location_name"
                  value={formData.location_name}
                  onChange={handleChange}
                  placeholder="City, Country"
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label>I am a</label>
                <select name="role" value={formData.role} onChange={handleChange}>
                  <option value="jammer">Jammer (Musician)</option>
                  <option value="owner">Instrument Owner</option>
                  <option value="renter">Renter</option>
                </select>
              </div>

              {/* Genres Section */}
              <div className={styles.sectionDivider} />
              <div className={styles.sectionTitle}>Musical Preferences</div>

              <div className={styles.formGroup}>
                <label>Genres You Enjoy</label>
                <div className={styles.genresGrid}>
                  {genres.map(genre => (
                    <button
                      key={genre}
                      type="button"
                      className={`${styles.genreTag} ${formData.genres_enjoyed.includes(genre) ? styles.active : ''}`}
                      onClick={() => toggleGenre(genre)}
                    >
                      {genre}
                    </button>
                  ))}
                </div>
              </div>

              {/* Instruments Section */}
              <div className={styles.formGroup}>
                <label>Instruments You Play</label>
                <div className={styles.instrumentsList}>
                  {formData.instruments_played.map((instrument, index) => (
                    <div key={index} className={styles.instrumentRow}>
                      <select
                        value={instrument.instrument_type}
                        onChange={(e) => handleInstrumentChange(index, 'instrument_type', e.target.value)}
                        className={styles.instrumentSelect}
                      >
                        <option value="">Select Instrument</option>
                        {instrumentOptions.map(inst => (
                          <option key={inst} value={inst.toLowerCase()}>{inst}</option>
                        ))}
                      </select>
                      <select
                        value={instrument.skill_level}
                        onChange={(e) => handleInstrumentChange(index, 'skill_level', e.target.value)}
                        className={styles.skillSelect}
                      >
                        {skillLevels.map(level => (
                          <option key={level} value={level.toLowerCase()}>{level}</option>
                        ))}
                      </select>
                      <button
                        type="button"
                        onClick={() => removeInstrument(index)}
                        className={styles.removeBtn}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={addInstrument}
                  className={styles.addInstrumentBtn}
                >
                  + Add Instrument
                </button>
              </div>

              {/* Active for Jam Toggle */}
              <div className={styles.jamToggle}>
                <label>Available for Jam Sessions</label>
                <button
                  type="button"
                  onClick={toggleJamActivity}
                  className={`${styles.toggleSwitch} ${formData.is_active_for_jam ? styles.active : ''}`}
                >
                  <span className={styles.toggleSlider}></span>
                  {formData.is_active_for_jam ? 'Yes' : 'No'}
                </button>
              </div>
            </>
          )}

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? 'Loading...' : isLogin ? 'Sign In' : 'Sign Up'}
          </button>
        </form>

        <div className={styles.toggle}>
          {isLogin ? 'No account? ' : 'Already have an account? '}
          <button 
            type="button"
            onClick={() => {
              setIsLogin(!isLogin)
              setError('')
            }}
            className={styles.toggleBtn}
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  )
}
