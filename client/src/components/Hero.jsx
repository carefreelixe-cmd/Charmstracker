import React from 'react';

const Hero = () => {
  // Improved base64 SVG images for charms with better colors
  const charmImages = [
    // Sterling Heart Charm - Silver with better contrast
    "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmYWZhZmEiLz48cGF0aCBkPSJNNTAgODFDMzcgNjkgMjMgNTcgMTUgNDQuNWMtOC0xMy00LTI3IDMuNS0zMy41IDcuNS02LjUgMTgtNi43IDI3LS41IDMgMiA2IDUuMyA3LjQgOC41aC0ycyA2LTEzIDE3LTEzYzEwLjgtLjIgMTYuMiA3IDE4IDE2IDIgOSAxIDE1LTQuNSAyNUM3MCA2Ni41IDU4LjggNzMuNSA1MCA4MVoiIGZpbGw9IiNjMGMwYzAiIHN0cm9rZT0iI2EwYTBhMCIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9zdmc+",
    
    // Texas Charm - Blue silver
    "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmNGY4ZmMiLz48cGF0aCBkPSJNMzIgMzBMNDAgMThoMTVsMiA1IDQtMWgxNWw4IDMtNCAxMCA3IDJMNzMgODRsLTExLTEtMiAxaC03bC00LTFoLTdsMi0zLTMtMi03LTN2LThoNmw1LTEgMi0xMC0zLTMtNy0xLTMtMTEtMi0xMHoiIGZpbGw9IiNiMGM0ZDAiIHN0cm9rZT0iIzkwYTRiMCIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9zdmc+",
    
    // Cross Charm - Silver with a hint of blue
    "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmYWZhZmEiLz48cGF0aCBkPSJNNDAgMjJoMjB2MThIMTh2MjBoMTJ2MjBoMTB2LTIwaDIwVjQwSDQwWiIgZmlsbD0iI2MwYzVjZCIgc3Ryb2tlPSIjYTBhNWFkIiBzdHJva2Utd2lkdGg9IjEiLz48L3N2Zz4="
  ];
  
  // Trending charms data
  const trendingCharms = [
    {
      id: 1,
      name: "Sterling Heart Charm",
      image: charmImages[0],
      material: "Silver",
      status: "Active",
      price: "$32.50",
      change: "+5.2%",
      isPositive: true
    },
    {
      id: 2,
      name: "Texas Charm",
      image: charmImages[1],
      material: "Silver",
      status: "Active",
      price: "$42.75",
      change: "-1.3%",
      isPositive: false
    },
    {
      id: 3,
      name: "Cross Charm",
      image: charmImages[2],
      material: "Silver",
      status: "Active",
      price: "$38.00",
      change: "+2.8%",
      isPositive: true
    }
  ];

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
                  
                  {trendingCharms.map((charm) => (
                    <div key={charm.id} className="flex items-center justify-between p-3 mb-2 border-b border-gray-100 hover:bg-gray-50 rounded transition-colors cursor-pointer">
                      <div className="flex items-center">
                        <div className="w-12 h-12 rounded-md mr-3 overflow-hidden bg-gradient-to-b from-gray-100 to-gray-200 shadow-inner">
                          <img 
                            src={charm.image}
                            alt={charm.name}
                            className="w-full h-full object-contain"
                          />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-800">{charm.name}</h4>
                          <p className="text-sm text-gray-500">{charm.material} • {charm.status}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-amber-500">{charm.price}</p>
                        <p className={`text-sm ${charm.isPositive ? 'text-green-600' : 'text-red-600'} flex items-center`}>
                          <i className={`fas ${charm.isPositive ? 'fa-arrow-up' : 'fa-arrow-down'} mr-1 text-xs`}></i>
                          {charm.change}
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