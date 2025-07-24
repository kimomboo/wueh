import { useState, useEffect, useCallback } from "react";
import { useInView } from "react-intersection-observer";
import ListingCard from "./ListingCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle } from "lucide-react";
import { useListingStore } from "@/store/listingStore";

// Mock function to simulate API call
const fetchListings = async (page: number, limit: number = 12) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const mockListings = Array.from({ length: limit }, (_, index) => ({
    id: `listing-${page}-${index}`,
    title: `Amazing Product ${page * limit + index + 1}`,
    price: Math.floor(Math.random() * 500000) + 10000,
    images: ["/placeholder.svg"],
    location: ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"][Math.floor(Math.random() * 5)] + ", Kenya",
    timeAgo: ["2 hours ago", "5 hours ago", "1 day ago", "2 days ago"][Math.floor(Math.random() * 4)],
    seller: {
      id: `seller-${index}`,
      name: ["John Kamau", "Grace Wanjiku", "Peter Otieno", "Mary Njeri", "David Kipchoge"][Math.floor(Math.random() * 5)],
      phone: "+254712345678",
      rating: 4.5 + Math.random() * 0.5,
      verified: Math.random() > 0.3
    },
    isPremium: Math.random() > 0.7,
    isExpired: false,
    createdAt: new Date(),
    expiryDate: Math.random() > 0.5 ? new Date(Date.now() + Math.random() * 4 * 24 * 60 * 60 * 1000) : undefined,
    views: Math.floor(Math.random() * 1000),
    favorites: Math.floor(Math.random() * 50),
    status: 'active' as const,
    category: ["Electronics", "Vehicles", "Property", "Fashion", "Home"][Math.floor(Math.random() * 5)],
    condition: "Excellent",
    delivery: "Both Pickup & Delivery",
    description: "This is a great product in excellent condition.",
    currency: "KES"
  }));
  
  return {
    listings: mockListings,
    hasMore: page < 10, // Simulate 10 pages max
    totalCount: 120
  };
};

const InfiniteListings = () => {
  const [listings, setListings] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '100px',
  });

  const { getFilteredListings, toggleFavorite } = useListingStore();

  const loadMoreListings = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetchListings(page);
      
      setListings(prev => {
        // Randomize the order to simulate mixed categories
        const shuffled = [...prev, ...result.listings].sort(() => Math.random() - 0.5);
        return shuffled;
      });
      
      setHasMore(result.hasMore);
      setPage(prev => prev + 1);
    } catch (err) {
      setError('Failed to load listings. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [page, loading, hasMore]);

  // Load initial listings
  useEffect(() => {
    loadMoreListings();
  }, []); // Only run once on mount

  // Load more when scrolling to bottom
  useEffect(() => {
    if (inView && hasMore && !loading) {
      loadMoreListings();
    }
  }, [inView, hasMore, loading, loadMoreListings]);

  const handleFavorite = (listingId: string) => {
    toggleFavorite(listingId);
  };

  const handleContact = (listingId: string) => {
    console.log("Contacting seller for listing:", listingId);
    // Implement contact logic (WhatsApp, call, etc.)
  };

  const handleRetry = () => {
    setError(null);
    loadMoreListings();
  };

  return (
    <section className="py-12 bg-gradient-card">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-2">Latest Listings</h2>
          <p className="text-muted-foreground">
            Fresh items from verified sellers across Kenya • {listings.length} items loaded
          </p>
        </div>

        {/* Listings Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {listings.map((listing) => (
            <ListingCard
              key={listing.id}
              {...listing}
              onFavorite={() => handleFavorite(listing.id)}
              onContact={() => handleContact(listing.id)}
            />
          ))}
          
          {/* Loading Skeletons */}
          {loading && Array.from({ length: 8 }).map((_, index) => (
            <div key={`skeleton-${index}`} className="space-y-4">
              <Skeleton className="aspect-[4/3] w-full rounded-lg" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-1/4" />
                  <Skeleton className="h-4 w-1/4" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Error State */}
        {error && (
          <div className="text-center mt-8">
            <div className="inline-flex items-center gap-2 text-destructive mb-4">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
            <div>
              <Button onClick={handleRetry} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        )}

        {/* Load More Trigger */}
        {hasMore && !loading && !error && (
          <div ref={ref} className="text-center mt-8">
            <div className="text-muted-foreground">
              Scroll down to load more listings...
            </div>
          </div>
        )}

        {/* End of Results */}
        {!hasMore && !loading && listings.length > 0 && (
          <div className="text-center mt-12 py-8 border-t border-border">
            <h3 className="text-lg font-semibold mb-2">🎉 You've seen it all!</h3>
            <p className="text-muted-foreground mb-4">
              You've browsed through all available listings. Check back later for new items!
            </p>
            <Button 
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              variant="outline"
            >
              Back to Top
            </Button>
          </div>
        )}
      </div>
    </section>
  );
};

export default InfiniteListings;