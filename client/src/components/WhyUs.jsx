import React from 'react';

const WhyUs = () => {
  return (
    <section className="py-16 bg-white" id="why-us">
      <div className="container mx-auto px-4 md:px-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Why Collectors Use Charms Tracker</h2>
            <p className="text-lg text-gray-600">
              Built for accuracy, speed, and simplicity
            </p>
          </div>
          
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-8 shadow-lg mb-12">
            <div className="flex flex-col md:flex-row items-center">
              <div className="md:w-1/2 mb-6 md:mb-0 md:pr-8">
                <h3 className="text-2xl font-semibold text-gray-800 mb-4">Built for Collectors</h3>
                <p className="text-gray-600 mb-4">
                  Charms Tracker was designed for collectors — no logins, no ads, no noise. Just clean data, quick search, and clear insight into the real charm market.
                </p>
                <p className="text-gray-600">
                  Whether you're hunting for a rare retired piece or pricing a collection to sell, you'll have the same data edge as professional resellers.
                </p>
              </div>
              <div className="md:w-1/2 grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="text-amber-500 mb-2">
                    <i className="fas fa-bolt text-xl"></i>
                  </div>
                  <h4 className="font-semibold text-gray-800 mb-1">Lightning Fast</h4>
                  <p className="text-sm text-gray-600">Get market data instantly</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="text-amber-500 mb-2">
                    <i className="fas fa-chart-pie text-xl"></i>
                  </div>
                  <h4 className="font-semibold text-gray-800 mb-1">Data-Driven</h4>
                  <p className="text-sm text-gray-600">Real prices, not estimates</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="text-amber-500 mb-2">
                    <i className="fas fa-user-shield text-xl"></i>
                  </div>
                  <h4 className="font-semibold text-gray-800 mb-1">Private</h4>
                  <p className="text-sm text-gray-600">No account needed</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-md">
                  <div className="text-amber-500 mb-2">
                    <i className="fas fa-th-large text-xl"></i>
                  </div>
                  <h4 className="font-semibold text-gray-800 mb-1">Complete</h4>
                  <p className="text-sm text-gray-600">All charms cataloged</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center">
            <button className="bg-amber-500 hover:bg-amber-600 text-white px-8 py-4 rounded-lg shadow-md text-lg font-semibold transition-colors inline-flex items-center">
              <i className="fas fa-search mr-2"></i>
              Start Browsing Now
            </button>
            <p className="text-gray-500 mt-4">
              Search the live market and track your favorite charms instantly.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyUs;