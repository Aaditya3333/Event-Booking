import axios, { AxiosInstance } from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        } else if (error.response?.status >= 500) {
          toast.error('Server error. Please try again later.')
        } else if (error.response?.data?.detail) {
          toast.error(error.response.data.detail)
        } else if (error.message) {
          toast.error(error.message)
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/api/auth/login', { email, password })
    return response.data
  }

  async register(userData: {
    email: string
    username: string
    full_name: string
    password: string
    phone?: string
  }) {
    const response = await this.client.post('/api/auth/register', userData)
    return response.data
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/auth/me')
    return response.data
  }

  async refreshToken() {
    const response = await this.client.post('/api/auth/refresh')
    return response.data
  }

  async logout() {
    const response = await this.client.post('/api/auth/logout')
    return response.data
  }

  // Events endpoints
  async getEvents(params?: {
    page?: number
    size?: number
    search?: string
    event_type?: string
    city?: string
    country?: string
    start_date?: string
    end_date?: string
    min_price?: number
    max_price?: number
    is_virtual?: boolean
    is_featured?: boolean
    sort_by?: string
    sort_order?: string
  }) {
    const response = await this.client.get('/api/events', { params })
    return response.data
  }

  async getEvent(id: string) {
    const response = await this.client.get(`/api/events/${id}`)
    return response.data
  }

  async getEventBySlug(slug: string) {
    const response = await this.client.get(`/api/events/slug/${slug}`)
    return response.data
  }

  async createEvent(eventData: any) {
    const response = await this.client.post('/api/events', eventData)
    return response.data
  }

  async updateEvent(id: string, eventData: any) {
    const response = await this.client.put(`/api/events/${id}`, eventData)
    return response.data
  }

  async publishEvent(id: string, publishData: { publish_now: boolean; scheduled_time?: string }) {
    const response = await this.client.post(`/api/events/${id}/publish`, publishData)
    return response.data
  }

  async cancelEvent(id: string) {
    const response = await this.client.post(`/api/events/${id}/cancel`)
    return response.data
  }

  async deleteEvent(id: string) {
    const response = await this.client.delete(`/api/events/${id}`)
    return response.data
  }

  async getMyEvents(params?: { page?: number; size?: number; status_filter?: string }) {
    const response = await this.client.get('/api/events/my-events', { params })
    return response.data
  }

  // Tickets endpoints
  async getTicketTiers(eventId: string, includeHidden = false) {
    const response = await this.client.get(`/api/tickets/tiers?event_id=${eventId}&include_hidden=${includeHidden}`)
    return response.data
  }

  async createTicketTier(eventId: string, tierData: any) {
    const response = await this.client.post(`/api/tickets/tiers?event_id=${eventId}`, tierData)
    return response.data
  }

  async updateTicketTier(tierId: string, tierData: any) {
    const response = await this.client.put(`/api/tickets/tiers/${tierId}`, tierData)
    return response.data
  }

  async deleteTicketTier(tierId: string) {
    const response = await this.client.delete(`/api/tickets/tiers/${tierId}`)
    return response.data
  }

  async getTicketAvailability(eventId: string) {
    const response = await this.client.get(`/api/tickets/availability/${eventId}`)
    return response.data
  }

  async getMyTickets() {
    const response = await this.client.get('/api/tickets/my-tickets')
    return response.data
  }

  async validateTicket(ticketNumber: string) {
    const response = await this.client.post(`/api/tickets/validate/${ticketNumber}`)
    return response.data
  }

  async checkInTicket(checkInData: { ticket_number: string; check_in_location?: string; device_id?: string; notes?: string }) {
    const response = await this.client.post('/api/tickets/checkin', checkInData)
    return response.data
  }

  // Bookings endpoints
  async createBooking(bookingData: any) {
    const response = await this.client.post('/api/bookings', bookingData)
    return response.data
  }

  async getMyBookings(params?: { page?: number; size?: number; status_filter?: string }) {
    const response = await this.client.get('/api/bookings/my-bookings', { params })
    return response.data
  }

  async getBooking(id: string) {
    const response = await this.client.get(`/api/bookings/${id}`)
    return response.data
  }

  async getBookingSummary(id: string) {
    const response = await this.client.get(`/api/bookings/${id}/summary`)
    return response.data
  }

  async cancelBooking(id: string, cancelData: { reason?: string; refund_requested?: boolean }) {
    const response = await this.client.post(`/api/bookings/${id}/cancel`, cancelData)
    return response.data
  }

  // Payments endpoints
  async createPaymentIntent(paymentData: { booking_id: string; payment_method_id?: string; save_payment_method?: boolean }) {
    const response = await this.client.post('/api/payments/create-payment-intent', paymentData)
    return response.data
  }

  async confirmPayment(paymentIntentId: string) {
    const response = await this.client.post('/api/payments/confirm-payment', { payment_intent_id: paymentIntentId })
    return response.data
  }

  async getMyPayments(params?: { page?: number; size?: number; status_filter?: string }) {
    const response = await this.client.get('/api/payments/my-payments', { params })
    return response.data
  }

  async getPayment(id: string) {
    const response = await this.client.get(`/api/payments/${id}`)
    return response.data
  }

  async createRefund(refundData: { payment_id: string; amount?: number; reason?: string }) {
    const response = await this.client.post('/api/payments/refund', refundData)
    return response.data
  }
}

export const apiClient = new ApiClient()
export default apiClient
