import React from 'react';

const SampleTable = () => {
  const charms = [
    {
      id: 1,
      name: 'Heart Charm',
      image: '',
      price: 32.50,
      change: 5.2,
      material: 'Silver',
      status: 'Active',
      popularity: 'High'
    },
    {
      id: 2,
      name: 'Texas Charm',
      image: '',
      price: 42.75,
      change: -1.3,
      material: 'Silver',
      status: 'Active',
      popularity: 'Medium'
    },
    {
      id: 3,
      name: 'Cross Charm',
      image: '',
      price: 38.00,
      change: 2.8,
      material: 'Silver',
      status: 'Active',
      popularity: 'High'
    },
    {
      id: 4,
      name: 'Dove Charm',
      image: '',
      price: 45.25,
      change: 0.5,
      material: 'Silver',
      status: 'Retired',
      popularity: 'Medium'
    },
    {
      id: 5,
      name: 'Gold Heart Charm',
      image: '',
      price: 120.00,
      change: 8.5,
      material: 'Gold',
      status: 'Active',
      popularity: 'High'
    }
  ];

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Explore the Charm Database</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Our comprehensive database provides real-time pricing and availability for all James Avery charms.
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="flex justify-between items-center p-4 border-b border-gray-200 bg-gray-50">
            <h3 className="text-xl font-semibold text-gray-800">Popular Charms</h3>
            <div className="flex items-center">
              <div className="relative mr-2">
                <input 
                  type="text" 
                  placeholder="Filter charms..." 
                  className="pl-8 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 w-48"
                />
                <i className="fas fa-search absolute left-3 top-3 text-gray-400 text-sm"></i>
              </div>
              <select className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-gray-800 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500">
                <option>All Materials</option>
                <option>Silver</option>
                <option>Gold</option>
                <option>Other</option>
              </select>
            </div>
          </div>
          
          <div className="overflow-x-auto">
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
                        <div className="w-10 h-10 bg-gray-200 rounded-md mr-3"></div>
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
          
          <div className="px-4 py-3 flex items-center justify-between border-t border-gray-200 bg-gray-50">
            <div className="flex-1 flex justify-between items-center">
              <button className="px-4 py-2 border rounded-md bg-white text-gray-700 text-sm">
                Previous
              </button>
              <div className="hidden md:flex">
                <button className="px-4 py-2 border-t border-b border-l rounded-l-md bg-amber-500 text-white text-sm">
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
              <button className="px-4 py-2 border rounded-md bg-white text-gray-700 text-sm">
                Next
              </button>
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