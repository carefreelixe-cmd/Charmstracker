import React from 'react';

const Header = () => {
  return (
    <header className="bg-white shadow-md py-4">
      <div className="container mx-auto px-4 md:px-6 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-gray-800">
            <span className="text-gray-400">Charm</span>
            <span className="text-amber-500">Tracker</span>
            <span className="text-sm text-gray-400 ml-1">.com</span>
          </h1>
        </div>
        
        <nav className="hidden md:flex">
          <ul className="flex space-x-6">
            <li><a href="#how-it-works" className="text-gray-600 hover:text-amber-500 transition-colors">How It Works</a></li>
            <li><a href="#discover" className="text-gray-600 hover:text-amber-500 transition-colors">Discover</a></li>
            <li><a href="#why-us" className="text-gray-600 hover:text-amber-500 transition-colors">Why Choose Us</a></li>
          </ul>
        </nav>
        
        <div className="flex items-center">
          <div className="relative mr-2">
            <input 
              type="text" 
              placeholder="Search for charms..." 
              className="pl-8 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 w-full md:w-64"
            />
            <i className="fas fa-search absolute left-3 top-3 text-gray-400"></i>
          </div>
          <button className="bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-full shadow-md transition-colors hidden md:block">
            <i className="fas fa-chart-line mr-2"></i>Track
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;