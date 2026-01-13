/**
 * Get the correct image URL for frontend rendering
 * Tries frontend public folder first, then falls back to backend
 * @param {string} photoUrl - The photo URL from the API
 * @returns {string|null} - The resolved image URL or null
 */
export const getImageUrl = (photoUrl) => {
  if (!photoUrl) return null
  
  // If it's already an absolute HTTP URL, return it
  if (photoUrl.startsWith('http')) return photoUrl
  
  // If it's a relative path starting with /uploads, try frontend public first, then backend
  if (photoUrl.startsWith('/uploads')) {
    // In development, Vite serves from public folder
    // Try backend first (more reliable for uploaded content)
    return `http://localhost:5000${photoUrl}`
  }
  
  // If it's just a filename, construct backend URL
  if (!photoUrl.startsWith('/')) {
    return `http://localhost:5000/uploads/${photoUrl}`
  }
  
  // Otherwise, construct backend URL
  return `http://localhost:5000${photoUrl}`
}

