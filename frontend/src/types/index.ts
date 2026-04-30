// User types
export interface User {
  id: string
  email: string
  username: string
  full_name: string
  phone?: string
  bio?: string
  avatar_url?: string
  role: 'user' | 'admin' | 'organizer'
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at?: string
  last_login?: string
}

// Event types
export interface Event {
  id: string
  organizer_id: string
  title: string
  description?: string
  short_description?: string
  event_type: string
  status: 'draft' | 'published' | 'cancelled' | 'completed'
  venue_name?: string
  venue_address?: string
  city?: string
  country?: string
  is_virtual: boolean
  virtual_url?: string
  start_time: string
  end_time: string
  doors_open?: string
  max_capacity?: number
  current_capacity: number
  currency: string
  min_price?: number
  max_price?: number
  cover_image_url?: string
  banner_image_url?: string
  tags?: string[]
  age_restriction?: string
  accessibility_info?: string
  terms_and_conditions?: string
  slug: string
  meta_title?: string
  meta_description?: string
  allow_waitlist: boolean
  require_approval: boolean
  is_featured: boolean
  view_count: number
  booking_count: number
  created_at: string
  updated_at?: string
  published_at?: string
}

// Ticket types
export interface TicketTier {
  id: string
  event_id: string
  name: string
  description?: string
  ticket_type: string
  price: number
  currency: string
  total_quantity: number
  available_quantity: number
  sold_quantity: number
  min_per_order: number
  max_per_order: number
  sale_start_time?: string
  sale_end_time?: string
  status: 'available' | 'sold_out' | 'unavailable' | 'hidden'
  is_hidden: boolean
  features?: string[]
  restrictions?: string
  created_at: string
  updated_at?: string
}

export interface Ticket {
  id: string
  ticket_tier_id: string
  booking_id: string
  ticket_number: string
  qr_code_url?: string
  holder_name: string
  holder_email: string
  holder_phone?: string
  is_valid: boolean
  is_used: boolean
  checked_in_at?: string
  checked_in_by?: string
  created_at: string
  updated_at?: string
  expires_at?: string
  custom_fields?: Record<string, any>
}

// Booking types
export interface Booking {
  id: string
  user_id: string
  event_id: string
  booking_number: string
  status: 'pending' | 'confirmed' | 'cancelled' | 'refunded' | 'expired'
  total_amount: number
  currency: string
  discount_amount: number
  tax_amount: number
  service_fee: number
  customer_name: string
  customer_email: string
  customer_phone?: string
  payment_status: string
  payment_method?: string
  payment_id?: string
  booking_time: string
  confirmation_time?: string
  cancellation_time?: string
  expiry_time?: string
  notes?: string
  special_requests?: string
  metadata?: Record<string, any>
}

export interface BookingItem {
  id: string
  booking_id: string
  ticket_tier_id: string
  quantity: number
  unit_price: number
  total_price: number
  created_at: string
}

// Payment types
export interface Payment {
  id: string
  booking_id: string
  user_id: string
  payment_id: string
  payment_method: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'refunded' | 'partially_refunded'
  amount: number
  currency: string
  fee_amount: number
  net_amount?: number
  stripe_intent_id?: string
  stripe_charge_id?: string
  stripe_customer_id?: string
  created_at: string
  processed_at?: string
  failed_at?: string
  failure_reason?: string
  metadata?: Record<string, any>
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Form types
export interface LoginFormData {
  email: string
  password: string
}

export interface RegisterFormData {
  email: string
  username: string
  full_name: string
  password: string
  phone?: string
}

export interface CreateEventData {
  title: string
  description?: string
  short_description?: string
  event_type: string
  venue_name?: string
  venue_address?: string
  city?: string
  country?: string
  is_virtual: boolean
  virtual_url?: string
  start_time: string
  end_time: string
  doors_open?: string
  max_capacity?: number
  currency: string
  min_price?: number
  max_price?: number
  cover_image_url?: string
  tags?: string[]
  age_restriction?: string
  accessibility_info?: string
  terms_and_conditions?: string
  allow_waitlist: boolean
  require_approval: boolean
}

export interface BookingFormData {
  event_id: string
  items: {
    ticket_tier_id: string
    quantity: number
  }[]
  customer_name: string
  customer_email: string
  customer_phone?: string
  notes?: string
  special_requests?: string
}

// UI State types
export interface CartItem {
  ticket_tier: TicketTier
  quantity: number
}

export interface CartState {
  items: CartItem[]
  total: number
  currency: string
}

// Filter types
export interface EventFilters {
  query?: string
  event_type?: string
  city?: string
  country?: string
  start_date?: string
  end_date?: string
  min_price?: number
  max_price?: number
  tags?: string[]
  is_virtual?: boolean
  is_featured?: boolean
  page?: number
  size?: number
  sort_by?: string
  sort_order?: string
}
