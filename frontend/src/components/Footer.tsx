export function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">Event Booking</h3>
            <p className="text-gray-400">
              Discover and book tickets for amazing events in your area.
            </p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Events</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white">Concerts</a></li>
              <li><a href="#" className="hover:text-white">Conferences</a></li>
              <li><a href="#" className="hover:text-white">Festivals</a></li>
              <li><a href="#" className="hover:text-white">Sports</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white">Help Center</a></li>
              <li><a href="#" className="hover:text-white">Contact Us</a></li>
              <li><a href="#" className="hover:text-white">FAQs</a></li>
              <li><a href="#" className="hover:text-white">Terms of Service</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Connect</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white">Facebook</a></li>
              <li><a href="#" className="hover:text-white">Twitter</a></li>
              <li><a href="#" className="hover:text-white">Instagram</a></li>
              <li><a href="#" className="hover:text-white">LinkedIn</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2024 Event Booking System. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
