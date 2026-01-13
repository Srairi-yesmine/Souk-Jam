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
    role: 'jammer'
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
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
          <img src="/uploads/2.png" alt="Souk'Jam" className={styles.logoImg} />
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
