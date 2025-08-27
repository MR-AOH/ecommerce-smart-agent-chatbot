// Import Font Awesome icons for UI elements (search, cart, user, heart)
import { FaSearch, FaShoppingCart, FaUser, FaHeart, FaStar, FaFire, FaShippingFast, FaShieldAlt } from 'react-icons/fa'
import { useState } from 'react'
// Import the custom ChatWidget component for AI assistance
import ChatWidget from './ChatWidget'
const EcommerceStore = () => {
  const [searchQuery, setSearchQuery] = useState('')
  
  const featuredProducts = [
    { id: 1, name: "Wireless Headphones", price: "$99", originalPrice: "$149", image: "🎧", rating: 4.8, discount: "33% OFF" },
    { id: 2, name: "Smart Watch", price: "$299", originalPrice: "$399", image: "⌚", rating: 4.9, discount: "25% OFF" },
    { id: 3, name: "Gaming Laptop", price: "$1,299", originalPrice: "$1,699", image: "💻", rating: 4.7, discount: "24% OFF" },
    { id: 4, name: "Wireless Earbuds", price: "$79", originalPrice: "$129", image: "🎵", rating: 4.6, discount: "39% OFF" }
  ]

  const categories = [
    { name: "Electronics", icon: "📱", color: "from-blue-500 to-cyan-500" },
    { name: "Fashion", icon: "👔", color: "from-pink-500 to-rose-500" },
    { name: "Home", icon: "🏠", color: "from-green-500 to-emerald-500" },
    { name: "Beauty", icon: "💄", color: "from-purple-500 to-indigo-500" },
    { name: "Sports", icon: "⚽", color: "from-orange-500 to-red-500" },
    { name: "Books", icon: "📚", color: "from-yellow-500 to-amber-500" }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-gray-100 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Top Bar */}
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 bg-clip-text text-transparent">
                ShopSmart✨
              </h1>
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-2xl mx-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search for amazing products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-6 py-3 pl-12 bg-gray-50 border-2 border-transparent rounded-full focus:border-purple-500 focus:bg-white focus:outline-none transition-all duration-300"
                />
                <FaSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <button className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1.5 rounded-full hover:shadow-lg transition-all">
                  Search
                </button>
              </div>
            </div>

            {/* Nav Icons */}
            <div className="flex items-center space-x-6">
              <button className="relative p-2 text-gray-600 hover:text-purple-600 transition-colors">
                <FaUser className="w-5 h-5" />
              </button>
              <button className="relative p-2 text-gray-600 hover:text-purple-600 transition-colors">
                <FaHeart className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">3</span>
              </button>
              <button className="relative p-2 text-gray-600 hover:text-purple-600 transition-colors">
                <FaShoppingCart className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 bg-purple-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">2</span>
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center justify-center space-x-8 py-4">
            {['Home', 'Electronics', 'Fashion', 'Home & Garden', 'Beauty', 'Sports', 'Deals'].map((item, index) => (
              <a
                key={item}
                href="#"
                className={`px-3 py-2 text-sm font-medium rounded-full transition-all duration-300 ${
                  index === 0
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                    : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50'
                }`}
              >
                {item}
              </a>
            ))}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-purple-900 via-purple-800 to-pink-800 text-white">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full mb-6">
              <FaFire className="text-orange-400 mr-2" />
              <span className="text-sm font-medium">Limited Time Offer</span>
            </div>
            <h2 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white to-pink-200 bg-clip-text text-transparent">
              Summer Sale
            </h2>
            <p className="text-xl md:text-2xl mb-8 text-purple-100 max-w-2xl mx-auto">
              Get up to <span className="text-3xl font-bold text-yellow-300">70% OFF</span> on selected items. Don't miss out!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-4 bg-white text-purple-900 font-bold rounded-full hover:bg-gray-100 transform hover:scale-105 transition-all duration-300 shadow-2xl">
                Shop Now 🛍️
              </button>
              <button className="px-8 py-4 border-2 border-white text-white font-bold rounded-full hover:bg-white hover:text-purple-900 transition-all duration-300">
                View Deals
              </button>
            </div>
          </div>
        </div>
        {/* Decorative elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-pink-500/20 rounded-full blur-xl"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-purple-500/20 rounded-full blur-xl"></div>
      </section>

      {/* Categories */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-center mb-12 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
            Shop by Category
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {categories.map((category, index) => (
              <div
                key={index}
                className="group cursor-pointer"
              >
                <div className={`bg-gradient-to-br ${category.color} p-6 rounded-2xl text-center transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl`}>
                  <div className="text-4xl mb-3">{category.icon}</div>
                  <h4 className="text-white font-semibold">{category.name}</h4>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              🔥 Hot Deals
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Don't miss these incredible deals! Limited time offers on our most popular products.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {featuredProducts.map((product) => (
              <div
                key={product.id}
                className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100 overflow-hidden group"
              >
                <div className="relative p-6 bg-gradient-to-br from-gray-50 to-gray-100">
                  <div className="absolute top-4 left-4 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                    {product.discount}
                  </div>
                  <div className="text-6xl text-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    {product.image}
                  </div>
                </div>
                
                <div className="p-6">
                  <h4 className="font-bold text-lg mb-2 text-gray-900">{product.name}</h4>
                  <div className="flex items-center mb-3">
                    <div className="flex text-yellow-400 text-sm mr-2">
                      {[...Array(5)].map((_, i) => (
                        <FaStar key={i} className={i < Math.floor(product.rating) ? 'text-yellow-400' : 'text-gray-300'} />
                      ))}
                    </div>
                    <span className="text-sm text-gray-600">({product.rating})</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-2xl font-bold text-purple-600">{product.price}</span>
                      <span className="text-sm text-gray-500 line-through ml-2">{product.originalPrice}</span>
                    </div>
                    <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-full hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <FaShippingFast className="text-white text-xl" />
              </div>
              <h4 className="text-xl font-bold mb-2">Free Shipping</h4>
              <p className="text-gray-600">Free shipping on all orders over $50</p>
            </div>
            <div className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <FaShieldAlt className="text-white text-xl" />
              </div>
              <h4 className="text-xl font-bold mb-2">Secure Payment</h4>
              <p className="text-gray-600">Your payment information is safe with us</p>
            </div>
            <div className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                <FaHeart className="text-white text-xl" />
              </div>
              <h4 className="text-xl font-bold mb-2">24/7 Support</h4>
              <p className="text-gray-600">We're here to help you anytime</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
                ShopSmart✨
              </h3>
              <p className="text-gray-400 mb-4">Your one-stop shop for amazing products at unbeatable prices.</p>
              <div className="flex space-x-4">
                {['Facebook', 'Instagram', 'Twitter'].map((social) => (
                  <a key={social} href="#" className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center hover:shadow-lg transition-all duration-300 transform hover:scale-110">
                    <span className="text-sm">📱</span>
                  </a>
                ))}
              </div>
            </div>
            
            {[
              { title: 'Shop', items: ['Electronics', 'Fashion', 'Home & Garden', 'Beauty', 'Sports'] },
              { title: 'Customer Service', items: ['Contact Us', 'FAQs', 'Shipping Info', 'Returns', 'Track Order'] },
              { title: 'Company', items: ['About Us', 'Blog', 'Careers', 'Press', 'Sustainability'] }
            ].map((section, index) => (
              <div key={index}>
                <h4 className="text-lg font-semibold mb-4">{section.title}</h4>
                <ul className="space-y-2">
                  {section.items.map((item, idx) => (
                    <li key={idx}>
                      <a href="#" className="text-gray-400 hover:text-white transition-colors duration-300">{item}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} ShopSmart. All rights reserved. Made with ❤️</p>
          </div>
        </div>
      </footer>

      {/* Chat Widget */}
      <ChatWidget />
    </div>
  )
}

export default EcommerceStore