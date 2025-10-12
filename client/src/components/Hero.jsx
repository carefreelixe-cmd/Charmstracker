import React from 'react';

const Hero = () => {
  return (
    <section className="bg-gradient-to-r from-gray-50 to-gray-100 py-12 md:py-20">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-8 md:mb-0">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Track James Avery Charm Values <span className="text-amber-500">In Real-Time</span>
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              The first marketplace aggregator that tracks price history, availability, and popularity trends of James Avery charms.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 rounded-lg shadow-md transition-colors flex items-center justify-center">
                <i className="fas fa-search mr-2"></i>
                Browse Charm Database
              </button>
              <button className="bg-white hover:bg-gray-100 text-gray-800 px-6 py-3 rounded-lg shadow-md border border-gray-200 transition-colors flex items-center justify-center">
                <i className="fas fa-info-circle mr-2"></i>
                Learn How It Works
              </button>
            </div>
          </div>
          <div className="md:w-1/2">
            <div className="bg-white rounded-lg shadow-xl overflow-hidden">
              <div className="p-1 bg-gradient-to-r from-gray-300 via-amber-300 to-gray-300">
                <div className="bg-white p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-gray-800">Trending Charms</h3>
                    <span className="text-sm text-gray-500">Updated Today</span>
                  </div>
                  {[1, 2, 3].map((item) => (
                    <div key={item} className="flex items-center justify-between p-3 mb-2 border-b border-gray-100 hover:bg-gray-50 rounded transition-colors">
                      <div className="flex items-center">
                        <div className="w-12 h-12 bg-gray-200 rounded-md mr-3"></div>
                        <div>
                          <h4 className="font-medium text-gray-800">Sterling Heart Charm</h4>
                          <p className="text-sm text-gray-500">Silver • Active</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-amber-500">$32.50</p>
                        <p className="text-sm text-green-600 flex items-center">
                          <i className="fas fa-arrow-up mr-1 text-xs"></i>
                          5.2%
                        </p>
                      </div>
                    </div>
                  ))}
                  <button className="w-full mt-3 text-center text-amber-600 hover:text-amber-700 py-2">
                    View all trending charms <i className="fas fa-chevron-right ml-1 text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;