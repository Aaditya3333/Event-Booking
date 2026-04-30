export default function TestAuth() {
  const testAPI = async () => {
    try {
      console.log('Testing API connection...')
      const response = await fetch('http://localhost:8000/health')
      const data = await response.json()
      console.log('API Response:', data)
      alert('API is working! Check console for details.')
    } catch (error) {
      console.error('API Error:', error)
      alert('API connection failed. Check console for details.')
    }
  }

  const testLogin = async () => {
    try {
      console.log('Testing login...')
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'test123'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('Login Response:', data)
        alert('Login working! Check console for details.')
      } else {
        console.error('Login failed:', response.status)
        alert('Login failed. Check console for details.')
      }
    } catch (error) {
      console.error('Login Error:', error)
      alert('Login connection failed. Check console for details.')
    }
  }

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Authentication Test Page</h1>
      <p>This page tests if the authentication API is working.</p>
      
      <div style={{ margin: '20px 0' }}>
        <button 
          onClick={testAPI}
          style={{ 
            padding: '10px 20px', 
            margin: '5px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test API Connection
        </button>
        
        <button 
          onClick={testLogin}
          style={{ 
            padding: '10px 20px', 
            margin: '5px', 
            backgroundColor: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test Login
        </button>
      </div>
      
      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <p>Open the browser console (F12) to see detailed API responses.</p>
      </div>
    </div>
  )
}
