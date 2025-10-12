import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-12">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col md:flex-row justify-between mb-8">
          <div className="mb-8 md:mb-0">
            <h2 className="text-2xl font-bold mb-4">
              <span className="text-gray-400">Charm</span>
              <span className="text-amber-500">Tracker</span>
              <span className="text-sm text-gray-400 ml-1">.com</span>
            </h2>
            <p className="text-gray-400 max-w-md mb-4">
              The first marketplace aggregator that tracks James Avery charm values in real-time.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">
                <i className="fab fa-facebook-f"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">
                <i className="fab fa-twitter"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">
                <i className="fab fa-instagram"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">
                <i className="fab fa-pinterest-p"></i>
              </a>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Features</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Charm Database</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Price History</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Marketplace Listings</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Watchlist</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Resources</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Blog</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Market Reports</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">FAQ</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Help Center</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Company</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">About Us</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Terms of Service</a></li>
                <li><a href="#" className="text-gray-400 hover:text-amber-500 transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-700 pt-8 mt-8 text-center md:text-left md:flex md:justify-between md:items-center">
          <p className="text-gray-500 text-sm mb-4 md:mb-0">
            &copy; {new Date().getFullYear()} CharmTracker.com. All rights reserved.
          </p>
          <p className="text-gray-500 text-sm">
            CharmTracker is not affiliated with James Avery Artisan Jewelry.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;