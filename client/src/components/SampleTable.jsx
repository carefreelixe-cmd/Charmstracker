import React, { useState } from 'react';

const SampleTable = () => {
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);
  
  // Hardcoded base64 image data for charm images that will always work
  const heartImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmOWQ2ZDIiLz48cGF0aCBkPSJNNTAgODFDMzcgNjkgMjMgNTcgMTUgNDQuNWMtOC0xMy00LTI3IDMuNS0zMy41IDcuNS02LjUgMTgtNi43IDI3LS41IDMgMiA2IDUuMyA3LjQgOC41aC0ycyA2LTEzIDE3LTEzYzEwLjgtLjIgMTYuMiA3IDE4IDE2IDIgOSAxIDE1LTQuNSAyNUM3MCA2Ni41IDU4LjggNzMuNSA1MCA4MVoiIGZpbGw9IiNlNjVmNmUiLz48L3N2Zz4=";
  const texasImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNkMmUyZjkiLz48cGF0aCBkPSJNMzIgMzBMNDAgMThoMTVsMiA1IDQtMWgxNWw4IDMtNCAxMCA3IDJMNzMgODRsLTExLTEtMiAxaC03bC00LTFoLTdsMi0zLTMtMi03LTN2LThoNmw1LTEgMi0xMC0zLTMtNy0xLTMtMTEtMi0xMHoiIGZpbGw9IiM5NmEzYzQiLz48L3N2Zz4=";
  const crossImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNlMmY5ZDIiLz48cGF0aCBkPSJNNDAgMjJoMjB2MThIMTh2MjBoMTJ2MjBoMTB2LTIwaDIwVjQwSDQwWiIgZmlsbD0iIzZlYTY2MCIvPjwvc3ZnPg==";
  const doveImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmOWYyZDIiLz48cGF0aCBkPSJNNzIgMjhjLTctMS0xNC40IDMuNi0xOSA4LTYuMy0zLjUtMjAuNS0xMi0zMiAyLTctMy0xMiAyLTggOSAyLTEgNC4yLS4yIDYgMiA1LjYgNi44IDYgMjQgMjEgMzItMi42IDEuMi01IDMtOCA1bDMgNCA3LTFjNi45IDQuMiAxNS4yIDQgMjItMS41IDYuNy01LjQgMTEuMy0xNi43IDktMjguNS0uNy0zLjUgNy04LjIgNy0xMS41IDAtNS01LTYuNi04LTQuNS0yLjgtMS45LTUuOC01LTEzLTMuNWwyIDVjLS42LjUtMyAxLTQuNSAwIDE1LTE0LTE1LTkgMi01LjUtNi0yLTctNi41LTUuNS0xMC41IDAtLjQuNy0xIDEtMVoiIGZpbGw9IiNhZDk1NjciLz48L3N2Zz4=";
  const goldImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmOWQ5YjMiLz48dGV4dCB4PSI1MCIgeT0iNjIiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSI0MCIgZmlsbD0iIzk5ODU1YyIgdGV4dC1hbmNob3I9Im1pZGRsZSI+QXU8L3RleHQ+PC9zdmc+";
  const defaultImage = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmM2YzZjMiLz48dGV4dCB4PSI1MCIgeT0iNTgiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIyNCIgZmlsbD0iIzY2NjY2NiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+SkE8L3RleHQ+PC9zdmc+";
  
  // Get appropriate image for each charm
  const getCharmImage = (name) => {
    if (name.toLowerCase().includes('heart') && name.toLowerCase().includes('gold')) return goldImage;
    if (name.toLowerCase().includes('heart')) return heartImage;
    if (name.toLowerCase().includes('texas')) return texasImage;
    if (name.toLowerCase().includes('cross')) return crossImage;
    if (name.toLowerCase().includes('dove')) return doveImage;
    if (name.toLowerCase().includes('gold')) return goldImage;
    return defaultImage;
  };
  
  const charms = [
    {
      id: 1,
      name: 'Heart Charm',
      price: 32.50,
      change: 5.2,
      material: 'Silver',
      status: 'Active',
      popularity: 'High'
    },
    {
      id: 2,
      name: 'Texas Charm',
      price: 42.75,
      change: -1.3,
      material: 'Silver',
      status: 'Active',
      popularity: 'Medium'
    },
    {
      id: 3,
      name: 'Cross Charm',
      price: 38.00,
      change: 2.8,
      material: 'Silver',
      status: 'Active',
      popularity: 'High'
    },
    {
      id: 4,
      name: 'Dove Charm',
      price: 45.25,
      change: 0.5,
      material: 'Silver',
      status: 'Retired',
      popularity: 'Medium'
    },
    {
      id: 5,
      name: 'Gold Heart Charm',
      price: 120.00,
      change: 8.5,
      material: 'Gold',
      status: 'Active',
      popularity: 'High'
    }
  ];

  // Function to render mobile cards for each charm
  const renderMobileCharmCards = () => {
    return charms.map((charm) => (
      <div key={charm.id} className="bg-white p-4 rounded-lg shadow-sm mb-4">
        <div className="flex items-center mb-2">
          <div className="w-16 h-16 rounded-md mr-3 overflow-hidden">
            <img 
              src={getCharmImage(charm.name)} 
              alt={charm.name} 
              className="w-full h-full object-cover"
            />
          </div>
          <div>
            <h4 className="font-medium text-gray-800">{charm.name}</h4>
            <div className="flex items-center">
              <span className={`mr-2 px-2 py-0.5 rounded-full text-xs ${charm.material === 'Gold' ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-800'}`}>
                {charm.material}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-xs ${charm.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {charm.status}
              </span>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-2 mb-3">
          <div>
            <p className="text-xs text-gray-500">Price</p>
            <p className="font-semibold text-amber-500">${charm.price.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">7-Day Change</p>
            <div className={`flex items-center ${charm.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              <i className={`fas ${charm.change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'} mr-1 text-xs`}></i>
              <span className="text-sm">{Math.abs(charm.change)}%</span>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500">Popularity</p>
            <div className="flex items-center">
              <div className="w-12 h-2 bg-gray-200 rounded-full mr-1">
                <div 
                  className={`h-2 rounded-full ${charm.popularity === 'High' ? 'bg-green-500 w-5/6' : charm.popularity === 'Medium' ? 'bg-amber-500 w-1/2' : 'bg-red-500 w-1/4'}`}
                ></div>
              </div>
              <span className="text-xs text-gray-600">{charm.popularity}</span>
            </div>
          </div>
        </div>
        
        <div className="flex justify-center">
          <button className="text-amber-500 hover:text-amber-600 focus:outline-none text-sm">
            <i className="fas fa-star mr-1"></i>
            Add to Watchlist
          </button>
        </div>
      </div>
    ));
  };

  return (
    <section className="py-12 md:py-16 bg-gray-50">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-8 md:mb-12">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-3 md:mb-4">Explore the Charm Database</h2>
          <p className="text-base md:text-lg text-gray-600 max-w-2xl mx-auto">
            Our comprehensive database provides real-time pricing and availability for all James Avery charms.
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header with Filters */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 border-b border-gray-200 bg-gray-50">
            <h3 className="text-lg md:text-xl font-semibold text-gray-800 mb-3 sm:mb-0">Popular Charms</h3>
            
            {/* Mobile filter toggle button */}
            <button 
              className="sm:hidden bg-gray-200 hover:bg-gray-300 text-gray-700 py-1 px-3 rounded text-sm mb-3 w-full flex justify-center items-center"
              onClick={() => setMobileFilterOpen(!mobileFilterOpen)}
            >
              <i className={`fas ${mobileFilterOpen ? 'fa-chevron-up' : 'fa-filter'} mr-2`}></i>
              {mobileFilterOpen ? 'Hide Filters' : 'Show Filters'}
            </button>
            
            {/* Desktop filters always visible, Mobile filters conditionally visible */}
            <div className={`w-full sm:w-auto flex flex-col sm:flex-row items-center gap-3 ${mobileFilterOpen ? 'block' : 'hidden sm:flex'}`}>
              <div className="relative w-full sm:w-auto mb-2 sm:mb-0">
                <input 
                  type="text" 
                  placeholder="Filter charms..." 
                  className="pl-8 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 w-full sm:w-48"
                />
                <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"></i>
              </div>
              <select className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-gray-800 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 w-full sm:w-auto">
                <option>All Materials</option>
                <option>Silver</option>
                <option>Gold</option>
                <option>Other</option>
              </select>
            </div>
          </div>
          
          {/* Desktop Table View - Hidden on Mobile */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 border-b border-gray-200">
                    <div className="flex items-center">
                      Charm
                      <i className="fas fa-sort ml-1 text-gray-400"></i>
                    </div>
                  </th>
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 border-b border-gray-200">
                    <div className="flex items-center">
                      Price
                      <i className="fas fa-sort ml-1 text-gray-400"></i>
                    </div>
                  </th>
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 border-b border-gray-200">
                    <div className="flex items-center">
                      7-Day Change
                      <i className="fas fa-sort ml-1 text-gray-400"></i>
                    </div>
                  </th>
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 border-b border-gray-200">
                    <div className="flex items-center">
                      Material
                      <i className="fas fa-sort ml-1 text-gray-400"></i>
                    </div>
                  </th>
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 border-b border-gray-200">
                    <div className="flex items-center">
                      Status
                      <i className="fas fa-sort ml-1 text-gray-400"></i>
                    </div>
                  </th>
                  <th className="py-3 px-4 text-left font-semibold text-gray-600 border-b border-gray-200">
                    <div className="flex items-center">
                      Popularity
                      <i className="fas fa-sort ml-1 text-gray-400"></i>
                    </div>
                  </th>
                  <th className="py-3 px-4 text-center font-semibold text-gray-600 border-b border-gray-200">Action</th>
                </tr>
              </thead>
              <tbody>
                {charms.map((charm) => (
                  <tr key={charm.id} className="hover:bg-gray-50 cursor-pointer">
                    <td className="py-3 px-4 border-b border-gray-200">
                      <div className="flex items-center">
                        <div className="w-10 h-10 rounded-md mr-3 overflow-hidden">
                          <img 
                            src={getCharmImage(charm.name)} 
                            alt={charm.name} 
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <span className="font-medium text-gray-800">{charm.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 border-b border-gray-200 font-semibold text-amber-500">
                      ${charm.price.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 border-b border-gray-200">
                      <div className={`flex items-center ${charm.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        <i className={`fas ${charm.change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'} mr-1 text-xs`}></i>
                        {Math.abs(charm.change)}%
                      </div>
                    </td>
                    <td className="py-3 px-4 border-b border-gray-200">
                      <span className={`px-2 py-1 rounded-full text-xs ${charm.material === 'Gold' ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-800'}`}>
                        {charm.material}
                      </span>
                    </td>
                    <td className="py-3 px-4 border-b border-gray-200">
                      <span className={`px-2 py-1 rounded-full text-xs ${charm.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {charm.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 border-b border-gray-200">
                      <div className="flex items-center">
                        <div className="w-20 h-2 bg-gray-200 rounded-full mr-2">
                          <div 
                            className={`h-2 rounded-full ${charm.popularity === 'High' ? 'bg-green-500 w-5/6' : charm.popularity === 'Medium' ? 'bg-amber-500 w-1/2' : 'bg-red-500 w-1/4'}`}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">{charm.popularity}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 border-b border-gray-200 text-center">
                      <button className="text-amber-500 hover:text-amber-600 focus:outline-none">
                        <i className="fas fa-star mr-1"></i>
                        Watch
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Mobile Card View - Only visible on Mobile and Tablets */}
          <div className="md:hidden p-4">
            {renderMobileCharmCards()}
          </div>
          
          {/* Pagination - Responsive for all devices */}
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            {/* Mobile pagination */}
            <div className="flex justify-between items-center md:hidden">
              <button className="px-4 py-2 border rounded-md bg-white text-gray-700 text-sm">
                Previous
              </button>
              <span className="text-sm text-gray-600">Page 1 of 4</span>
              <button className="px-4 py-2 border rounded-md bg-white text-gray-700 text-sm">
                Next
              </button>
            </div>
            
            {/* Desktop pagination */}
            <div className="hidden md:flex md:items-center md:justify-between">
              <div>
                <button className="px-4 py-2 border rounded-md bg-white text-gray-700 text-sm">
                  <i className="fas fa-chevron-left mr-2"></i>
                  Previous
                </button>
              </div>
              
              <div className="flex">
                <button className="px-4 py-2 border rounded-l-md bg-amber-500 text-white text-sm">
                  1
                </button>
                <button className="px-4 py-2 border-t border-b border-l bg-white text-gray-700 text-sm">
                  2
                </button>
                <button className="px-4 py-2 border-t border-b border-l bg-white text-gray-700 text-sm">
                  3
                </button>
                <button className="px-4 py-2 border rounded-r-md bg-white text-gray-700 text-sm">
                  4
                </button>
              </div>
              
              <div>
                <button className="px-4 py-2 border rounded-md bg-white text-gray-700 text-sm">
                  Next
                  <i className="fas fa-chevron-right ml-2"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="text-center mt-8">
          <button className="bg-gray-800 hover:bg-gray-900 text-white px-6 py-3 rounded-lg shadow-md transition-colors inline-flex items-center">
            <i className="fas fa-th-list mr-2"></i>
            View Full Database
          </button>
        </div>
      </div>
    </section>
  );
};

export default SampleTable;