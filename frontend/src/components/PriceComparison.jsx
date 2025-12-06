import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, AlertCircle } from 'lucide-react';

/**
 * PriceComparison Component
 * Displays price comparison across James Avery, eBay, Etsy, and Poshmark
 * with a visual bar chart showing price differences
 */
export const PriceComparison = ({ charm }) => {
  // Calculate average prices by marketplace
  const marketplacePrices = useMemo(() => {
    if (!charm || !charm.listings) {
      return null;
    }

    const prices = {
      'James Avery': {
        price: charm.james_avery_price || null,
        count: charm.james_avery_price ? 1 : 0,
        color: '#c9a94d',
        isOfficial: true
      },
      'eBay': {
        prices: [],
        count: 0,
        color: '#e53238'
      },
      'Etsy': {
        prices: [],
        count: 0,
        color: '#f1641e'
      },
      'Poshmark': {
        prices: [],
        count: 0,
        color: '#8c1645'
      }
    };

    // Group listings by platform and calculate averages
    charm.listings.forEach(listing => {
      // Capitalize platform name to match keys (ebay -> eBay, etsy -> Etsy, poshmark -> Poshmark)
      const platformKey = listing.platform.charAt(0).toUpperCase() + listing.platform.slice(1);
      const platform = platformKey === 'Ebay' ? 'eBay' : platformKey;
      if (prices[platform] && !prices[platform].isOfficial) {
        prices[platform].prices.push(listing.price);
        prices[platform].count++;
      }
    });

    // Calculate average for each marketplace
    const result = {};
    Object.keys(prices).forEach(platform => {
      if (prices[platform].isOfficial) {
        result[platform] = {
          avg: prices[platform].price,
          count: prices[platform].count,
          color: prices[platform].color,
          min: prices[platform].price,
          max: prices[platform].price
        };
      } else if (prices[platform].prices.length > 0) {
        const priceList = prices[platform].prices;
        result[platform] = {
          avg: priceList.reduce((a, b) => a + b, 0) / priceList.length,
          count: prices[platform].count,
          color: prices[platform].color,
          min: Math.min(...priceList),
          max: Math.max(...priceList)
        };
      }
    });

    return result;
  }, [charm]);

  // Prepare chart data
  const chartData = useMemo(() => {
    if (!marketplacePrices) return [];

    return Object.entries(marketplacePrices)
      .filter(([_, data]) => data.avg !== null)
      .map(([platform, data]) => ({
        platform,
        price: parseFloat(data.avg.toFixed(2)),
        count: data.count,
        color: data.color,
        min: data.min,
        max: data.max
      }))
      .sort((a, b) => b.price - a.price);
  }, [marketplacePrices]);

  // Calculate price differences from James Avery price
  const priceDifferences = useMemo(() => {
    if (!marketplacePrices || !marketplacePrices['James Avery']) return null;

    const jamesAveryPrice = marketplacePrices['James Avery'].avg;
    const differences = {};

    Object.entries(marketplacePrices).forEach(([platform, data]) => {
      if (platform !== 'James Avery' && data.avg !== null) {
        const diff = data.avg - jamesAveryPrice;
        const percentDiff = ((diff / jamesAveryPrice) * 100).toFixed(1);
        differences[platform] = {
          amount: diff,
          percent: parseFloat(percentDiff),
          savings: diff < 0
        };
      }
    });

    return differences;
  }, [marketplacePrices]);

  // Calculate best deal
  const bestDeal = useMemo(() => {
    if (!chartData || chartData.length === 0) return null;
    return chartData.reduce((best, current) => 
      current.price < best.price ? current : best
    , chartData[0]);
  }, [chartData]);

  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div 
          className="p-4" 
          style={{ 
            background: '#ffffff', 
            border: '2px solid #c9a94d',
            borderRadius: '0px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}
        >
          <p className="font-semibold mb-2" style={{ color: '#333333' }}>
            {data.platform}
          </p>
          <p className="text-lg font-bold mb-1" style={{ color: data.color }}>
            ${data.price.toFixed(2)}
          </p>
          <p className="text-sm" style={{ color: '#666666' }}>
            {data.count} listing{data.count !== 1 ? 's' : ''}
          </p>
          {data.min !== data.max && (
            <p className="text-xs mt-1" style={{ color: '#999999' }}>
              Range: ${data.min.toFixed(2)} - ${data.max.toFixed(2)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // If no real data, show message
  if (!marketplacePrices || chartData.length === 0) {
    return (
      <div className="bg-white p-6 md:p-8 text-center" style={{ border: '2px solid #c9a94d', borderRadius: '0px' }}>
        <AlertCircle className="w-12 h-12 mx-auto mb-4" style={{ color: '#c9a94d' }} />
        <h3 className="heading-3 mb-2">No Price Data Available</h3>
        <p className="body-regular" style={{ color: '#666666' }}>
          Click "🔍 Fetch Live Prices" above to get current marketplace pricing.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 md:p-8" style={{ border: '2px solid #c9a94d', borderRadius: '0px' }}>
      <div className="mb-6">
        <h2 className="heading-2 mb-2">Marketplace Price Comparison</h2>
        <p className="body-regular" style={{ color: '#666666' }}>
          Compare prices across different platforms to find the best deal
        </p>
      </div>

      {/* Best Deal Highlight */}
      {bestDeal && (
        <div 
          className="mb-6 p-4 flex items-center gap-3" 
          style={{ background: '#f6f5e8', border: '1px solid #c9a94d', borderRadius: '0px' }}
        >
          <DollarSign className="w-6 h-6" style={{ color: '#c9a94d' }} />
          <div>
            <p className="font-semibold" style={{ color: '#333333' }}>
              Best Deal: {bestDeal.platform}
            </p>
            <p className="body-small" style={{ color: '#666666' }}>
              ${bestDeal.price.toFixed(2)} average from {bestDeal.count} listing{bestDeal.count !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      )}

      {/* Price Comparison Chart */}
      <div className="mb-8">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart 
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis 
              dataKey="platform" 
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fill: '#666666', fontSize: 12 }}
            />
            <YAxis 
              label={{ value: 'Price ($)', angle: -90, position: 'insideLeft', style: { fill: '#666666' } }}
              tick={{ fill: '#666666', fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="price" radius={[0, 0, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Price Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {Object.entries(marketplacePrices).map(([platform, data]) => (
          data.avg !== null && (
            <div 
              key={platform}
              className="p-4"
              style={{ 
                background: '#f9f9f9',
                border: '1px solid #e5e5e5',
                borderRadius: '0px'
              }}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold" style={{ color: '#333333' }}>
                    {platform}
                  </h4>
                  <p className="text-xs" style={{ color: '#999999' }}>
                    {data.count} listing{data.count !== 1 ? 's' : ''}
                  </p>
                </div>
                <p className="text-xl font-bold" style={{ color: data.color }}>
                  ${data.avg.toFixed(2)}
                </p>
              </div>
              
              {data.min !== data.max && (
                <div className="text-sm mb-2" style={{ color: '#666666' }}>
                  <span>Range: ${data.min.toFixed(2)} - ${data.max.toFixed(2)}</span>
                </div>
              )}

              {/* Price Difference from James Avery */}
              {priceDifferences && priceDifferences[platform] && (
                <div className="flex items-center gap-2 mt-2">
                  {priceDifferences[platform].savings ? (
                    <TrendingDown className="w-4 h-4" style={{ color: '#2d8659' }} />
                  ) : (
                    <TrendingUp className="w-4 h-4" style={{ color: '#ba3e2b' }} />
                  )}
                  <span 
                    className="text-sm font-medium"
                    style={{ 
                      color: priceDifferences[platform].savings ? '#2d8659' : '#ba3e2b' 
                    }}
                  >
                    {priceDifferences[platform].savings ? 'Save' : 'Pay'} $
                    {Math.abs(priceDifferences[platform].amount).toFixed(2)} (
                    {priceDifferences[platform].savings ? '' : '+'}
                    {priceDifferences[platform].percent}%)
                  </span>
                  <span className="text-xs" style={{ color: '#999999' }}>
                    vs. James Avery
                  </span>
                </div>
              )}
            </div>
          )
        ))}
      </div>

      {/* Summary Statistics */}
      {chartData.length > 1 && (
        <div 
          className="p-4" 
          style={{ 
            background: '#f3f3f3',
            border: '1px solid #bcbcbc',
            borderRadius: '0px'
          }}
        >
          <h4 className="font-semibold mb-2" style={{ color: '#333333' }}>
            Summary
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs mb-1" style={{ color: '#666666' }}>Lowest Price</p>
              <p className="font-semibold" style={{ color: '#2d8659' }}>
                ${Math.min(...chartData.map(d => d.price)).toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs mb-1" style={{ color: '#666666' }}>Highest Price</p>
              <p className="font-semibold" style={{ color: '#ba3e2b' }}>
                ${Math.max(...chartData.map(d => d.price)).toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs mb-1" style={{ color: '#666666' }}>Price Range</p>
              <p className="font-semibold" style={{ color: '#333333' }}>
                ${(Math.max(...chartData.map(d => d.price)) - Math.min(...chartData.map(d => d.price))).toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs mb-1" style={{ color: '#666666' }}>Total Listings</p>
              <p className="font-semibold" style={{ color: '#333333' }}>
                {chartData.reduce((sum, d) => sum + d.count, 0)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PriceComparison;
