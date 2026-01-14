/**
 * Get the correct image URL for frontend rendering
 * Uses backend API endpoint for all uploaded images
 * @param {string} photoUrl - The photo URL from the API
 * @returns {string|null} - The resolved image URL or null
 */
export const getImageUrl = (photoUrl) => {
  if (!photoUrl) return null
  
  // If it's already an absolute HTTP URL, return it
  if (photoUrl.startsWith('http')) return photoUrl
  
  // All paths from the API are /uploads/*, route to backend
  // Backend has /uploads/<path:filepath> route to serve files
  if (photoUrl.startsWith('/uploads')) {
    return `http://localhost:5000${photoUrl}`
  }
  
  // If it's just a filename (no slash), construct backend URL
  if (!photoUrl.startsWith('/')) {
    return `http://localhost:5000/uploads/${photoUrl}`
  }
  
  // Otherwise, construct backend URL
  return `http://localhost:5000${photoUrl}`
}

