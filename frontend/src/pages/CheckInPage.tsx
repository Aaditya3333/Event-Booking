import { useState } from 'react'
import { QRCodeScanner } from '../components/QRCodeScanner'

export function CheckInPage() {
  const [scanResult, setScanResult] = useState<string | null>(null)
  const [checkInStatus, setCheckInStatus] = useState<'idle' | 'scanning' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState<string>('')

  const handleScanSuccess = async (ticketNumber: string) => {
    setScanResult(ticketNumber)
    setCheckInStatus('scanning')
    
    try {
      // Simulate API call to validate and check in ticket
      const response = await fetch(`/api/tickets/checkin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticket_number: ticketNumber,
          check_in_location: 'Main Entrance',
          device_id: 'web-scanner-001'
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setCheckInStatus('success')
      } else {
        const error = await response.json()
        setErrorMessage(error.detail || 'Check-in failed')
        setCheckInStatus('error')
      }
    } catch (error) {
      setErrorMessage('Network error. Please try again.')
      setCheckInStatus('error')
    }
  }

  const handleScanError = (error: string) => {
    setErrorMessage(error)
    setCheckInStatus('error')
  }

  const resetScanner = () => {
    setScanResult(null)
    setCheckInStatus('idle')
    setErrorMessage('')
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '2rem 0' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '0 1rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem', color: '#1f2937' }}>
          Event Check-In
        </h1>
        
        <div style={{ 
          backgroundColor: 'white', 
          padding: '2rem', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          marginBottom: '2rem'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem', color: '#1f2937' }}>
              Scan QR Code
            </h2>
            <p style={{ color: '#6b7280' }}>
              Scan the QR code on the attendee's ticket to check them in
            </p>
          </div>
          
          {checkInStatus === 'idle' && (
            <QRCodeScanner 
              onScanSuccess={handleScanSuccess}
              onError={handleScanError}
            />
          )}
          
          {checkInStatus === 'scanning' && (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{
                width: '60px',
                height: '60px',
                border: '4px solid #3b82f6',
                borderTop: '4px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 1rem'
              }}></div>
              <p style={{ color: '#6b7280' }}>Processing ticket...</p>
            </div>
          )}
          
          {checkInStatus === 'success' && (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{
                width: '60px',
                height: '60px',
                backgroundColor: '#22c55e',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem'
              }}>
                <span style={{ color: 'white', fontSize: '1.5rem' }}>✓</span>
              </div>
              <h3 style={{ color: '#16a34a', fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                Check-In Successful!
              </h3>
              <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
                Ticket {scanResult} has been successfully checked in.
              </p>
              <button
                onClick={resetScanner}
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Scan Next Ticket
              </button>
            </div>
          )}
          
          {checkInStatus === 'error' && (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{
                width: '60px',
                height: '60px',
                backgroundColor: '#ef4444',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem'
              }}>
                <span style={{ color: 'white', fontSize: '1.5rem' }}>✕</span>
              </div>
              <h3 style={{ color: '#dc2626', fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                Check-In Failed
              </h3>
              <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
                {errorMessage}
              </p>
              <button
                onClick={resetScanner}
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Try Again
              </button>
            </div>
          )}
        </div>
        
        <div style={{ 
          backgroundColor: 'white', 
          padding: '1.5rem', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
            Manual Check-In
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
            If QR code scanning is not working, you can manually enter the ticket number:
          </p>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <input
              type="text"
              placeholder="Enter ticket number"
              style={{
                flex: 1,
                padding: '0.75rem',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                outline: 'none'
              }}
            />
            <button
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '0.75rem 1.5rem',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Check In
            </button>
          </div>
        </div>
      </div>
      
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
