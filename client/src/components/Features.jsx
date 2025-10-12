import React from 'react';

const Features = () => {
  const features = [
    {
      icon: 'fa-database',
      title: 'Charm Database Table',
      description: 'Large, filterable, sortable table showing charm details, pricing, and availability.'
    },
    {
      icon: 'fa-chart-line',
      title: 'Price History',
      description: 'Detailed price charts with trends over time (7d, 30d, 90d, 1y).'
    },
    {
      icon: 'fa-search',
      title: 'Advanced Search & Filtering',
      description: 'Filter by price, category, material, status, and popularity.'
    },
    {
      icon: 'fa-tachometer-alt',
      title: 'Market Overview Dashboard',
      description: 'Track trending charms, price indexes, and market movements.'
    },
    {
      icon: 'fa-bell',
      title: 'Alerts & Updates',
      description: 'No login needed - track favorites with browser storage.'
    },
    {
      icon: 'fa-list',
      title: 'Watchlist',
      description: 'Easily manage and track your favorite charms in one place.'
    }
  ];

  return (
    <section className="py-16 bg-white" id="how-it-works">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Core Features</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Everything you need to track, monitor, and analyze the James Avery charm market.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-gray-50 rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mb-4">
                <i className={`fas ${feature.icon} text-amber-500 text-xl`}></i>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;