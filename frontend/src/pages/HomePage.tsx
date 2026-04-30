import { Link } from 'react-router-dom'
import { Search, Calendar, MapPin, Users, Star, ArrowRight } from 'lucide-react'

export function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Discover Amazing Events
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              Find and book tickets for concerts, conferences, festivals, and more
            </p>
            <div className="max-w-2xl mx-auto">
              <div className="bg-white rounded-lg shadow-lg p-2 flex">
                <input
                  type="text"
                  placeholder="Search for events, artists, or venues..."
                  className="flex-1 px-4 py-3 text-gray-900 focus:outline-none"
                />
                <button className="bg-primary-600 text-white px-6 py-3 rounded-md hover:bg-primary-700 transition-colors flex items-center space-x-2">
                  <Search className="w-5 h-5" />
                  <span>Search</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose Event Booking?
            </h2>
            <p className="text-lg text-gray-600">
              The easiest way to discover and book events in your area
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Easy Discovery</h3>
              <p className="text-gray-600">
                Find events that match your interests with our smart search and filters
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Simple Booking</h3>
              <p className="text-gray-600">
                Book tickets in just a few clicks with secure payment processing
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Mobile Tickets</h3>
              <p className="text-gray-600">
                Get QR code tickets delivered instantly to your phone
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Events */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Popular Events</h2>
            <Link
              to="/events"
              className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
            >
              <span>View All Events</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* Sample Event Cards */}
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="h-48 bg-gray-200"></div>
                <div className="p-6">
                  <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
                    <Calendar className="w-4 h-4" />
                    <span>Dec {15 + i}, 2024</span>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Sample Event {i}</h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
                    <MapPin className="w-4 h-4" />
                    <span>New York, NY</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-primary-600">${25 * i}</span>
                    <button className="btn btn-primary btn-sm">
                      Book Now
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Find Your Next Experience?
          </h2>
          <p className="text-xl mb-8 text-primary-100">
            Join thousands of users discovering amazing events every day
          </p>
          <div className="space-x-4">
            <Link
              to="/events"
              className="btn bg-white text-primary-600 hover:bg-gray-100"
            >
              Browse Events
            </Link>
            <Link
              to="/register"
              className="btn border-2 border-white text-white hover:bg-white hover:text-primary-600"
            >
              Sign Up Free
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
