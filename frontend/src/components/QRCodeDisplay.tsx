import { useState, useEffect } from 'react'

interface QRCodeDisplayProps {
  ticketNumber: string
  eventName: string
  holderName: string
  holderEmail: string
  size?: number
}

export function QRCodeDisplay({ 
  ticketNumber, 
  eventName, 
  holderName, 
  holderEmail, 
  size = 200 
}: QRCodeDisplayProps) {
  const [qrCodeUrl, setQrCodeUrl] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    generateQRCode()
  }, [ticketNumber])

  const generateQRCode = async () => {
    setIsLoading(true)
    setError('')
    
    try {
      // Generate QR code data
      const qrData = JSON.stringify({
        ticketNumber,
        eventName,
        holderName,
        holderEmail,
        timestamp: new Date().toISOString()
      })

      // Use a simple QR code generation service or library
      // For now, we'll use a placeholder approach
      const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(qrData)}`
      
      setQrCodeUrl(qrCodeUrl)
    } catch (err) {
      setError('Failed to generate QR code')
      console.error('QR code generation error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const downloadQRCode = () => {
    if (qrCodeUrl) {
      const link = document.createElement('a')
      link.href = qrCodeUrl
      link.download = `ticket-${ticketNumber}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <div style={{
          width: size,
          height: size,
          border: '2px dashed #d1d5db',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto'
        }}>
          <span style={{ color: '#6b7280' }}>Loading QR Code...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <div style={{
          width: size,
          height: size,
          border: '2px solid #ef4444',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto'
        }}>
          <span style={{ color: '#ef4444' }}>Error</span>
        </div>
        <p style={{ color: '#ef4444', marginTop: '0.5rem' }}>{error}</p>
      </div>
    )
  }

  return (
    <div style={{ textAlign: 'center', padding: '2rem' }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        maxWidth: '400px',
        margin: '0 auto'
      }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem', color: '#1f2937' }}>
          Event Ticket
        </h3>
        
        <div style={{ marginBottom: '1rem' }}>
          <img 
            src={qrCodeUrl} 
            alt={`QR Code for ticket ${ticketNumber}`}
            style={{ 
              width: size, 
              height: size, 
              border: '2px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
        </div>
        
        <div style={{ textAlign: 'left', fontSize: '0.875rem', color: '#6b7280' }}>
          <p style={{ marginBottom: '0.5rem' }}><strong>Event:</strong> {eventName}</p>
          <p style={{ marginBottom: '0.5rem' }}><strong>Ticket #:</strong> {ticketNumber}</p>
          <p style={{ marginBottom: '0.5rem' }}><strong>Holder:</strong> {holderName}</p>
          <p style={{ marginBottom: '0.5rem' }}><strong>Email:</strong> {holderEmail}</p>
        </div>
        
        <button
          onClick={downloadQRCode}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '0.875rem',
            marginTop: '1rem',
            width: '100%'
          }}
        >
          Download QR Code
        </button>
      </div>
    </div>
  )
}
