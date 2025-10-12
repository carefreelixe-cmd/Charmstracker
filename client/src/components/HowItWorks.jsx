import React from 'react';

const HowItWorks = () => {
  // Hardcoded base64 SVG images for charms
  const crossImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNlMmY5ZDIiLz48cGF0aCBkPSJNNDAgMjJoMjB2MThIMTh2MjBoMTJ2MjBoMTB2LTIwaDIwVjQwSDQwWiIgZmlsbD0iIzZlYTY2MCIvPjwvc3ZnPg==";
  const heartImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmOWQ5YjMiLz48cGF0aCBkPSJNNTAgODFDMzcgNjkgMjMgNTcgMTUgNDQuNWMtOC0xMy00LTI3IDMuNS0zMy41IDcuNS02LjUgMTgtNi43IDI3LS41IDMgMiA2IDUuMyA3LjQgOC41aC0ycyA2LTEzIDE3LTEzYzEwLjgtLjIgMTYuMiA3IDE4IDE2IDIgOSAxIDE1LTQuNSAyNUM3MCA2Ni41IDU4LjggNzMuNSA1MCA4MVoiIGZpbGw9IiNlNmIwNzgiLz48L3N2Zz4=";
  const texasImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNkMmUyZjkiLz48cGF0aCBkPSJNMzIgMzBMNDAgMThoMTVsMiA1IDQtMWgxNWw4IDMtNCAxMCA3IDJMNzMgODRsLTExLTEtMiAxaC03bC00LTFoLTdsMi0zLTMtMi03LTN2LThoNmw1LTEgMi0xMC0zLTMtNy0xLTMtMTEtMi0xMHoiIGZpbGw9IiM5NmEzYzQiLz48L3N2Zz4=";
  
  return (
    <section className="py-16 bg-gray-50" id="discover">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">How It Works</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Real market data updated daily from trusted sources
          </p>
        </div>
        
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="bg-white rounded-lg shadow-md p-6 flex-1">
            <h3 className="text-2xl font-semibold text-gray-800 mb-4">Real Market Data — Updated Daily</h3>
            <p className="text-gray-600 mb-6">
              Charms Tracker pulls pricing and listing data from trusted marketplaces like eBay, Poshmark, and Etsy every few hours. Each charm's page shows an average price based on sold listings, not just what sellers are asking. Our charts reveal real-world value trends so you can spot deals, track appreciation, or confirm fair prices before buying or selling.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start">
                <div className="text-amber-500 mr-3">
                  <i className="fas fa-chart-line text-xl"></i>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Accurate Price History</h4>
                  <p className="text-sm text-gray-600">See historical highs, lows, and averages.</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="text-amber-500 mr-3">
                  <i className="fas fa-search text-xl"></i>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Live Listings</h4>
                  <p className="text-sm text-gray-600">Browse active sales across multiple platforms.</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="text-amber-500 mr-3">
                  <i className="fas fa-clock text-xl"></i>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Retired Status</h4>
                  <p className="text-sm text-gray-600">Instantly know if a charm is still sold by James Avery.</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="text-amber-500 mr-3">
                  <i className="fas fa-comments text-xl"></i>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Popularity Tracking</h4>
                  <p className="text-sm text-gray-600">Discover what collectors are buying right now.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 flex-1">
            <div className="mb-6">
              <h3 className="text-2xl font-semibold text-gray-800 mb-4">Find Out What's Trending Among Collectors</h3>
              <p className="text-gray-600">
                Stay ahead of the market with trend insights that show which charms are climbing in value and which are cooling off. The Trending Dashboard highlights price movers, recently sold pieces, and collector favorites so you can act before the crowd.
              </p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-3">Live Market Preview</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-white rounded shadow-sm">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-md mr-3 overflow-hidden">
                      <img 
                        src={crossImage} 
                        alt="Silver Cross Charm" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <span className="font-medium text-gray-800">Silver Cross Charm</span>
                  </div>
                  <div className="flex items-center text-green-600">
                    <i className="fas fa-arrow-up mr-1"></i>
                    <span>12.5%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded shadow-sm">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-md mr-3 overflow-hidden">
                      <img 
                        src={heartImage} 
                        alt="Gold Heart Pendant" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <span className="font-medium text-gray-800">Gold Heart Pendant</span>
                  </div>
                  <div className="flex items-center text-green-600">
                    <i className="fas fa-arrow-up mr-1"></i>
                    <span>8.3%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded shadow-sm">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-md mr-3 overflow-hidden">
                      <img 
                        src={texasImage} 
                        alt="Texas Charm" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <span className="font-medium text-gray-800">Texas Charm</span>
                  </div>
                  <div className="flex items-center text-red-600">
                    <i className="fas fa-arrow-down mr-1"></i>
                    <span>2.1%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;