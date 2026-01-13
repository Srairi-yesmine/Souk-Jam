import { useState, useEffect } from 'react'
import { getImageUrl } from '../utils/imageUrl'
import styles from './Navigation.module.css'

export default function Navigation({ currentPage, onNavigate, user }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  // On non-hero pages (create, rentals, jam, profile), nav is always opaque
  // On browse page, nav is transparent and becomes opaque when scrolled
  const isHeroPage = currentPage === 'browse'
  const shouldBeOpaque = !isHeroPage || scrolled

  useEffect(() => {
    const onScroll = () => {
      const threshold = Math.max(window.innerHeight - 120, 80)
      setScrolled(window.scrollY > threshold)
    }
    onScroll()
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav className={`${styles.nav} ${shouldBeOpaque ? styles.scrolledNav : ''}`}>
      <div className={styles.container}>
        <div className={styles.menu}>
          <button
            className={`${styles.navItem} ${currentPage === 'browse' ? styles.active : ''}`}
            onClick={() => {
              onNavigate('browse')
              setMobileMenuOpen(false)
            }}
          >
            Browse
          </button>

          <button
            className={`${styles.navItem} ${currentPage === 'create' ? styles.active : ''}`}
            onClick={() => {
              onNavigate('create')
              setMobileMenuOpen(false)
            }}
          >
            Add
          </button>

          <button
            className={`${styles.navItem} ${currentPage === 'rentals' ? styles.active : ''}`}
            onClick={() => {
              onNavigate('rentals')
              setMobileMenuOpen(false)
            }}
          >
            Rentals
          </button>

          <button
            className={`${styles.navItem} ${currentPage === 'jam' ? styles.active : ''}`}
            onClick={() => {
              onNavigate('jam')
              setMobileMenuOpen(false)
            }}
          >
            Jam
          </button>

          <button
            className={`${styles.navItem} ${currentPage === 'profile' ? styles.active : ''}`}
            onClick={() => {
              onNavigate('profile')
              setMobileMenuOpen(false)
            }}
          >
            Profile
          </button>
        </div>

        <div className={styles.userSection}>
          <div className={styles.userAvatar}>
            {user?.profile_photo_url ? (
              <img src={getImageUrl(user.profile_photo_url)} alt={user.name} />
            ) : (
              <div className={styles.avatarPlaceholder}>
                {user?.name?.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div className={styles.userName}>{user?.name}</div>
        </div>
      </div>
    </nav>
  )
}
