import React, { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, TrendingUp, TrendingDown, Heart, ExternalLink, 
  RefreshCw, Clock, CheckCircle, AlertCircle 
} from 'lucide-react';
import { charmAPI, watchlistUtils, realtimeUtils } from '../services/api';
import PriceHistoryChart from '../components/PriceHistoryChart';
import { MarketDataTable } from '../components/MarketDataTable';
import { PriceComparison } from '../components/PriceComparison';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '../components/ui/carousel';

export const CharmDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [charm, setCharm] = useState(null);
  const [relatedCharms, setRelatedCharms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [selectedImage, setSelectedImage] = useState(0);
  const [marketplaceStatus, setMarketplaceStatus] = useState(null);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const [scraperRunning, setScraperRunning] = useState(false);

  useEffect(() => {
    fetchCharmDetail();
    
    // Auto-refresh every 30 seconds
    const cleanup = realtimeUtils.startAutoRefresh(
      id, 
      (data) => {
        setCharm(data);
        setLastUpdateTime(data.last_updated);
      },
      30000
    );
    
    return cleanup;
  }, [id]);

  useEffect(() => {
    if (charm) {
      setIsInWatchlist(watchlistUtils.isInWatchlist(charm.id));
      setLastUpdateTime(charm.last_updated);
    }
  }, [charm]);

  const fetchCharmDetail = async () => {
    try {
      setLoading(true);
      const data = await charmAPI.getCharmById(id);
      setCharm(data);

      // 🔍 DETAILED CONSOLE LOGGING FOR MARKETPLACE DATA
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('📦 CHARM DATA RECEIVED:', data.name);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      
      // Log listings by platform
      if (data.listings && data.listings.length > 0) {
        console.log(`✅ Total Listings Found: ${data.listings.length}`);
        
        const ebayListings = data.listings.filter(l => l.platform === 'eBay');
        const etsyListings = data.listings.filter(l => l.platform === 'Etsy');
        const poshmarkListings = data.listings.filter(l => l.platform === 'Poshmark');
        
        console.log(`🛒 eBay: ${ebayListings.length} listings`);
        if (ebayListings.length > 0) {
          console.log('  Sample eBay listing:', ebayListings[0]);
        }
        
        console.log(`🎨 Etsy: ${etsyListings.length} listings`);
        if (etsyListings.length > 0) {
          console.log('  Sample Etsy listing:', etsyListings[0]);
        }
        
        console.log(`👗 Poshmark: ${poshmarkListings.length} listings`);
        if (poshmarkListings.length > 0) {
          console.log('  ✅ POSHMARK DATA IS WORKING!');
          console.log('  Sample Poshmark listing:', poshmarkListings[0]);
          console.log('  Poshmark Prices:', poshmarkListings.map(l => `$${l.price}`).join(', '));
        } else {
          console.log('  ⚠️ NO POSHMARK DATA - Check backend logs');
        }
        
        // Log price data
        console.log('\n💰 PRICE ANALYSIS:');
        console.log(`  Average Price: $${data.average_price?.toFixed(2) || 'N/A'}`);
        console.log(`  James Avery Price: $${data.james_avery_price?.toFixed(2) || 'N/A'}`);
        
        // Log images
        console.log('\n🖼️ IMAGES:');
        console.log(`  Total Images: ${data.images?.length || 0}`);
        if (data.images && data.images.length > 0) {
          console.log('  First Image URL:', data.images[0]);
        }
        
      } else {
        console.log('⚠️ NO LISTINGS FOUND for this charm');
      }
      
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

      // Fetch related charms
      if (data.related_charm_ids && data.related_charm_ids.length > 0) {
        const relatedPromises = data.related_charm_ids.slice(0, 4).map(relatedId =>
          charmAPI.getCharmById(relatedId).catch(() => null)
        );
        const related = await Promise.all(relatedPromises);
        setRelatedCharms(related.filter(c => c !== null));
      }

      // Check marketplace availability
      checkMarketplaceAvailability(data.name);
    } catch (error) {
      console.error('❌ Error fetching charm detail:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkMarketplaceAvailability = async (charmName) => {
    try {
      const status = await charmAPI.checkMarketplaceAvailability(charmName);
      setMarketplaceStatus(status);
    } catch (error) {
      console.error('Error checking marketplace:', error);
    }
  };

  const handleFetchLivePrices = async () => {
    try {
      setUpdating(true);
      console.log('🔍 FETCHING LIVE PRICES for charm:', charm.name);
      
      const result = await charmAPI.fetchLivePrices(id);
      
      console.log('✅ Live prices fetched:');
      console.log(`   🎨 Etsy: ${result.summary.etsy.count} listings`);
      console.log(`   🛒 eBay: ${result.summary.ebay.count} listings`);
      console.log(`   👗 Poshmark: ${result.summary.poshmark.count} listings`);
      console.log(`   💰 Average: $${result.average_price}`);
      
      // Refresh charm data
      await fetchCharmDetail();
      setUpdating(false);
      
      alert(`✅ Live prices fetched!\n\nEtsy: ${result.summary.etsy.count} listings\neBay: ${result.summary.ebay.count} listings\nPoshmark: ${result.summary.poshmark.count} listings\n\nAverage Price: $${result.average_price}`);
    } catch (error) {
      console.error('❌ Error fetching live prices:', error);
      setUpdating(false);
      alert('❌ Error fetching live prices. Check console for details.');
    }
  };

  const handleForceUpdate = async () => {
    try {
      setUpdating(true);
      console.log('🔄 TRIGGERING CHARM UPDATE for ID:', id);
      
      await charmAPI.updateCharm(id);
      
      console.log('✅ Update request sent, waiting for data refresh...');
      
      // Wait a few seconds then refresh
      setTimeout(async () => {
        await fetchCharmDetail();
        setUpdating(false);
        console.log('✅ Charm data refreshed after update');
      }, 3000);
    } catch (error) {
      console.error('❌ Error updating charm:', error);
      setUpdating(false);
    }
  };

  const handleRefreshAllData = async () => {
    try {
      setScraperRunning(true);
      await charmAPI.triggerJamesAveryScrape();
      
      // Show notification
      alert('🔄 Data refresh started! This will update all charm data from marketplace sources. Check back in a few minutes for updated data.');
      
      setScraperRunning(false);
    } catch (error) {
      console.error('Error triggering scraper:', error);
      alert('❌ Error starting data refresh. Please try again.');
      setScraperRunning(false);
    }
  };

  const toggleWatchlist = () => {
    if (isInWatchlist) {
      watchlistUtils.removeFromWatchlist(charm.id);
      setIsInWatchlist(false);
    } else {
      watchlistUtils.addToWatchlist(charm.id);
      setIsInWatchlist(true);
    }
  };

  // Auto-refresh data every 5 minutes
  useEffect(() => {
    const fetchData = async () => {
      if (id) {
        const data = await charmAPI.getCharmById(id);
        setCharm(data);
      }
    };

    // Initial fetch
    fetchData();

    // Set up auto-refresh
    const refreshInterval = setInterval(fetchData, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(refreshInterval);
  }, [id]);

  const chartData = useMemo(() => {
    if (!charm || !charm.price_history || charm.price_history.length === 0) return [];
    
    // Get last 90 days of price history
    return charm.price_history
      .slice(-90)
      .map(entry => ({
        date: new Date(entry.date),
        price: entry.price
      }))
      .filter(entry => !isNaN(entry.date.getTime()))
      .sort((a, b) => a.date - b.date);
  }, [charm]);

  const needsUpdate = charm ? realtimeUtils.needsRefresh(charm.last_updated, 30) : false;

  if (loading) {
    return (
      <div className="min-h-screen pt-24 pb-16" style={{ background: '#f3f3f3' }}>
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <div className="animate-pulse">
            <div className="h-96 bg-gray-200 mb-8" />
            <div className="h-8 bg-gray-200 w-1/3 mb-4" />
            <div className="h-4 bg-gray-200 w-2/3" />
          </div>
        </div>
      </div>
    );
  }

  if (!charm) {
    return (
      <div className="min-h-screen pt-24 pb-16" style={{ background: '#f3f3f3' }}>
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12 text-center">
          <h2 className="heading-1 mb-4">Charm Not Found</h2>
          <button
            onClick={() => navigate('/browse')}
            className="btn-primary"
            style={{
              background: 'transparent',
              color: '#333333',
              border: '1px solid #333333',
              borderRadius: '0px',
              padding: '19px 23px',
              minWidth: '210px',
              height: '60px'
            }}
          >
            Browse All Charms
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-16" style={{ background: '#f3f3f3' }}>
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 mb-8 body-regular transition-smooth hover:text-[#c9a94d]"
          style={{ color: '#666666' }}
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </button>

        {/* Update Status Bar */}
        <div className="mb-6 p-4 bg-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 sm:gap-0" style={{ border: '1px solid #bcbcbc' }}>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5" style={{ color: '#666666' }} />
              <span className="body-small" style={{ color: '#666666' }}>
                Last updated: {realtimeUtils.timeSinceUpdate(lastUpdateTime)}
              </span>
            </div>
            {needsUpdate && (
              <span className="flex items-center gap-1 body-small" style={{ color: '#c9a94d' }}>
                <AlertCircle className="w-4 h-4" />
                Data may be outdated
              </span>
            )}
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
            <button
              onClick={handleForceUpdate}
              disabled={updating}
              className="flex items-center gap-2 px-4 py-2 transition-smooth flex-1 sm:flex-initial"
              style={{
                background: updating ? '#f3f3f3' : '#c9a94d',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0px',
                opacity: updating ? 0.6 : 1,
                cursor: updating ? 'wait' : 'pointer'
              }}
              title="Refresh marketplace data for this charm"
            >
              <RefreshCw className={`w-4 h-4 ${updating ? 'animate-spin' : ''}`} />
              {updating ? 'Updating...' : 'Refresh Charm'}
            </button>
            <button
              onClick={handleFetchLivePrices}
              disabled={updating}
              className="flex items-center gap-2 px-4 py-2 transition-smooth flex-1 sm:flex-initial"
              style={{
                background: updating ? '#f3f3f3' : '#2d8659',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0px',
                opacity: updating ? 0.6 : 1,
                cursor: updating ? 'wait' : 'pointer',
                fontWeight: '600'
              }}
              title="Fetch live prices from Etsy, eBay, and Poshmark"
            >
              <RefreshCw className={`w-4 h-4 ${updating ? 'animate-spin' : ''}`} />
              {updating ? 'Fetching...' : '🔍 Fetch Live Prices'}
            </button>
            <button
              onClick={handleRefreshAllData}
              disabled={scraperRunning}
              className="flex items-center gap-2 px-4 py-2 transition-smooth flex-1 sm:flex-initial"
              style={{
                background: scraperRunning ? '#f3f3f3' : 'transparent',
                color: scraperRunning ? '#999999' : '#c9a94d',
                border: '1px solid #c9a94d',
                borderRadius: '0px',
                opacity: scraperRunning ? 0.6 : 1,
                cursor: scraperRunning ? 'wait' : 'pointer'
              }}
              title="Update all charms from marketplace sources"
            >
              <RefreshCw className={`w-4 h-4 ${scraperRunning ? 'animate-spin' : ''}`} />
              {scraperRunning ? 'Updating...' : 'Refresh All Data'}
            </button>
          </div>
        </div>

        {/* Auto-Update Info */}
        <div className="mb-6 p-3 flex items-center gap-2" style={{ background: '#f6f5e8', border: '1px solid #c9a94d' }}>
          <CheckCircle className="w-5 h-5" style={{ color: '#c9a94d' }} />
          <span className="body-small" style={{ color: '#666666' }}>
            <strong>Auto-Update:</strong> Data automatically refreshes from marketplace sources. Use "Fetch Live Prices" to get real-time data from Etsy, eBay, and Poshmark.
          </span>
        </div>

        {/* Marketplace Availability */}
        {marketplaceStatus && (
          <div className="mb-6 p-4 bg-white" style={{ border: '1px solid #bcbcbc' }}>
            <h3 className="heading-3 mb-3">Marketplace Availability</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(marketplaceStatus.availability).map(([platform, status]) => (
                <div key={platform} className="flex items-center gap-2">
                  {status.available ? (
                    <CheckCircle className="w-5 h-5" style={{ color: '#2d8659' }} />
                  ) : (
                    <AlertCircle className="w-5 h-5" style={{ color: '#ba3e2b' }} />
                  )}
                  <div>
                    <p className="body-small font-semibold capitalize">{platform}</p>
                    <p className="text-xs" style={{ color: '#666666' }}>
                      {status.listing_count} listings
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* Image Gallery/Carousel */}
          <div>
            {charm.images.length > 1 ? (
              // Carousel for multiple images
              <div className="relative">
                <Carousel
                  opts={{
                    align: "start",
                    loop: true,
                  }}
                  className="w-full"
                >
                  <CarouselContent>
                    {charm.images.map((img, index) => (
                      <CarouselItem key={index}>
                        <div className="bg-white p-4" style={{ border: 'none', borderRadius: '0px' }}>
                          <img
                            src={img}
                            alt={`${charm.name} - Image ${index + 1}`}
                            className="w-full h-96 object-cover"
                          />
                        </div>
                      </CarouselItem>
                    ))}
                  </CarouselContent>
                  <CarouselPrevious 
                    className="left-4"
                    style={{
                      background: 'rgba(255, 255, 255, 0.9)',
                      border: '1px solid #c9a94d',
                      color: '#c9a94d'
                    }}
                  />
                  <CarouselNext 
                    className="right-4"
                    style={{
                      background: 'rgba(255, 255, 255, 0.9)',
                      border: '1px solid #c9a94d',
                      color: '#c9a94d'
                    }}
                  />
                </Carousel>
                {/* Thumbnail Navigation */}
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2 mt-4">
                  {charm.images.map((img, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImage(index)}
                      className="transition-smooth"
                      style={{
                        border: selectedImage === index ? '2px solid #c9a94d' : '1px solid #bcbcbc',
                        borderRadius: '0px',
                        overflow: 'hidden'
                      }}
                    >
                      <img
                        src={img}
                        alt={`${charm.name} thumbnail ${index + 1}`}
                        className="w-full h-16 sm:h-20 object-contain md:object-cover"
                      />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              // Single image display
              <div className="bg-white p-4" style={{ border: 'none', borderRadius: '0px' }}>
                <img
                  src={charm.images[0]}
                  alt={charm.name}
                  className="w-full h-[250px] sm:h-[300px] md:h-[400px] lg:h-96 object-contain md:object-cover"
                />
              </div>
            )}
          </div>

          {/* Charm Details */}
          <div>
            <div className="flex flex-col sm:flex-row items-start justify-between gap-4 sm:gap-0 mb-4">
              <div className="w-full sm:w-auto">
                <h1 className="heading-1 mb-2 text-2xl sm:text-3xl md:text-4xl">{charm.name}</h1>
                <div className="flex flex-wrap items-center gap-2 sm:gap-4 mb-4">
                  <span className="body-regular" style={{ color: '#666666' }}>
                    Material: {charm.material}
                  </span>
                  <span
                    className="px-2 sm:px-3 py-1 text-xs sm:text-sm"
                    style={{
                      background: charm.status === 'Retired' ? '#f6f5e8' : 'transparent',
                      border: `1px solid ${charm.status === 'Retired' ? '#bcbcbc' : '#c9a94d'}`,
                      borderRadius: '0px',
                      color: '#333333'
                    }}
                  >
                    {charm.status}
                  </span>
                </div>
              </div>
              <button
                onClick={toggleWatchlist}
                className="p-2 sm:p-3 transition-smooth"
                style={{
                  background: isInWatchlist ? '#c9a94d' : 'transparent',
                  border: '1px solid #c9a94d',
                  borderRadius: '0px'
                }}
              >
                <Heart
                  className="w-6 h-6"
                  style={{ color: isInWatchlist ? '#ffffff' : '#c9a94d' }}
                  fill={isInWatchlist ? '#ffffff' : 'none'}
                />
              </button>
            </div>

            <div className="mb-6">
              <div className="flex flex-wrap items-baseline gap-2 sm:gap-4 mb-2">
                <span className="text-3xl sm:text-4xl font-semibold" style={{ color: '#333333' }}>
                  ${charm.avg_price.toFixed(2)}
                </span>
                {(!charm.listings || charm.listings.length === 0) && (
                  <span 
                    className="text-xs sm:text-sm px-2 sm:px-3 py-1" 
                    style={{ 
                      background: '#f6f5e8', 
                      color: '#666666',
                      border: '1px solid #bcbcbc',
                      borderRadius: '0px'
                    }}
                    title="Price from James Avery official or historical data"
                  >
                    Estimated
                  </span>
                )}
                <div
                  className="flex items-center gap-1 text-lg font-medium"
                  style={{ color: charm.price_change_7d >= 0 ? '#2d8659' : '#ba3e2b' }}
                >
                  {charm.price_change_7d >= 0 ? (
                    <TrendingUp className="w-5 h-5" />
                  ) : (
                    <TrendingDown className="w-5 h-5" />
                  )}
                  {Math.abs(charm.price_change_7d)}% (7d)
                </div>
              </div>
              <p className="body-small" style={{ color: '#666666' }}>
                {charm.listings && charm.listings.length > 0 
                  ? `Average market price from ${charm.listings.length} live listings`
                  : 'Price based on James Avery official pricing or historical data'
                }
              </p>
            </div>

            <p className="body-regular mb-8" style={{ color: '#666666' }}>
              {charm.description}
            </p>

            {/* Price Changes */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="p-4" style={{ background: '#ffffff', borderRadius: '0px' }}>
                <p className="body-small mb-1" style={{ color: '#666666' }}>
                  7 Days
                </p>
                <p
                  className="text-lg font-semibold"
                  style={{ color: charm.price_change_7d >= 0 ? '#2d8659' : '#ba3e2b' }}
                >
                  {charm.price_change_7d >= 0 ? '+' : ''}{charm.price_change_7d}%
                </p>
              </div>
              <div className="p-4" style={{ background: '#ffffff', borderRadius: '0px' }}>
                <p className="body-small mb-1" style={{ color: '#666666' }}>
                  30 Days
                </p>
                <p
                  className="text-lg font-semibold"
                  style={{ color: charm.price_change_30d >= 0 ? '#2d8659' : '#ba3e2b' }}
                >
                  {charm.price_change_30d >= 0 ? '+' : ''}{charm.price_change_30d}%
                </p>
              </div>
              <div className="p-4" style={{ background: '#ffffff', borderRadius: '0px' }}>
                <p className="body-small mb-1" style={{ color: '#666666' }}>
                  90 Days
                </p>
                <p
                  className="text-lg font-semibold"
                  style={{ color: charm.price_change_90d >= 0 ? '#2d8659' : '#ba3e2b' }}
                >
                  {charm.price_change_90d >= 0 ? '+' : ''}{charm.price_change_90d}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Price Comparison Chart */}
        <div className="mb-16">
          <PriceComparison charm={charm} />
        </div>

        {/* Price History Chart */}
        {charm && charm.price_history && charm.price_history.length > 0 && (
          <div className="mb-16 bg-white p-8" style={{ border: '2px solid #c9a94d', borderRadius: '0px' }}>
            <h2 className="heading-2 mb-6">Price History (Last 30 Days)</h2>
            <div className="w-full h-[400px] bg-white rounded-lg shadow-sm p-4">
              <PriceHistoryChart priceHistory={chartData} />
            </div>
            <p className="text-center mt-4 body-small" style={{ color: '#999999' }}>
              Real-time aggregated pricing from eBay, Etsy, Poshmark and more
            </p>
          </div>
        )}

        {/* Active Listings */}
        {charm.listings && charm.listings.length > 0 ? (
          <div className="mb-16">
            <div className="flex items-center justify-between mb-6">
              <h2 className="heading-2">Active Listings ({charm.listings.length})</h2>
              <span className="body-small" style={{ color: '#666666' }}>
                Updated {realtimeUtils.timeSinceUpdate(charm.last_updated)}
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {charm.listings.slice(0, 9).map((listing, index) => (
                <a
                  key={index}
                  href={listing.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-white p-6 transition-smooth hover:shadow-lg"
                  style={{ border: '1px solid #bcbcbc', borderRadius: '0px', textDecoration: 'none' }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="body-regular font-semibold" style={{ color: '#333333' }}>
                      {listing.platform}
                    </span>
                    <ExternalLink className="w-4 h-4" style={{ color: '#c9a94d' }} />
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-2xl font-semibold" style={{ color: '#333333' }}>
                      ${listing.price.toFixed(2)}
                    </span>
                    {listing.shipping > 0 && (
                      <span className="body-small" style={{ color: '#666666' }}>
                        +${listing.shipping} shipping
                      </span>
                    )}
                  </div>
                  <p className="body-small" style={{ color: '#666666' }}>
                    Condition: {listing.condition}
                  </p>
                  {listing.seller && (
                    <p className="body-small" style={{ color: '#999999' }}>
                      Seller: {listing.seller}
                    </p>
                  )}
                </a>
              ))}
            </div>
          </div>
        ) : (
          <div className="mb-16 bg-white p-8" style={{ border: '1px solid #bcbcbc', borderRadius: '0px' }}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="heading-2">Active Listings</h2>
              <span className="body-small" style={{ color: '#666666' }}>
                Updated {realtimeUtils.timeSinceUpdate(charm.last_updated)}
              </span>
            </div>
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 mx-auto mb-4" style={{ color: '#c9a94d' }} />
              <h3 className="heading-3 mb-2">No Active Listings Found</h3>
              <p className="body-regular mb-4" style={{ color: '#666666' }}>
                We couldn't find any active marketplace listings for this charm at the moment.
              </p>
              {charm.james_avery_price && (
                <div className="bg-gray-50 p-6 max-w-md mx-auto" style={{ borderRadius: '0px' }}>
                  <p className="body-small mb-2" style={{ color: '#666666' }}>
                    Official James Avery Price
                  </p>
                  <p className="text-3xl font-semibold mb-3" style={{ color: '#333333' }}>
                    ${charm.james_avery_price.toFixed(2)}
                  </p>
                  {charm.james_avery_url && (
                    <a
                      href={charm.james_avery_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-6 py-3 transition-smooth"
                      style={{
                        background: '#c9a94d',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '0px',
                        textDecoration: 'none'
                      }}
                    >
                      View on James Avery
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              )}
              <p className="body-small mt-6" style={{ color: '#999999' }}>
                Try checking back later or use the refresh button to search for new listings.
              </p>
            </div>
          </div>
        )}

        {/* Related Charms */}
        {relatedCharms.length > 0 && (
          <div>
            <h2 className="heading-2 mb-6">Related Charms</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {relatedCharms.map((relatedCharm) => (
                <button
                  key={relatedCharm.id}
                  onClick={() => navigate(`/charm/${relatedCharm.id}`)}
                  className="bg-white overflow-hidden transition-smooth hover:shadow-lg text-left"
                  style={{ border: 'none', borderRadius: '0px' }}
                >
                  <img
                    src={relatedCharm.images[0]}
                    alt={relatedCharm.name}
                    className="w-full h-48 object-cover"
                  />
                  <div className="p-4">
                    <h3 className="heading-3 mb-2">{relatedCharm.name}</h3>
                    <p className="text-lg font-semibold" style={{ color: '#333333' }}>
                      ${relatedCharm.avg_price.toFixed(2)}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};