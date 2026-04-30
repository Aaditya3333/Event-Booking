import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { Menu, X, Search, User, LogOut, Settings, Calendar, Ticket } from 'lucide-react'

export function Header() {
  const [user, setUser] = useState<any>(null)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (error) {
        // Clear invalid data
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      }
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
    navigate('/')
  }

  return (
    <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '1rem 0' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '32px', height: '32px', backgroundColor: '#3b82f6', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontWeight: 'bold', fontSize: '12px' }}>EB</span>
          </div>
          <Link to="/" style={{ textDecoration: 'none', color: '#1f2937', fontSize: '1.25rem', fontWeight: 'bold' }}>
            EventBooking
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <Link to="/events" style={{ color: '#6b7280', textDecoration: 'none' }}>Events</Link>
          
          {user ? (
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  backgroundColor: 'white',
                  cursor: 'pointer'
                }}
              >
                <User size={16} />
                <span style={{ fontSize: '0.875rem' }}>{user.full_name || user.username}</span>
              </button>

              {isProfileOpen && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  right: '0',
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  minWidth: '200px',
                  zIndex: 50
                }}>
                  <Link
                    to="/profile"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1rem',
                      color: '#374151',
                      textDecoration: 'none',
                      fontSize: '0.875rem'
                    }}
                  >
                    <Settings size={16} />
                    Profile
                  </Link>
                  <Link
                    to="/my-bookings"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1rem',
                      color: '#374151',
                      textDecoration: 'none',
                      fontSize: '0.875rem'
                    }}
                  >
                    <Calendar size={16} />
                    My Bookings
                  </Link>
                  <Link
                    to="/my-tickets"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1rem',
                      color: '#374151',
                      textDecoration: 'none',
                      fontSize: '0.875rem'
                    }}
                  >
                    <Ticket size={16} />
                    My Tickets
                  </Link>
                  <hr style={{ margin: '0.5rem 0', border: 'none', borderTop: '1px solid #e5e7eb' }} />
                  <button
                    onClick={handleLogout}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem 1rem',
                      color: '#dc2626',
                      backgroundColor: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      width: '100%'
                    }}
                  >
                    <LogOut size={16} />
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Link
                to="/login"
                style={{
                  color: '#6b7280',
                  textDecoration: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb'
                }}
              >
                Login
              </Link>
              <Link
                to="/register"
                style={{
                  color: 'white',
                  backgroundColor: '#3b82f6',
                  textDecoration: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '6px'
                }}
              >
                Sign Up
              </Link>
            </div>
          )}
        </nav>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          style={{
            display: 'none',
            padding: '0.5rem',
            border: 'none',
            backgroundColor: 'transparent',
            cursor: 'pointer'
          }}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div style={{
            position: 'absolute',
            top: '100%',
            left: '0',
            right: '0',
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '0 0 8px 8px',
            padding: '1rem',
            zIndex: 50
          }}>
            <Link
              to="/events"
              style={{
                display: 'block',
                padding: '0.75rem 0',
                color: '#6b7280',
                textDecoration: 'none'
              }}
            >
              Events
            </Link>
            
            {user ? (
              <>
                <Link
                  to="/profile"
                  style={{
                    display: 'block',
                    padding: '0.75rem 0',
                    color: '#374151',
                    textDecoration: 'none'
                  }}
                >
                  Profile
                </Link>
                <Link
                  to="/my-bookings"
                  style={{
                    display: 'block',
                    padding: '0.75rem 0',
                    color: '#374151',
                    textDecoration: 'none'
                  }}
                >
                  My Bookings
                </Link>
                <Link
                  to="/my-tickets"
                  style={{
                    display: 'block',
                    padding: '0.75rem 0',
                    color: '#374151',
                    textDecoration: 'none'
                  }}
                >
                  My Tickets
                </Link>
                <button
                  onClick={handleLogout}
                  style={{
                    display: 'block',
                    padding: '0.75rem 0',
                    color: '#dc2626',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    width: '100%',
                    textAlign: 'left'
                  }}
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  style={{
                    display: 'block',
                    padding: '0.75rem 0',
                    color: '#6b7280',
                    textDecoration: 'none'
                  }}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  style={{
                    display: 'block',
                    padding: '0.75rem 0',
                    color: '#3b82f6',
                    textDecoration: 'none'
                  }}
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </header>
  )
}
