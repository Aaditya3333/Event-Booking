import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'

// Pages
import { HomePage } from './pages/HomePage'
import { EventsPage } from './pages/EventsPage'
import { EventDetailPage } from './pages/EventDetailPage'
import SimpleLoginPage from './pages/SimpleLoginPage'
import SimpleRegisterPage from './pages/SimpleRegisterPage'
import TestAuth from './pages/TestAuth'
import { ProfilePage } from './pages/ProfilePage'
import { MyBookingsPage } from './pages/MyBookingsPage'
import { MyTicketsPage } from './pages/MyTicketsPage'
import { CreateEventPage } from './pages/CreateEventPage'
import { MyEventsPage } from './pages/MyEventsPage'
import { EditEventPage } from './pages/EditEventPage'
import { CheckoutPage } from './pages/CheckoutPage'
import { BookingSuccessPage } from './pages/BookingSuccessPage'
import { CheckInPage } from './pages/CheckInPage'
import { NotFoundPage } from './pages/NotFoundPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="events" element={<EventsPage />} />
        <Route path="events/:id" element={<EventDetailPage />} />
        <Route path="checkout/:bookingId" element={<CheckoutPage />} />
        <Route path="booking-success/:bookingId" element={<BookingSuccessPage />} />
        <Route path="check-in" element={<CheckInPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="my-bookings" element={<MyBookingsPage />} />
        <Route path="my-tickets" element={<MyTicketsPage />} />
        <Route path="create-event" element={<CreateEventPage />} />
        <Route path="my-events" element={<MyEventsPage />} />
        <Route path="edit-event/:id" element={<EditEventPage />} />
      </Route>
      
      {/* Simple authentication routes */}
      <Route path="/simple-login" element={<SimpleLoginPage />} />
      <Route path="/simple-register" element={<SimpleRegisterPage />} />
      <Route path="/test-auth" element={<TestAuth />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
