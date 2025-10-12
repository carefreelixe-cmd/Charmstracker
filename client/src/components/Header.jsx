import React, { useState } from 'react';

const Header = () => {
  // State to manage mobile menu toggle
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="bg-white shadow-md py-4">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-xl md:text-2xl font-bold text-gray-800">
              <span className="text-gray-400">Charm</span>
              <span className="text-amber-500">Tracker</span>
              <span className="text-sm text-gray-400 ml-1">.com</span>
            </h1>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex">
            <ul className="flex space-x-6">
              <li><a href="#how-it-works" className="text-gray-600 hover:text-amber-500 transition-colors">How It Works</a></li>
              <li><a href="#discover" className="text-gray-600 hover:text-amber-500 transition-colors">Discover</a></li>
              <li><a href="#why-us" className="text-gray-600 hover:text-amber-500 transition-colors">Why Choose Us</a></li>
            </ul>
          </nav>
          
          {/* Desktop Search & Button */}
          <div className="hidden md:flex items-center">
            <div className="relative mr-2">
              <input 
                type="text" 
                placeholder="Search for charms..." 
                className="pl-8 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 w-64"
              />
              <i className="fas fa-search absolute left-3 top-3 text-gray-400"></i>
            </div>
            <button className="bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-full shadow-md transition-colors">
              <i className="fas fa-chart-line mr-2"></i>Track
            </button>
          </div>
          
          {/* Mobile Search & Menu Toggle */}
          <div className="flex items-center md:hidden">
            <button 
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 text-gray-600 focus:outline-none"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                <i className="fas fa-times text-xl"></i>
              ) : (
                <i className="fas fa-bars text-xl"></i>
              )}
            </button>
          </div>
        </div>
        
        {/* Mobile Search (visible when menu is open) */}
        {isMobileMenuOpen && (
          <div className="mt-4 md:hidden">
            <div className="relative mb-4">
              <input 
                type="text" 
                placeholder="Search for charms..." 
                className="pl-8 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 w-full"
              />
              <i className="fas fa-search absolute left-3 top-3 text-gray-400"></i>
            </div>
            <nav>
              <ul className="flex flex-col space-y-3">
                <li><a href="#how-it-works" className="block py-2 px-4 bg-gray-50 rounded-md text-gray-600 hover:text-amber-500 transition-colors" onClick={() => setIsMobileMenuOpen(false)}>How It Works</a></li>
                <li><a href="#discover" className="block py-2 px-4 bg-gray-50 rounded-md text-gray-600 hover:text-amber-500 transition-colors" onClick={() => setIsMobileMenuOpen(false)}>Discover</a></li>
                <li><a href="#why-us" className="block py-2 px-4 bg-gray-50 rounded-md text-gray-600 hover:text-amber-500 transition-colors" onClick={() => setIsMobileMenuOpen(false)}>Why Choose Us</a></li>
              </ul>
            </nav>
            <div className="mt-4">
              <button className="bg-amber-500 hover:bg-amber-600 text-white w-full px-4 py-2 rounded-full shadow-md transition-colors">
                <i className="fas fa-chart-line mr-2"></i>Track
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;