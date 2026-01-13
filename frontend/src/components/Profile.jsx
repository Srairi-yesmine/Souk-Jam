import { useState } from 'react'
import { authAPI } from '../api'
import { getImageUrl } from '../utils/imageUrl'
import styles from './Profile.module.css'

export default function Profile({ user, onLogout }) {
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [photoFile, setPhotoFile] = useState(null)

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0]
    if (file) {
      setLoading(true)
      try {
        const formData = new FormData()
        formData.append('profile_photo', file)
        await authAPI.uploadProfilePhoto(user.id, file)
        setPhotoFile(null)
        window.location.reload()
      } catch (error) {
        console.error('Error uploading photo:', error)
      } finally {
        setLoading(false)
      }
    }
  }

  return (
    <div className={styles.profile}>
      <div className={styles.header}>
        <h2>Profile</h2>
      </div>

      <div className={styles.card}>
        <div className={styles.photoSection}>
          <div className={styles.photoContainer}>
            {user?.profile_photo_url ? (
              <img src={getImageUrl(user.profile_photo_url)} alt={user.name} />
            ) : (
              <div className={styles.placeholder}>
                {user?.name?.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <label className={styles.uploadLabel}>
            Change Photo
            <input
              type="file"
              accept="image/*"
              onChange={handlePhotoUpload}
              disabled={loading}
            />
          </label>
        </div>

        <div className={styles.infoSection}>
          <div className={styles.infoGroup}>
            <label>Name</label>
            <p>{user?.name}</p>
          </div>

          <div className={styles.infoGroup}>
            <label>Email</label>
            <p>{user?.email}</p>
          </div>

          <div className={styles.infoGroup}>
            <label>Location</label>
            <p>{user?.location_name}</p>
          </div>

          <div className={styles.infoGroup}>
            <label>Role</label>
            <p className={styles.role}>{user?.role}</p>
          </div>

          {user?.genres_enjoyed && user.genres_enjoyed.length > 0 && (
            <div className={styles.infoGroup}>
              <label>Genres</label>
              <div className={styles.tags}>
                {user.genres_enjoyed.map((genre, i) => (
                  <span key={i}>{genre}</span>
                ))}
              </div>
            </div>
          )}

          {user?.instruments_played && user.instruments_played.length > 0 && (
            <div className={styles.infoGroup}>
              <label>Instruments</label>
              <div className={styles.tags}>
                {user.instruments_played.map((inst, i) => (
                  <span key={i}>
                    {typeof inst === 'string' ? inst : inst.instrument_type}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <button className={styles.logoutBtn} onClick={onLogout}>
          Sign Out
        </button>
      </div>
    </div>
  )
}
