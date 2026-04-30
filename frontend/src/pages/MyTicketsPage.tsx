import { useState } from 'react'
import { QRCodeDisplay } from '../components/QRCodeDisplay'

export function MyTicketsPage() {
  const [selectedTicket, setSelectedTicket] = useState<any>(null)
  
  // Sample ticket data - in a real app, this would come from API
  const [tickets] = useState([
    {
      id: 1,
      ticket_number: 'TKT-2024-001',
      event_name: 'Summer Music Festival',
      holder_name: 'John Doe',
      holder_email: 'john.doe@example.com',
      event_date: '2024-07-15',
      event_time: '18:00',
      venue: 'Central Park Amphitheater',
      status: 'active',
      qr_code: 'TKT-2024-001'
    },
    {
      id: 2,
      ticket_number: 'TKT-2024-002',
      event_name: 'Tech Conference 2024',
      holder_name: 'John Doe',
      holder_email: 'john.doe@example.com',
      event_date: '2024-09-20',
      event_time: '09:00',
      venue: 'Convention Center',
      status: 'active',
      qr_code: 'TKT-2024-002'
    }
  ])

  const handleViewQRCode = (ticket: any) => {
    setSelectedTicket(ticket)
  }

  const handleCloseQRCode = () => {
    setSelectedTicket(null)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#22c55e'
      case 'used': return '#6b7280'
      case 'cancelled': return '#ef4444'
      default: return '#6b7280'
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '2rem 0' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem', color: '#1f2937' }}>
          My Tickets
        </h1>
        
        {selectedTicket ? (
          <div>
            <button
              onClick={handleCloseQRCode}
              style={{
                backgroundColor: '#6b7280',
                color: 'white',
                padding: '0.5rem 1rem',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                marginBottom: '1rem'
              }}
            >
              ← Back to Tickets
            </button>
            
            <QRCodeDisplay
              ticketNumber={selectedTicket.ticket_number}
              eventName={selectedTicket.event_name}
              holderName={selectedTicket.holder_name}
              holderEmail={selectedTicket.holder_email}
            />
          </div>
        ) : (
          <div>
            {tickets.length === 0 ? (
              <div style={{
                backgroundColor: 'white',
                padding: '3rem',
                borderRadius: '12px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                textAlign: 'center'
              }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  backgroundColor: '#f3f4f6',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1rem'
                }}>
                  <span style={{ fontSize: '2rem' }}>🎫</span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem', color: '#1f2937' }}>
                  No Tickets Yet
                </h3>
                <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
                  You haven't purchased any tickets yet. Browse events to get started!
                </p>
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
                  Browse Events
                </button>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: '1.5rem' }}>
                {tickets.map((ticket) => (
                  <div
                    key={ticket.id}
                    style={{
                      backgroundColor: 'white',
                      padding: '1.5rem',
                      borderRadius: '12px',
                      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem', color: '#1f2937' }}>
                        {ticket.event_name}
                      </h3>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.875rem', color: '#6b7280' }}>
                        <p><strong>Date:</strong> {ticket.event_date}</p>
                        <p><strong>Time:</strong> {ticket.event_time}</p>
                        <p><strong>Venue:</strong> {ticket.venue}</p>
                        <p><strong>Ticket #:</strong> {ticket.ticket_number}</p>
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                      <span
                        style={{
                          backgroundColor: getStatusColor(ticket.status),
                          color: 'white',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '9999px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textTransform: 'uppercase'
                        }}
                      >
                        {ticket.status}
                      </span>
                      
                      <button
                        onClick={() => handleViewQRCode(ticket)}
                        style={{
                          backgroundColor: '#3b82f6',
                          color: 'white',
                          padding: '0.5rem 1rem',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}
                      >
                        View QR Code
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
