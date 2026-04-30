import { useState, useRef, useEffect } from 'react'

interface QRCodeScannerProps {
  onScanSuccess: (ticketNumber: string) => void
  onError?: (error: string) => void
}

export function QRCodeScanner({ onScanSuccess, onError }: QRCodeScannerProps) {
  const [isScanning, setIsScanning] = useState(false)
  const [scanResult, setScanResult] = useState<string | null>(null)
  const videoRef = useRef<HTMLDivElement>(null)
  const [scanner, setScanner] = useState<any>(null)

  const startScanning = async () => {
    setIsScanning(true)
    setScanResult(null)
    
    try {
      // Dynamically import html5-qrcode to avoid SSR issues
      const { Html5QrcodeScanner } = await import('html5-qrcode')
      
      const qrScanner = new Html5QrcodeScanner(
        'qr-reader',
        { fps: 10, qrbox: { width: 250, height: 250 } },
        false
      )
      
      qrScanner.render(
        (decodedText: string) => {
          setScanResult(decodedText)
          onScanSuccess(decodedText)
          qrScanner.clear()
          setIsScanning(false)
        },
        (error: any) => {
          console.warn('QR scan error:', error)
        }
      )
      
      setScanner(qrScanner)
    } catch (error) {
      console.error('Failed to start QR scanner:', error)
      setIsScanning(false)
      onError?.('Failed to start QR scanner')
    }
  }

  const stopScanning = () => {
    if (scanner) {
      scanner.clear()
      setScanner(null)
    }
    setIsScanning(false)
  }

  useEffect(() => {
    return () => {
      if (scanner) {
        scanner.clear()
      }
    }
  }, [scanner])

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: '#1f2937' }}>
        QR Code Scanner
      </h2>
      
      {!isScanning ? (
        <div>
          <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
            Click the button below to start scanning QR codes for event check-in
          </p>
          <button
            onClick={startScanning}
            style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Start Scanning
          </button>
        </div>
      ) : (
        <div>
          <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
            Position the QR code within the scanner frame
          </p>
          <div id="qr-reader" style={{ maxWidth: '400px', margin: '0 auto' }}></div>
          <button
            onClick={stopScanning}
            style={{
              backgroundColor: '#ef4444',
              color: 'white',
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '1rem',
              marginTop: '1rem'
            }}
          >
            Stop Scanning
          </button>
        </div>
      )}
      
      {scanResult && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: '#f0fdf4',
          border: '1px solid #22c55e',
          borderRadius: '6px'
        }}>
          <p style={{ color: '#16a34a', fontWeight: '600' }}>Scan Result:</p>
          <p style={{ color: '#15803d', fontFamily: 'monospace' }}>{scanResult}</p>
        </div>
      )}
    </div>
  )
}
