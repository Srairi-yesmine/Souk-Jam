import { useState, useEffect } from 'react'
import { getImageUrl } from '../utils/imageUrl'
import styles from './InstrumentManagement.module.css'

export default function InstrumentManagement({ user, token, onNavigate }) {
  const [instruments, setInstruments] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState(null)
  const [editData, setEditData] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Fetch user's instruments
  useEffect(() => {
    fetchInstruments()
  }, [user])

  const fetchInstruments = async () => {
    try {
      setLoading(true)
      const response = await fetch(
        `http://localhost:5000/instruments/?owner_id=${user.id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      if (response.ok) {
        const data = await response.json()
        setInstruments(data)
      }
    } catch (err) {
      setError('Failed to load instruments')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (instrument) => {
    setEditingId(instrument.id)
    setEditData({ ...instrument })
    setImagePreview(getImageUrl(instrument.photo_url))
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onload = (event) => setImagePreview(event.target.result)
      reader.readAsDataURL(file)
    }
  }

  const handleInputChange = (field, value) => {
    setEditData({ ...editData, [field]: value })
  }

  const handleSave = async () => {
    try {
      setError('')
      const formData = new FormData()
      formData.append('name', editData.name)
      formData.append('brand', editData.brand)
      formData.append('type', editData.type)
      formData.append('description', editData.description)
      formData.append('price_per_day', editData.price_per_day)
      formData.append('location_name', editData.location_name)
      formData.append('tags', JSON.stringify(editData.tags || []))
      if (imageFile) {
        formData.append('photo', imageFile)
      }

      const response = await fetch(
        `http://localhost:5000/instruments/${editingId}`,
        {
          method: 'PUT',
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        }
      )

      if (response.ok) {
        setSuccess('Instrument updated successfully!')
        setEditingId(null)
        setImageFile(null)
        fetchInstruments()
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const data = await response.json()
        setError(data.message || 'Failed to update instrument')
      }
    } catch (err) {
      setError('Error updating instrument')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this instrument?')) return

    try {
      setError('')
      const response = await fetch(`http://localhost:5000/instruments/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.ok) {
        setSuccess('Instrument deleted successfully!')
        fetchInstruments()
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const errorData = await response.json().catch(() => ({}))
        setError(errorData.message || `Failed to delete instrument (${response.status})`)
      }
    } catch (err) {
      setError(err.message || 'Error deleting instrument')
    }
  }

  if (loading) {
    return <div className={styles.container}>Loading your instruments...</div>
  }

  if (instruments.length === 0) {
    return (
      <div className={styles.container}>
        <h2>My Instruments</h2>
        <div className={styles.empty}>
          <p>You haven't added any instruments yet</p>
          <button 
            className={styles.addBtn}
            onClick={() => onNavigate('create')}
          >
            Add Your First Instrument
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <h2>My Instruments</h2>
      
      {error && <div className={styles.error}>{error}</div>}
      {success && <div className={styles.success}>{success}</div>}

      <div className={styles.instrumentsList}>
        {instruments.map((instrument) => (
          <div key={instrument.id} className={styles.instrumentCard}>
            {editingId === instrument.id ? (
              // Edit mode
              <div className={styles.editForm}>
                <div className={styles.editGrid}>
                  <div className={styles.imageSection}>
                    <div className={styles.imagePreview}>
                      {imagePreview && (
                        <img src={imagePreview} alt="Preview" />
                      )}
                    </div>
                    <label className={styles.fileInput}>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                      />
                      Change Image
                    </label>
                  </div>

                  <div className={styles.fieldsSection}>
                    <div className={styles.field}>
                      <label>Name</label>
                      <input
                        type="text"
                        value={editData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                      />
                    </div>

                    <div className={styles.field}>
                      <label>Brand</label>
                      <input
                        type="text"
                        value={editData.brand}
                        onChange={(e) => handleInputChange('brand', e.target.value)}
                      />
                    </div>

                    <div className={styles.field}>
                      <label>Type</label>
                      <input
                        type="text"
                        value={editData.type}
                        onChange={(e) => handleInputChange('type', e.target.value)}
                      />
                    </div>

                    <div className={styles.field}>
                      <label>Price per Day (TND)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editData.price_per_day}
                        onChange={(e) => handleInputChange('price_per_day', parseFloat(e.target.value))}
                      />
                    </div>

                    <div className={styles.field}>
                      <label>Location</label>
                      <input
                        type="text"
                        value={editData.location_name}
                        onChange={(e) => handleInputChange('location_name', e.target.value)}
                      />
                    </div>

                    <div className={styles.field}>
                      <label>Description</label>
                      <textarea
                        value={editData.description}
                        onChange={(e) => handleInputChange('description', e.target.value)}
                        rows="4"
                      />
                    </div>
                  </div>
                </div>

                <div className={styles.actions}>
                  <button className={styles.saveBtn} onClick={handleSave}>
                    Save Changes
                  </button>
                  <button 
                    className={styles.cancelBtn}
                    onClick={() => {
                      setEditingId(null)
                      setImageFile(null)
                      setImagePreview(null)
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              // View mode
              <div className={styles.viewMode}>
                <div className={styles.imageContainer}>
                  {getImageUrl(instrument.photo_url) && (
                    <img 
                      src={getImageUrl(instrument.photo_url)} 
                      alt={instrument.name}
                    />
                  )}
                </div>

                <div className={styles.details}>
                  <h3>{instrument.name}</h3>
                  <p className={styles.brand}>{instrument.brand}</p>
                  <p className={styles.type}>{instrument.type}</p>
                  <p className={styles.price}>{instrument.price_per_day} TND/day</p>
                  <p className={styles.location}>{instrument.location_name}</p>
                  <p className={styles.status}>
                    Status: <span className={`${styles.statusBadge} ${styles[instrument.status]}`}>
                      {instrument.status}
                    </span>
                  </p>
                </div>

                <div className={styles.cardActions}>
                  <button 
                    className={styles.editBtn}
                    onClick={() => handleEdit(instrument)}
                  >
                    Edit
                  </button>
                  <button 
                    className={styles.deleteBtn}
                    onClick={() => handleDelete(instrument.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <button 
        className={styles.addMoreBtn}
        onClick={() => onNavigate('create')}
      >
        + Add Another Instrument
      </button>
    </div>
  )
}
