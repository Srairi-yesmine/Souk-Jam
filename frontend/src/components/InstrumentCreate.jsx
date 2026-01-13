import { useState } from 'react'
import { instrumentsAPI } from '../api'
import styles from './InstrumentCreate.module.css'

export default function InstrumentCreate() {
  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    type: 'electric_guitar',
    description: '',
    price_per_day: '',
    location_name: '',
    tags: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [photo, setPhoto] = useState(null)

  const instrumentTypes = [
    'electric_guitar', 'acoustic_guitar', 'bass_guitar', 'drums', 'keyboard',
    'piano', 'violin', 'cello', 'saxophone', 'trumpet', 'flute', 'clarinet',
    'oud', 'percussion', 'accordion'
  ]

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handlePhotoChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setPhoto(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const tags = formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      
      const submitData = {
        name: formData.name,
        brand: formData.brand,
        type: formData.type,
        description: formData.description,
        price_per_day: parseFloat(formData.price_per_day),
        location_name: formData.location_name,
        tags: tags
      }

      if (photo) {
        const photoFormData = new FormData()
        Object.keys(submitData).forEach(key => {
          if (key === 'tags') {
            photoFormData.append(key, JSON.stringify(submitData[key]))
          } else {
            photoFormData.append(key, submitData[key])
          }
        })
        photoFormData.append('photo', photo)
        await instrumentsAPI.create(photoFormData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } else {
        await instrumentsAPI.create(submitData)
      }

      setSuccess('Instrument created successfully!')
      setFormData({
        name: '',
        brand: '',
        type: 'electric_guitar',
        description: '',
        price_per_day: '',
        location_name: '',
        tags: ''
      })
      setPhoto(null)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create instrument')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2>Create New Instrument</h2>
        <p>List an instrument for rent on Souk'Jam</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}
          {success && <div className={styles.success}>{success}</div>}

          <div className={styles.formGroup}>
            <label>Instrument Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., Fender Stratocaster"
              required
            />
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label>Brand *</label>
              <input
                type="text"
                name="brand"
                value={formData.brand}
                onChange={handleChange}
                placeholder="e.g., Fender"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label>Type *</label>
              <select name="type" value={formData.type} onChange={handleChange} required>
                {instrumentTypes.map(type => (
                  <option key={type} value={type}>
                    {type.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className={styles.formGroup}>
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe the condition, features, and any special notes..."
              rows={4}
            />
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label>Price per Day (USD) *</label>
              <input
                type="number"
                name="price_per_day"
                value={formData.price_per_day}
                onChange={handleChange}
                placeholder="e.g., 25.00"
                step="0.01"
                min="0"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label>Location *</label>
              <input
                type="text"
                name="location_name"
                value={formData.location_name}
                onChange={handleChange}
                placeholder="City or neighborhood"
                required
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label>Tags (comma-separated)</label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="e.g., professional, vintage, new"
            />
          </div>

          <div className={styles.formGroup}>
            <label>Photo</label>
            <div className={styles.fileInput}>
              <input
                type="file"
                id="photoInput"
                accept="image/*"
                onChange={handlePhotoChange}
              />
              <label htmlFor="photoInput" className={styles.fileInputLabel}>
                {photo ? (
                  <span className={styles.fileName}>{photo.name}</span>
                ) : (
                  <span className={styles.filePrompt}>
                    <span className={styles.fileIcon}>📸</span>
                    Click to upload photo
                  </span>
                )}
              </label>
            </div>
          </div>

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? 'Creating...' : 'Create Instrument'}
          </button>
        </form>
      </div>
    </div>
  )
}
