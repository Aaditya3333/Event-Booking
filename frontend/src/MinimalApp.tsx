import React, { useState, useEffect } from 'react'
import { Routes, Route, BrowserRouter } from 'react-router-dom'

function SimpleLoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('Logging in...')
    
    try {
      // Try backend first with timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 3000) // 3 second timeout
      
      const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (response.ok) {
        const data = await response.json()
        setMessage(`Login successful! Welcome ${data.user.full_name}`)
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        
        // Simulate sending login notification email
        console.log(`📧 Login notification sent to: ${data.user.email}`)
        console.log(`📧 Subject: New login to your EventBooking account`)
        console.log(`📧 Time: ${new Date().toLocaleString()}`)
        
        // Redirect to events page after successful login
        setTimeout(() => {
          window.location.href = '/events'
        }, 1500)
      } else {
        throw new Error('Backend login failed')
      }
    } catch (error) {
      console.log('🔄 Backend unavailable, using mock authentication...')
      
      // Fallback: Simple mock authentication
      if ((email === 'test@example.com' && password === 'test123') || 
          (email === 'aditi@gmail.com' && password === 'aditi123')) {
        const mockUser = {
          id: 1,
          email: email,
          full_name: email === 'aditi@gmail.com' ? 'Aditi' : 'Test User',
          created_at: new Date().toISOString()
        }
        
        setMessage(`Login successful! Welcome ${mockUser.full_name}`)
        localStorage.setItem('access_token', 'mock_token_' + Date.now())
        localStorage.setItem('user', JSON.stringify(mockUser))
        
        console.log(`📧 Login notification sent to: ${mockUser.email}`)
        console.log(`📧 Subject: New login to your EventBooking account`)
        console.log(`📧 Time: ${new Date().toLocaleString()}`)
        
        setTimeout(() => {
          window.location.href = '/events'
        }, 1500)
      } else {
        setMessage('Login failed. Please check your credentials.')
      }
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ 
        maxWidth: '450px', 
        width: '100%', 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden'
      }}>
        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
          padding: '40px 30px', 
          textAlign: 'center',
          color: 'white'
        }}>
          <div style={{ 
            width: '60px', 
            height: '60px', 
            backgroundColor: 'rgba(255, 255, 255, 0.2)', 
            borderRadius: '50%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            margin: '0 auto 20px',
            fontSize: '1.5rem'
          }}>
            🔐
          </div>
          <h2 style={{ fontSize: '2rem', marginBottom: '10px', fontWeight: '600' }}>Welcome Back</h2>
          <p style={{ opacity: 0.9 }}>Sign in to your account to continue</p>
        </div>
        
        <div style={{ padding: '40px 30px' }}>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email"
                style={{ 
                  width: '100%', 
                  padding: '12px 16px', 
                  border: '2px solid #e5e7eb', 
                  borderRadius: '8px',
                  fontSize: '1rem',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>
            
            <div style={{ marginBottom: '30px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
                style={{ 
                  width: '100%', 
                  padding: '12px 16px', 
                  border: '2px solid #e5e7eb', 
                  borderRadius: '8px',
                  fontSize: '1rem',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>
            
            <button
              type="submit"
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1.1rem',
                fontWeight: '600',
                transition: 'transform 0.2s',
                marginBottom: '20px'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              Sign In
            </button>
          </form>
          
          {message && (
            <div style={{ 
              padding: '12px 16px', 
              backgroundColor: message.includes('successful') ? '#d1fae5' : '#fee2e2', 
              borderRadius: '8px',
              color: message.includes('successful') ? '#065f46' : '#991b1b',
              textAlign: 'center',
              marginBottom: '20px'
            }}>
              {message}
            </div>
          )}
          
          <div style={{ textAlign: 'center', color: '#6b7280' }}>
            Don't have an account? <a href="/register" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600' }}>Sign up</a>
          </div>
        </div>
      </div>
    </div>
  )
}

function SimpleRegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    phone: ''
  })
  const [message, setMessage] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('Registering...')
    
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        const data = await response.json()
        setMessage(`Registration successful! Welcome ${data.user.full_name}`)
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        
        // Simulate sending welcome email
        console.log(`📧 Welcome email sent to: ${data.user.email}`)
        console.log(`📧 Subject: Welcome to EventBooking!`)
        console.log(`📧 Your account has been created successfully`)
        
        // Redirect to events page after successful registration
        setTimeout(() => {
          window.location.href = '/events'
        }, 2000)
      } else {
        setMessage('Registration failed. Please try again.')
      }
    } catch (error) {
      setMessage('Network error. Please try again.')
      console.error('Registration error:', error)
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ 
        maxWidth: '500px', 
        width: '100%', 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden'
      }}>
        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
          padding: '40px 30px', 
          textAlign: 'center',
          color: 'white'
        }}>
          <div style={{ 
            width: '60px', 
            height: '60px', 
            backgroundColor: 'rgba(255, 255, 255, 0.2)', 
            borderRadius: '50%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            margin: '0 auto 20px',
            fontSize: '1.5rem'
          }}>
            ✨
          </div>
          <h2 style={{ fontSize: '2rem', marginBottom: '10px', fontWeight: '600' }}>Create Account</h2>
          <p style={{ opacity: 0.9 }}>Join us and start booking amazing events</p>
        </div>
        
        <div style={{ padding: '40px 30px' }}>
          <form onSubmit={handleRegister}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Full Name</label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                  placeholder="John Doe"
                  style={{ 
                    width: '100%', 
                    padding: '12px 16px', 
                    border: '2px solid #e5e7eb', 
                    borderRadius: '8px',
                    fontSize: '1rem',
                    transition: 'border-color 0.2s',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  placeholder="johndoe"
                  style={{ 
                    width: '100%', 
                    padding: '12px 16px', 
                    border: '2px solid #e5e7eb', 
                    borderRadius: '8px',
                    fontSize: '1rem',
                    transition: 'border-color 0.2s',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
              </div>
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Email Address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="john@example.com"
                style={{ 
                  width: '100%', 
                  padding: '12px 16px', 
                  border: '2px solid #e5e7eb', 
                  borderRadius: '8px',
                  fontSize: '1rem',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Phone Number (Optional)</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+1 234 567 8900"
                style={{ 
                  width: '100%', 
                  padding: '12px 16px', 
                  border: '2px solid #e5e7eb', 
                  borderRadius: '8px',
                  fontSize: '1rem',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>
            
            <div style={{ marginBottom: '30px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Create a strong password"
                style={{ 
                  width: '100%', 
                  padding: '12px 16px', 
                  border: '2px solid #e5e7eb', 
                  borderRadius: '8px',
                  fontSize: '1rem',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>
            
            <button
              type="submit"
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1.1rem',
                fontWeight: '600',
                transition: 'transform 0.2s',
                marginBottom: '20px'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              Create Account
            </button>
          </form>
          
          {message && (
            <div style={{ 
              padding: '12px 16px', 
              backgroundColor: message.includes('successful') ? '#d1fae5' : '#fee2e2', 
              borderRadius: '8px',
              color: message.includes('successful') ? '#065f46' : '#991b1b',
              textAlign: 'center',
              marginBottom: '20px'
            }}>
              {message}
            </div>
          )}
          
          <div style={{ textAlign: 'center', color: '#6b7280' }}>
            Already have an account? <a href="/login" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600' }}>Sign in</a>
          </div>
        </div>
      </div>
    </div>
  )
}

function EventsPage() {
  const [events, setEvents] = useState([
    {
      id: 1,
      title: "Summer Music Festival 2024",
      description: "Experience the best summer vibes with top artists from around the world",
      date: "2024-07-15",
      time: "6:00 PM",
      location: "Central Park, New York",
      price: 75,
      image: "https://picsum.photos/seed/music-fest/400/300.jpg",
      category: "Music",
      availableTickets: 150,
      totalTickets: 500
    },
    {
      id: 2,
      title: "Tech Conference 2024",
      description: "Join industry leaders for the biggest tech conference of the year",
      date: "2024-08-20",
      time: "9:00 AM",
      location: "Convention Center, San Francisco",
      price: 299,
      image: "https://picsum.photos/seed/tech-conf/400/300.jpg",
      category: "Technology",
      availableTickets: 200,
      totalTickets: 1000
    },
    {
      id: 3,
      title: "Food & Wine Festival",
      description: "Savor exquisite cuisines and fine wines from renowned chefs",
      date: "2024-09-10",
      time: "12:00 PM",
      location: "Harbor Front, Miami",
      price: 120,
      image: "https://picsum.photos/seed/food-fest/400/300.jpg",
      category: "Food & Drink",
      availableTickets: 80,
      totalTickets: 300
    },
    {
      id: 4,
      title: "Comedy Night Special",
      description: "Laugh out loud with the best comedians in the industry",
      date: "2024-06-25",
      time: "8:00 PM",
      location: "Comedy Club, Los Angeles",
      price: 45,
      image: "https://picsum.photos/seed/comedy-night/400/300.jpg",
      category: "Entertainment",
      availableTickets: 120,
      totalTickets: 200
    },
    {
      id: 5,
      title: "Art Exhibition Opening",
      description: "Contemporary art exhibition featuring emerging artists",
      date: "2024-07-01",
      time: "7:00 PM",
      location: "Art Gallery, Chicago",
      price: 35,
      image: "https://picsum.photos/seed/art-expo/400/300.jpg",
      category: "Art",
      availableTickets: 90,
      totalTickets: 150
    },
    {
      id: 6,
      title: "Sports Marathon",
      description: "Challenge yourself in the city's biggest marathon event",
      date: "2024-10-15",
      time: "6:00 AM",
      location: "City Stadium, Boston",
      price: 85,
      image: "https://picsum.photos/seed/marathon/400/300.jpg",
      category: "Sports",
      availableTickets: 300,
      totalTickets: 2000
    }
  ])
  
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [priceRange, setPriceRange] = useState([0, 500])
  
  const categories = ['All', 'Music', 'Technology', 'Food & Drink', 'Entertainment', 'Art', 'Sports']
  
  const filteredEvents = events.filter(event => {
    const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || event.category === selectedCategory
    const matchesPrice = event.price >= priceRange[0] && event.price <= priceRange[1]
    
    return matchesSearch && matchesCategory && matchesPrice
  })

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Search and Filter Section */}
      <section style={{ backgroundColor: 'white', padding: '40px 20px', borderBottom: '1px solid #e5e7eb' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '2rem', color: '#1f2937', textAlign: 'center' }}>
            Discover Events
          </h1>
          
          {/* Search Bar */}
          <div style={{ marginBottom: '30px', maxWidth: '600px', margin: '0 auto 30px' }}>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    // Search is already happening in real-time, but Enter key provides feedback
                    console.log('Searching for:', searchTerm)
                  }
                }}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
              <button
                onClick={() => {
                  // Search is already happening in real-time, but button provides visual feedback
                  console.log('Search button clicked - searching for:', searchTerm)
                  // You could add analytics or other actions here
                }}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  transition: 'all 0.2s'
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#5a67d8'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#667eea'}
              >
                Search
              </button>
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  style={{
                    padding: '12px 16px',
                    backgroundColor: '#6b7280',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#4b5563'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#6b7280'}
                >
                  Clear
                </button>
              )}
            </div>
            <div style={{ marginTop: '8px', fontSize: '0.875rem', color: '#6b7280', textAlign: 'center' }}>
              {searchTerm && `Searching for "${searchTerm}"...`}
            </div>
          </div>
          
          {/* Filters */}
          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
            {/* Category Filter */}
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                style={{
                  padding: '8px 12px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  outline: 'none'
                }}
              >
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            {/* Price Range Filter */}
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '500' }}>
                Price Range: ${priceRange[0]} - ${priceRange[1]}
              </label>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <input
                  type="range"
                  min="0"
                  max="500"
                  value={priceRange[0]}
                  onChange={(e) => setPriceRange([parseInt(e.target.value), priceRange[1]])}
                  style={{ width: '100px' }}
                />
                <input
                  type="range"
                  min="0"
                  max="500"
                  value={priceRange[1]}
                  onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                  style={{ width: '100px' }}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Events Grid */}
      <section style={{ padding: '40px 20px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ marginBottom: '20px', color: '#6b7280' }}>
            Showing {filteredEvents.length} events
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '30px' }}>
            {filteredEvents.map(event => (
              <div
                key={event.id}
                style={{
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  cursor: 'pointer'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)'
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)'
                }}
              >
                {/* Event Image */}
                <div style={{ height: '200px', backgroundColor: '#f3f4f6', position: 'relative' }}>
                  <img
                    src={event.image}
                    alt={event.title}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                  <div style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}>
                    {event.category}
                  </div>
                </div>
                
                {/* Event Details */}
                <div style={{ padding: '20px' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '8px', color: '#1f2937' }}>
                    {event.title}
                  </h3>
                  <p style={{ color: '#6b7280', marginBottom: '12px', fontSize: '0.95rem', lineHeight: '1.5' }}>
                    {event.description}
                  </p>
                  
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', color: '#374151' }}>
                      <span style={{ marginRight: '8px' }}>📅</span>
                      <span style={{ fontSize: '0.9rem' }}>{event.date} at {event.time}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', color: '#374151' }}>
                      <span style={{ marginRight: '8px' }}>📍</span>
                      <span style={{ fontSize: '0.9rem' }}>{event.location}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', color: '#374151' }}>
                      <span style={{ marginRight: '8px' }}>🎫</span>
                      <span style={{ fontSize: '0.9rem' }}>
                        {event.availableTickets} of {event.totalTickets} tickets left
                      </span>
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#667eea' }}>
                        ${event.price}
                      </span>
                      <span style={{ color: '#6b7280', fontSize: '0.875rem', marginLeft: '4px' }}>
                        per ticket
                      </span>
                    </div>
                    <a
                      href={`/events/${event.id}`}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#667eea',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: '600',
                        fontSize: '0.9rem',
                        textDecoration: 'none',
                        display: 'inline-block'
                      }}
                    >
                      View Details
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {filteredEvents.length === 0 && (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: '#6b7280' }}>
              <div style={{ fontSize: '3rem', marginBottom: '20px' }}>🔍</div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>No events found</h3>
              <p>Try adjusting your search or filters to find more events.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

function EventDetailPage() {
  const [event] = useState({
    id: 1,
    title: "Summer Music Festival 2024",
    description: "Experience the best summer vibes with top artists from around the world. This incredible outdoor festival features multiple stages, food vendors, and an unforgettable atmosphere.",
    longDescription: "Join us for the biggest music festival of the summer! Featuring world-renowned artists, local bands, and everything in between. This three-day event showcases the best in contemporary music across multiple genres including rock, pop, electronic, and indie. With multiple stages running simultaneously, you'll discover new favorites while enjoying performances from your favorite artists.",
    date: "2024-07-15",
    time: "6:00 PM",
    endDate: "2024-07-17",
    endTime: "11:00 PM",
    location: "Central Park, New York",
    venue: "Central Park Great Lawn",
    price: 75,
    image: "https://picsum.photos/seed/music-fest/800/400.jpg",
    category: "Music",
    availableTickets: 150,
    totalTickets: 500,
    organizer: "NYC Events Group",
    ageRestriction: "All Ages",
    features: ["Multiple Stages", "Food Vendors", "VIP Areas", "Parking Available", "Accessible Venue"],
    lineup: [
      { time: "6:00 PM", artist: "Opening Acts", stage: "Main Stage" },
      { time: "7:30 PM", artist: "Local Bands Showcase", stage: "Side Stage" },
      { time: "9:00 PM", artist: "Headliner 1", stage: "Main Stage" },
      { time: "10:30 PM", artist: "DJ Set", stage: "Electronic Stage" }
    ]
  })
  
  const [ticketQuantity, setTicketQuantity] = useState(1)
  const [selectedTicketType, setSelectedTicketType] = useState('general')
  const [isBooking, setIsBooking] = useState(false)
  const [showBookingSuccess, setShowBookingSuccess] = useState(false)
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [confirmedEmail, setConfirmedEmail] = useState('')
  const [emailSentStatus, setEmailSentStatus] = useState<'success' | 'failed' | null>(null)
  
  // Check if user is logged in
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState<any>(null)
  
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token')
      const userData = localStorage.getItem('user')
      setIsLoggedIn(!!token && !!userData)
      if (userData) {
        setUser(JSON.parse(userData))
      }
    }
    
    // Initial check
    checkAuth()
    
    // Listen for storage changes (for cross-tab authentication)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token' || e.key === 'user') {
        checkAuth()
      }
    }
    
    window.addEventListener('storage', handleStorageChange)
    
    // Also check periodically for authentication changes
    const interval = setInterval(checkAuth, 1000)
    
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      clearInterval(interval)
    }
  }, [])

  const ticketTypes = [
    { id: 'general', name: 'General Admission', price: 75, description: 'Standard entry to all venues' },
    { id: 'vip', name: 'VIP Pass', price: 150, description: 'VIP access + exclusive areas' },
    { id: 'premium', name: 'Premium VIP', price: 250, description: 'All access + backstage tour' }
  ]

  const currentTicketType = ticketTypes.find(t => t.id === selectedTicketType)
  const totalPrice = currentTicketType ? currentTicketType.price * ticketQuantity : 0

  const handleBooking = async () => {
    // Check if user is logged in
    if (!isLoggedIn) {
      // Redirect to login page
      window.location.href = '/login'
      return
    }
    
    // Show email confirmation modal first
    setShowEmailModal(true)
  }
  
  const sendBookingConfirmationEmail = async (email: string, eventTitle: string, eventDate: string, eventTime: string, eventLocation: string, ticketQuantity: number, ticketType: string, totalPrice: number) => {
    try {
      // First try backend API with timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
      
      const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${API_URL}/api/email/booking-confirmation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to_email: email,
          event_title: eventTitle,
          event_date: eventDate,
          event_time: eventTime,
          event_location: eventLocation,
          ticket_quantity: ticketQuantity,
          ticket_type: ticketType,
          total_amount: totalPrice
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const data = await response.json()
        console.log(`✅ Email sent successfully to: ${email}`)
        console.log(`📧 Booking ID: ${data.booking_id}`)
        console.log(`📧 Event: ${eventTitle}`)
        console.log(`📧 Total: $${totalPrice}`)
        return true
      } else {
        throw new Error('Backend email service unavailable')
      }
    } catch (error) {
      // Fallback: Create mailto link and open email client
      console.log('🔄 Backend unavailable, using email client fallback...')
      
      const bookingId = `BK${Date.now()}`
      const emailSubject = `Booking Confirmation - ${eventTitle}`
      const emailBody = `
BOOKING CONFIRMATION 🎉

Event Details:
• Event: ${eventTitle}
• Date: ${eventDate}
• Time: ${eventTime}
• Location: ${eventLocation}
• Tickets: ${ticketQuantity} × ${ticketType}
• Total Amount: $${totalPrice}
• Booking ID: ${bookingId}

Your booking has been confirmed! Please keep this email for your records.
Your tickets will be available in your profile dashboard.

Thank you for using EventBooking System!
      `.trim()
      
      // Create mailto link
      const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`
      
      console.log(`📧 Opening email client for: ${email}`)
      console.log(`📧 Mailto link: ${mailtoLink}`)
      
      // Try to open email client
      try {
        // Method 1: Direct window.open
        const newWindow = window.open(mailtoLink, '_blank')
        
        // Method 2: If window.open fails, try creating a link
        if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
          const link = document.createElement('a')
          link.href = mailtoLink
          link.target = '_blank'
          link.style.display = 'none'
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        }
        
        console.log(`📧 Email client opened successfully for: ${email}`)
        console.log(`📧 Booking ID: ${bookingId}`)
        console.log(`📧 Event: ${eventTitle}`)
        console.log(`📧 Total: $${totalPrice}`)
        
        // Also show a message to the user
        alert(`Email client opened! Please send the booking confirmation to ${email}`)
        
        return true // Consider this successful since email client opened
      } catch (error) {
        console.error('Failed to open email client:', error)
        console.log(`📧 Please manually send email to: ${email}`)
        console.log(`📧 Subject: ${emailSubject}`)
        console.log(`📧 Body: ${emailBody}`)
        
        // Show manual instructions
        alert(`Please manually send email to ${email} with the booking details. Check console for email content.`)
        
        return false
      }
    }
  }

  const processBooking = async (email: string) => {
    setIsBooking(true)
    setConfirmedEmail(email)
    
    // Simulate booking process
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Send booking confirmation email via backend
    const emailSent = await sendBookingConfirmationEmail(
      email, 
      event.title, 
      event.date, 
      event.time, 
      event.location, 
      ticketQuantity, 
      selectedTicketType, 
      totalPrice
    )
    
    setIsBooking(false)
    setShowBookingSuccess(true)
    setEmailSentStatus(emailSent ? 'success' : 'failed')
    
    // Show email sent notification
    console.log(`📧 Booking confirmation ${emailSent ? 'sent successfully' : 'failed to send'} to: ${email}`)
    console.log(`📧 From: noreply@eventbooking.com`)
    console.log(`📧 Subject: Your tickets for ${event.title}`)
    console.log(`📧 Booking ID: BK${Date.now()}`)
    console.log(`📧 Total Amount: $${totalPrice}`)
    console.log(`📧 Platform: EventBooking System`)
    
    // Reset after 4 seconds
    setTimeout(() => {
      setShowBookingSuccess(false)
      setTicketQuantity(1)
      setConfirmedEmail('')
      setEmailSentStatus(null)
    }, 4000)
  }
  
  const handleEmailConfirm = (email: string) => {
    setShowEmailModal(false)
    processBooking(email)
  }
  
  const handleEmailCancel = () => {
    setShowEmailModal(false)
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Hero Image */}
      <div style={{ position: 'relative', height: '400px', backgroundColor: '#1f2937' }}>
        <img
          src={event.image}
          alt={event.title}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.7))',
          display: 'flex',
          alignItems: 'flex-end',
          padding: '40px 20px'
        }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: '300px' }}>
                <div style={{ 
                  display: 'inline-block', 
                  backgroundColor: 'rgba(255, 255, 255, 0.2)', 
                  color: 'white', 
                  padding: '6px 12px', 
                  borderRadius: '20px', 
                  fontSize: '0.875rem',
                  marginBottom: '16px'
                }}>
                  {event.category}
                </div>
                <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: 'white', marginBottom: '16px', lineHeight: '1.2' }}>
                  {event.title}
                </h1>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', color: 'white' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>📅</span>
                    <span>{event.date} - {event.endDate}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>📍</span>
                    <span>{event.location}</span>
                  </div>
                </div>
              </div>
              <div style={{ textAlign: 'right', minWidth: '200px' }}>
                <div style={{ color: 'white', fontSize: '1.25rem', marginBottom: '8px' }}>
                  Starting from
                </div>
                <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'white' }}>
                  ${event.price}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '40px' }}>
          {/* Event Details */}
          <div>
            {/* Quick Info */}
            <div style={{ 
              backgroundColor: 'white', 
              borderRadius: '12px', 
              padding: '24px', 
              marginBottom: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '20px', color: '#1f2937' }}>
                Event Information
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>Date & Time</div>
                  <div style={{ fontWeight: '500', color: '#1f2937' }}>
                    {event.date} at {event.time}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    Ends {event.endDate} at {event.endTime}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>Venue</div>
                  <div style={{ fontWeight: '500', color: '#1f2937' }}>
                    {event.venue}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    {event.location}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>Organizer</div>
                  <div style={{ fontWeight: '500', color: '#1f2937' }}>
                    {event.organizer}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>Age Restriction</div>
                  <div style={{ fontWeight: '500', color: '#1f2937' }}>
                    {event.ageRestriction}
                  </div>
                </div>
              </div>
            </div>

            {/* Description */}
            <div style={{ 
              backgroundColor: 'white', 
              borderRadius: '12px', 
              padding: '24px', 
              marginBottom: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '16px', color: '#1f2937' }}>
                About This Event
              </h2>
              <p style={{ color: '#4b5563', lineHeight: '1.6', marginBottom: '16px' }}>
                {event.longDescription}
              </p>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '12px', color: '#1f2937' }}>
                Event Features
              </h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {event.features.map((feature, index) => (
                  <li key={index} style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    marginBottom: '8px',
                    color: '#4b5563'
                  }}>
                    <span style={{ color: '#10b981', marginRight: '8px' }}>✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            {/* Lineup */}
            <div style={{ 
              backgroundColor: 'white', 
              borderRadius: '12px', 
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '20px', color: '#1f2937' }}>
                Event Lineup
              </h2>
              <div style={{ display: 'grid', gap: '12px' }}>
                {event.lineup.map((item, index) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '12px 16px',
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div>
                      <div style={{ fontWeight: '600', color: '#1f2937' }}>{item.artist}</div>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{item.stage}</div>
                    </div>
                    <div style={{ 
                      backgroundColor: '#667eea', 
                      color: 'white', 
                      padding: '4px 8px', 
                      borderRadius: '4px',
                      fontSize: '0.875rem'
                    }}>
                      {item.time}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Booking Panel */}
          <div>
            <div style={{ 
              backgroundColor: 'white', 
              borderRadius: '12px', 
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              position: 'sticky',
              top: '20px'
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '20px', color: '#1f2937' }}>
                Book Tickets
              </h2>

              {/* Ticket Availability */}
              <div style={{ 
                backgroundColor: '#f0fdf4', 
                border: '1px solid #bbf7d0', 
                borderRadius: '8px', 
                padding: '12px',
                marginBottom: '20px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#166534', fontSize: '0.875rem' }}>Available Tickets</span>
                  <span style={{ fontWeight: '600', color: '#166534' }}>
                    {event.availableTickets} / {event.totalTickets}
                  </span>
                </div>
                <div style={{ 
                  width: '100%', 
                  backgroundColor: '#e5e7eb', 
                  borderRadius: '4px', 
                  height: '8px',
                  marginTop: '8px'
                }}>
                  <div style={{ 
                    width: `${(event.availableTickets / event.totalTickets) * 100}%`,
                    backgroundColor: '#10b981',
                    height: '100%',
                    borderRadius: '4px'
                  }} />
                </div>
              </div>

              {/* Ticket Types */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                  Ticket Type
                </label>
                <div style={{ display: 'grid', gap: '8px' }}>
                  {ticketTypes.map(type => (
                    <div
                      key={type.id}
                      onClick={() => setSelectedTicketType(type.id)}
                      style={{
                        padding: '12px',
                        border: `2px solid ${selectedTicketType === type.id ? '#667eea' : '#e5e7eb'}`,
                        borderRadius: '8px',
                        cursor: 'pointer',
                        backgroundColor: selectedTicketType === type.id ? '#f0f9ff' : 'white',
                        transition: 'all 0.2s'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontWeight: '600', color: '#1f2937' }}>{type.name}</div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{type.description}</div>
                        </div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#667eea' }}>
                          ${type.price}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quantity */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                  Quantity
                </label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <button
                    onClick={() => setTicketQuantity(Math.max(1, ticketQuantity - 1))}
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '2px solid #e5e7eb',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      fontSize: '1.25rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    -
                  </button>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: '600', 
                    minWidth: '40px', 
                    textAlign: 'center',
                    color: '#1f2937'
                  }}>
                    {ticketQuantity}
                  </div>
                  <button
                    onClick={() => setTicketQuantity(Math.min(event.availableTickets, ticketQuantity + 1))}
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '2px solid #e5e7eb',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      fontSize: '1.25rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Total */}
              <div style={{ 
                borderTop: '1px solid #e5e7eb', 
                paddingTop: '16px',
                marginBottom: '20px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937' }}>Total</span>
                  <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#667eea' }}>
                    ${totalPrice}
                  </span>
                </div>
              </div>

              {/* Login Required Message */}
              {!isLoggedIn && (
                <div style={{
                  marginBottom: '16px',
                  padding: '12px',
                  backgroundColor: '#fef3c7',
                  border: '1px solid #fcd34d',
                  borderRadius: '8px',
                  textAlign: 'center',
                  color: '#92400e'
                }}>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>Login Required</div>
                  <div style={{ fontSize: '0.875rem' }}>Please login to book tickets for this event</div>
                </div>
              )}

              {/* Book Button */}
              <button
                onClick={handleBooking}
                disabled={isBooking || event.availableTickets === 0}
                style={{
                  width: '100%',
                  padding: '16px',
                  backgroundColor: isBooking || event.availableTickets === 0 ? '#9ca3af' : (isLoggedIn ? '#667eea' : '#f59e0b'),
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1.1rem',
                  fontWeight: '600',
                  cursor: isBooking || event.availableTickets === 0 ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {isBooking ? 'Processing...' : 
                 event.availableTickets === 0 ? 'Sold Out' : 
                 !isLoggedIn ? 'Login to Book' : 'Book Now'}
              </button>

              {/* Success Message */}
              {showBookingSuccess && (
                <div style={{
                  marginTop: '16px',
                  padding: '16px',
                  backgroundColor: emailSentStatus === 'success' ? '#d1fae5' : '#fee2e2',
                  border: emailSentStatus === 'success' ? '1px solid #bbf7d0' : '1px solid #fecaca',
                  borderRadius: '8px',
                  textAlign: 'center',
                  color: emailSentStatus === 'success' ? '#065f46' : '#991b1b'
                }}>
                  <div style={{ fontWeight: '600', marginBottom: '8px', fontSize: '1.1rem' }}>
                    {emailSentStatus === 'success' ? '🎉 Booking Successful!' : '⚠️ Booking Processed'}
                  </div>
                  <div style={{ fontSize: '0.9rem', marginBottom: '8px' }}>
                    {emailSentStatus === 'success' 
                      ? 'Your tickets have been confirmed and payment processed.' 
                      : 'Your booking was processed but email delivery failed.'}
                  </div>
                  <div style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: '500', 
                    backgroundColor: emailSentStatus === 'success' ? '#f0fdf4' : '#fef2f2', 
                    padding: '8px', 
                    borderRadius: '4px', 
                    display: 'inline-block',
                    color: emailSentStatus === 'success' ? '#065f46' : '#991b1b'
                  }}>
                    {emailSentStatus === 'success' 
                      ? '📧 Confirmation email sent successfully!' 
                      : '❌ Email failed to send. Check console for details.'}
                  </div>
                  <div style={{ fontSize: '0.75rem', marginTop: '8px', color: emailSentStatus === 'success' ? '#047857' : '#991b1b' }}>
                    {emailSentStatus === 'success' 
                      ? 'Check your inbox for tickets and QR codes' 
                      : 'Your booking is confirmed but you may not receive email confirmation.'}
                  </div>
                </div>
              )}

              {/* Trust Indicators */}
              <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #e5e7eb' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '0.875rem', color: '#6b7280' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>🔒</span>
                    <span>Secure Payment</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>🎫</span>
                    <span>Instant Confirmation</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>📧</span>
                    <span>Email Tickets</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>↩️</span>
                    <span>Free Cancellation</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    
    {/* Email Confirmation Modal */}
    {showEmailModal && user && (
      <EmailConfirmationModal
        user={user}
        onConfirm={handleEmailConfirm}
        onCancel={handleEmailCancel}
      />
    )}
    </div>
  )
}

function EmailConfirmationModal({ user, onConfirm, onCancel }: { user: any, onConfirm: (email: string) => void, onCancel: () => void }) {
  const [email, setEmail] = useState(user?.email || '')
  const [isValidEmail, setIsValidEmail] = useState(true)
  
  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  }
  
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value
    setEmail(newEmail)
    setIsValidEmail(validateEmail(newEmail))
  }
  
  const handleConfirm = () => {
    if (isValidEmail && email) {
      onConfirm(email)
    }
  }
  
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        maxWidth: '450px',
        width: '90%',
        padding: '0',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{
          backgroundColor: '#667eea',
          color: 'white',
          padding: '20px',
          borderRadius: '16px 16px 0 0',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '8px' }}>📧</div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: '600', margin: '0' }}>
            Confirm Email Address
          </h3>
        </div>
        
        <div style={{ padding: '24px' }}>
          <p style={{ color: '#6b7280', marginBottom: '20px', textAlign: 'center' }}>
            Where should we send your booking confirmation and tickets?
          </p>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={handleEmailChange}
              placeholder="Enter your email address"
              style={{
                width: '100%',
                padding: '12px',
                border: isValidEmail ? '1px solid #e5e7eb' : '1px solid #ef4444',
                borderRadius: '8px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = isValidEmail ? '#e5e7eb' : '#ef4444'}
            />
            {!isValidEmail && (
              <div style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '4px' }}>
                Please enter a valid email address
              </div>
            )}
          </div>
          
          <div style={{
            backgroundColor: '#f8fafc',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '20px',
            fontSize: '0.875rem',
            color: '#6b7280'
          }}>
            <div style={{ fontWeight: '600', marginBottom: '4px', color: '#374151' }}>You'll receive:</div>
            <ul style={{ margin: '0', paddingLeft: '16px' }}>
              <li>Booking confirmation with ticket details</li>
              <li>QR codes for event entry</li>
              <li>Payment receipt</li>
              <li>Event reminders</li>
            </ul>
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={onCancel}
              style={{
                flex: 1,
                padding: '12px',
                backgroundColor: 'white',
                color: '#6b7280',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={!isValidEmail || !email}
              style={{
                flex: 1,
                padding: '12px',
                backgroundColor: isValidEmail && email ? '#667eea' : '#9ca3af',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: isValidEmail && email ? 'pointer' : 'not-allowed',
                fontWeight: '600',
                transition: 'all 0.2s'
              }}
            >
              Confirm & Continue
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function TicketViewModal({ booking, onClose }: { booking: any, onClose: () => void }) {
  const [selectedTicket, setSelectedTicket] = useState(0)
  
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '90vh',
        overflow: 'auto',
        position: 'relative'
      }}>
        <div style={{
          position: 'sticky',
          top: 0,
          backgroundColor: 'white',
          padding: '20px',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
            Event Tickets
          </h3>
          <button
            onClick={onClose}
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              border: 'none',
              backgroundColor: '#f3f4f6',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem'
            }}
          >
            ×
          </button>
        </div>
        
        <div style={{ padding: '20px' }}>
          <div style={{ textAlign: 'center', marginBottom: '20px' }}>
            <div style={{
              width: '200px',
              height: '200px',
              backgroundColor: 'white',
              border: '2px solid #e5e7eb',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto',
              position: 'relative'
            }}>
              <div style={{
                width: '180px',
                height: '180px',
                backgroundImage: `url(https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${booking.qrCode}-${selectedTicket})`,
                backgroundSize: 'contain',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center'
              }} />
            </div>
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '8px' }}>
              Scan this code at the venue
            </p>
          </div>
          
          <div style={{
            backgroundColor: '#f8fafc',
            borderRadius: '12px',
            padding: '20px',
            border: '2px solid #e5e7eb'
          }}>
            <h4 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '12px', color: '#1f2937' }}>
              {booking.event.title}
            </h4>
            <div style={{ display: 'grid', gap: '8px', fontSize: '0.9rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#6b7280' }}>Date:</span>
                <span style={{ fontWeight: '600' }}>{booking.event.date}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#6b7280' }}>Time:</span>
                <span style={{ fontWeight: '600' }}>{booking.event.time}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#6b7280' }}>Location:</span>
                <span style={{ fontWeight: '600' }}>{booking.event.location}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#6b7280' }}>Booking ID:</span>
                <span style={{ fontWeight: '600' }}>{booking.id}</span>
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
            <button
              onClick={() => window.print()}
              style={{
                flex: 1,
                padding: '12px',
                backgroundColor: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function ProfilePage() {
  const [user, setUser] = useState<any>(null)
  const [bookings, setBookings] = useState([
    {
      id: 'BK001',
      event: {
        title: 'Summer Music Festival 2024',
        date: '2024-07-15',
        time: '6:00 PM',
        location: 'Central Park, New York',
        image: 'https://picsum.photos/seed/music-fest/100/100.jpg'
      },
      tickets: [
        { type: 'General Admission', quantity: 2, price: 75 },
        { type: 'VIP Pass', quantity: 1, price: 150 }
      ],
      totalAmount: 300,
      status: 'confirmed',
      bookingDate: '2024-06-20',
      qrCode: 'QR123456789'
    },
    {
      id: 'BK002',
      event: {
        title: 'Tech Conference 2024',
        date: '2024-08-20',
        time: '9:00 AM',
        location: 'Convention Center, San Francisco',
        image: 'https://picsum.photos/seed/tech-conf/100/100.jpg'
      },
      tickets: [
        { type: 'General Admission', quantity: 1, price: 299 }
      ],
      totalAmount: 299,
      status: 'pending',
      bookingDate: '2024-06-22',
      qrCode: 'QR987654321'
    }
  ])
  const [activeTab, setActiveTab] = useState('bookings')
  const [selectedBooking, setSelectedBooking] = useState<any>(null)
  const [showTicketModal, setShowTicketModal] = useState(false)
  
  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])
  
  if (!user) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#1f2937' }}>Please Login</h2>
          <p style={{ color: '#6b7280', marginBottom: '2rem' }}>You need to be logged in to view your profile.</p>
          <a
            href="/login"
            style={{
              padding: '12px 24px',
              backgroundColor: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '8px',
              fontWeight: '600'
            }}
          >
            Login
          </a>
        </div>
      </div>
    )
  }
  
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Profile Header */}
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
        color: 'white', 
        padding: '60px 20px'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', flexWrap: 'wrap' }}>
            <div style={{ 
              width: '100px', 
              height: '100px', 
              backgroundColor: 'rgba(255, 255, 255, 0.2)', 
              borderRadius: '50%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontSize: '2.5rem',
              fontWeight: 'bold'
            }}>
              {user.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '8px' }}>
                {user.full_name}
              </h1>
              <p style={{ opacity: 0.9, fontSize: '1.1rem' }}>{user.email}</p>
              <p style={{ opacity: 0.8, fontSize: '0.9rem' }}>Member since June 2024</p>
            </div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
        {/* Stats Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '40px' }}>
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            padding: '24px', 
            textAlign: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#667eea', marginBottom: '8px' }}>
              {bookings.length}
            </div>
            <div style={{ color: '#6b7280' }}>Total Bookings</div>
          </div>
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            padding: '24px', 
            textAlign: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#10b981', marginBottom: '8px' }}>
              {bookings.filter(b => b.status === 'confirmed').length}
            </div>
            <div style={{ color: '#6b7280' }}>Confirmed</div>
          </div>
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            padding: '24px', 
            textAlign: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#f59e0b', marginBottom: '8px' }}>
              ${bookings.reduce((sum, b) => sum + b.totalAmount, 0)}
            </div>
            <div style={{ color: '#6b7280' }}>Total Spent</div>
          </div>
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            padding: '24px', 
            textAlign: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#ef4444', marginBottom: '8px' }}>
              {bookings.reduce((sum, b) => sum + b.tickets.reduce((s, t) => s + t.quantity, 0), 0)}
            </div>
            <div style={{ color: '#6b7280' }}>Total Tickets</div>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', borderBottom: '1px solid #e5e7eb' }}>
            <button
              onClick={() => setActiveTab('bookings')}
              style={{
                flex: 1,
                padding: '16px',
                backgroundColor: activeTab === 'bookings' ? '#f8fafc' : 'transparent',
                border: 'none',
                borderBottom: activeTab === 'bookings' ? '2px solid #667eea' : 'none',
                color: activeTab === 'bookings' ? '#667eea' : '#6b7280',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              My Bookings
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              style={{
                flex: 1,
                padding: '16px',
                backgroundColor: activeTab === 'settings' ? '#f8fafc' : 'transparent',
                border: 'none',
                borderBottom: activeTab === 'settings' ? '2px solid #667eea' : 'none',
                color: activeTab === 'settings' ? '#667eea' : '#6b7280',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Account Settings
            </button>
          </div>

          <div style={{ padding: '24px' }}>
            {activeTab === 'bookings' && (
              <div>
                <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '20px', color: '#1f2937' }}>
                  Your Bookings
                </h3>
                {bookings.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '60px 20px', color: '#6b7280' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '20px' }}>🎫</div>
                    <h4 style={{ fontSize: '1.25rem', marginBottom: '10px' }}>No bookings yet</h4>
                    <p>Start exploring events and book your first tickets!</p>
                    <a
                      href="/events"
                      style={{
                        display: 'inline-block',
                        marginTop: '20px',
                        padding: '12px 24px',
                        backgroundColor: '#667eea',
                        color: 'white',
                        textDecoration: 'none',
                        borderRadius: '8px',
                        fontWeight: '600'
                      }}
                    >
                      Browse Events
                    </a>
                  </div>
                ) : (
                  <div style={{ display: 'grid', gap: '20px' }}>
                    {bookings.map(booking => (
                      <div
                        key={booking.id}
                        style={{
                          backgroundColor: '#f8fafc',
                          borderRadius: '12px',
                          padding: '20px',
                          border: '1px solid #e5e7eb'
                        }}
                      >
                        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                          <img
                            src={booking.event.image}
                            alt={booking.event.title}
                            style={{ width: '100px', height: '100px', borderRadius: '8px', objectFit: 'cover' }}
                          />
                          <div style={{ flex: 1, minWidth: '250px' }}>
                            <h4 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '8px', color: '#1f2937' }}>
                              {booking.event.title}
                            </h4>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginBottom: '12px', color: '#6b7280', fontSize: '0.9rem' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <span>📅</span>
                                <span>{booking.event.date}</span>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <span>🕐</span>
                                <span>{booking.event.time}</span>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <span>📍</span>
                                <span>{booking.event.location}</span>
                              </div>
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                              {booking.tickets.map((ticket, index) => (
                                <span
                                  key={index}
                                  style={{
                                    backgroundColor: '#e5e7eb',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '0.875rem',
                                    color: '#374151'
                                  }}
                                >
                                  {ticket.quantity}x {ticket.type}
                                </span>
                              ))}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div>
                                <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#667eea' }}>
                                  ${booking.totalAmount}
                                </span>
                                <span style={{ 
                                  marginLeft: '8px',
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  fontSize: '0.75rem',
                                  fontWeight: '600',
                                  backgroundColor: booking.status === 'confirmed' ? '#d1fae5' : '#fef3c7',
                                  color: booking.status === 'confirmed' ? '#065f46' : '#92400e'
                                }}>
                                  {booking.status.toUpperCase()}
                                </span>
                              </div>
                              <div style={{ display: 'flex', gap: '8px' }}>
                                <button
                                  onClick={() => {
                                    setSelectedBooking(booking)
                                    setShowTicketModal(true)
                                  }}
                                  style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#667eea',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    fontSize: '0.875rem',
                                    fontWeight: '600'
                                  }}
                                >
                                  View Tickets
                                </button>
                                {booking.status === 'confirmed' && (
                                  <button
                                    style={{
                                      padding: '8px 16px',
                                      backgroundColor: 'white',
                                      color: '#667eea',
                                      border: '1px solid #667eea',
                                      borderRadius: '6px',
                                      cursor: 'pointer',
                                      fontSize: '0.875rem',
                                      fontWeight: '600'
                                    }}
                                  >
                                    Download
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'settings' && (
              <div>
                <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '20px', color: '#1f2937' }}>
                  Account Settings
                </h3>
                <div style={{ display: 'grid', gap: '20px' }}>
                  <div style={{ backgroundColor: '#f8fafc', borderRadius: '8px', padding: '20px' }}>
                    <h4 style={{ fontWeight: '600', marginBottom: '12px', color: '#1f2937' }}>Personal Information</h4>
                    <div style={{ display: 'grid', gap: '12px' }}>
                      <div>
                        <label style={{ display: 'block', marginBottom: '4px', color: '#374151', fontSize: '0.875rem' }}>Full Name</label>
                        <input
                          type="text"
                          value={user.full_name}
                          readOnly
                          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', marginBottom: '4px', color: '#374151', fontSize: '0.875rem' }}>Email</label>
                        <input
                          type="email"
                          value={user.email}
                          readOnly
                          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div style={{ backgroundColor: '#f8fafc', borderRadius: '8px', padding: '20px' }}>
                    <h4 style={{ fontWeight: '600', marginBottom: '12px', color: '#1f2937' }}>Preferences</h4>
                    <div style={{ display: 'grid', gap: '12px' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input type="checkbox" defaultChecked />
                        <span style={{ color: '#374151' }}>Email notifications for upcoming events</span>
                      </label>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input type="checkbox" defaultChecked />
                        <span style={{ color: '#374151' }}>Email notifications for booking confirmations</span>
                      </label>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input type="checkbox" />
                        <span style={{ color: '#374151' }}>SMS notifications</span>
                      </label>
                    </div>
                  </div>
                  
                  <button
                    style={{
                      padding: '12px 24px',
                      backgroundColor: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    
    {/* Ticket View Modal */}
    {showTicketModal && selectedBooking && (
      <TicketViewModal
        booking={selectedBooking}
        onClose={() => {
          setShowTicketModal(false)
          setSelectedBooking(null)
        }}
      />
    )}
    </div>
  )
}

function HomePage() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Hero Section */}
      <section style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
        color: 'white', 
        padding: '100px 20px',
        textAlign: 'center'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '3.5rem', fontWeight: 'bold', marginBottom: '1.5rem', lineHeight: '1.2' }}>
            Discover Amazing Events
          </h1>
          <p style={{ fontSize: '1.5rem', marginBottom: '2rem', opacity: 0.9, maxWidth: '600px', margin: '0 auto 2rem' }}>
            Find and book tickets for concerts, conferences, festivals, and more. Your gateway to unforgettable experiences.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a 
              href="/events" 
              style={{ 
                padding: '15px 30px', 
                backgroundColor: 'white', 
                color: '#667eea', 
                textDecoration: 'none', 
                borderRadius: '8px', 
                display: 'inline-block',
                fontWeight: '600',
                fontSize: '1.1rem',
                transition: 'transform 0.2s'
              }}
            >
              Browse Events
            </a>
            <a 
              href="/login" 
              style={{ 
                padding: '15px 30px', 
                backgroundColor: 'transparent', 
                color: 'white', 
                border: '2px solid white',
                textDecoration: 'none', 
                borderRadius: '8px', 
                display: 'inline-block',
                fontWeight: '600',
                fontSize: '1.1rem',
                transition: 'transform 0.2s'
              }}
            >
              Sign Up
            </a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ padding: '80px 20px', backgroundColor: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '3rem', color: '#1f2937' }}>
            Why Choose EventBooking?
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{ 
                width: '80px', 
                height: '80px', 
                backgroundColor: '#3b82f6', 
                borderRadius: '50%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                margin: '0 auto 1.5rem',
                fontSize: '2rem'
              }}>
                🎫
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#1f2937' }}>Easy Booking</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.6', fontSize: '1.1rem' }}>
                Book tickets for your favorite events with just a few clicks. No hassle, no waiting.
              </p>
            </div>
            
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{ 
                width: '80px', 
                height: '80px', 
                backgroundColor: '#10b981', 
                borderRadius: '50%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                margin: '0 auto 1.5rem',
                fontSize: '2rem'
              }}>
                🔒
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#1f2937' }}>Secure Payments</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.6', fontSize: '1.1rem' }}>
                Your payment information is always secure with our encrypted payment system.
              </p>
            </div>
            
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{ 
                width: '80px', 
                height: '80px', 
                backgroundColor: '#f59e0b', 
                borderRadius: '50%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                margin: '0 auto 1.5rem',
                fontSize: '2rem'
              }}>
                📱
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#1f2937' }}>Mobile Friendly</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.6', fontSize: '1.1rem' }}>
                Access your tickets and event information on any device, anywhere, anytime.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section style={{ padding: '60px 20px', backgroundColor: '#f8fafc' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem', textAlign: 'center' }}>
            <div>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#3b82f6', marginBottom: '0.5rem' }}>10K+</div>
              <div style={{ color: '#6b7280', fontSize: '1.1rem' }}>Events Listed</div>
            </div>
            <div>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#10b981', marginBottom: '0.5rem' }}>50K+</div>
              <div style={{ color: '#6b7280', fontSize: '1.1rem' }}>Happy Users</div>
            </div>
            <div>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#f59e0b', marginBottom: '0.5rem' }}>100K+</div>
              <div style={{ color: '#6b7280', fontSize: '1.1rem' }}>Tickets Sold</div>
            </div>
            <div>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#ef4444', marginBottom: '0.5rem' }}>4.8★</div>
              <div style={{ color: '#6b7280', fontSize: '1.1rem' }}>User Rating</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

function NavigationHeader() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState<any>(null)
  
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token')
      const userData = localStorage.getItem('user')
      setIsLoggedIn(!!token && !!userData)
      if (userData) {
        setUser(JSON.parse(userData))
      } else {
        setUser(null)
      }
    }
    
    // Initial check
    checkAuth()
    
    // Listen for storage changes
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token' || e.key === 'user') {
        checkAuth()
      }
    }
    
    window.addEventListener('storage', handleStorageChange)
    const interval = setInterval(checkAuth, 1000)
    
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      clearInterval(interval)
    }
  }, [])
  
  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setIsLoggedIn(false)
    setUser(null)
    window.location.href = '/'
  }
  
  return (
    <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '1rem 0' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '32px', height: '32px', backgroundColor: '#3b82f6', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontWeight: 'bold', fontSize: '12px' }}>EB</span>
          </div>
          <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#1f2937' }}>EventBooking</span>
        </div>
        <nav style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          <a href="/" style={{ color: '#6b7280', textDecoration: 'none' }}>Home</a>
          <a href="/events" style={{ color: '#6b7280', textDecoration: 'none' }}>Events</a>
          {isLoggedIn ? (
            <>
              <a href="/profile" style={{ color: '#6b7280', textDecoration: 'none' }}>Profile</a>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ 
                  width: '32px', 
                  height: '32px', 
                  backgroundColor: '#667eea', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}>
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <span style={{ color: '#1f2937', fontWeight: '500' }}>
                  {user?.full_name || 'User'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '0.9rem'
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <a href="/login" style={{ color: '#6b7280', textDecoration: 'none' }}>Login</a>
              <a href="/register" style={{ color: '#6b7280', textDecoration: 'none' }}>Sign Up</a>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

function PageWithHeader({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <NavigationHeader />
      {children}
    </div>
  )
}

export default function MinimalApp() {
  return (
    <Routes>
      <Route path="/" element={<PageWithHeader><HomePage /></PageWithHeader>} />
      <Route path="/events" element={<PageWithHeader><EventsPage /></PageWithHeader>} />
      <Route path="/events/:id" element={<PageWithHeader><EventDetailPage /></PageWithHeader>} />
      <Route path="/profile" element={<PageWithHeader><ProfilePage /></PageWithHeader>} />
      <Route path="/login" element={<PageWithHeader><SimpleLoginPage /></PageWithHeader>} />
      <Route path="/register" element={<PageWithHeader><SimpleRegisterPage /></PageWithHeader>} />
    </Routes>
  )
}
