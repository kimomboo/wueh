import { useState, useEffect } from "react";
import ListingCard from "./ListingCard";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

// Mock data for demonstration
const mockListings = [
  {
    id: "1",
    title: "iPhone 14 Pro Max - Excellent Condition",
    price: 120000,
    images: ["/placeholder.svg"],
    location: "Nairobi, Kenya",
    timeAgo: "2 hours ago",
    seller: { name: "John Kamau", rating: 4.8, verified: true },
    isPremium: true,
    expiryDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // 2 days from now
    daysLeft: 2,
    isOwner: false
  },
  {
    id: "2", 
    title: "Toyota Fielder 2018 - Well Maintained",
    price: 1850000,
    images: ["/placeholder.svg"],
    location: "Mombasa, Kenya",
    timeAgo: "5 hours ago",
    seller: { name: "Grace Wanjiku", rating: 4.9, verified: true },
    isPremium: false,
    expiryDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000), // 1 day from now
    daysLeft: 1,
    isOwner: true // This user owns this listing
  },
  {
    id: "3",
    title: "3 Bedroom Apartment for Rent",
    price: 45000,
    images: ["/placeholder.svg"],
    location: "Kiambu, Kenya", 
    timeAgo: "1 day ago",
    seller: { name: "Peter Otieno", rating: 4.6, verified: false },
    isPremium: true,
    isOwner: false
  },
  {
    id: "4",
    title: "MacBook Air M2 - Like New",
    price: 185000,
    images: ["/placeholder.svg"],
    location: "Nakuru, Kenya",
    timeAgo: "3 hours ago",
    seller: { name: "Mary Njeri", rating: 4.7, verified: true },
    isPremium: false,
    expiryDate: new Date(Date.now() + 18 * 60 * 60 * 1000), // 18 hours from now
    daysLeft: 0,
    isOwner: true // Critical - expires in 18 hours
  },
  {
    id: "5",
    title: "Samsung 55\" Smart TV",
    price: 75000,
    images: ["/placeholder.svg"],
    location: "Eldoret, Kenya",
    timeAgo: "6 hours ago",
    seller: { name: "David Kipchoge", rating: 4.5, verified: true },
    isPremium: false,
    expiryDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), // 3 days from now
    daysLeft: 3,
    isOwner: false
  },
  {
    id: "6",
    title: "Honda CBR 600RR Motorcycle",
    price: 980000,
    images: ["/placeholder.svg"],
    location: "Kisumu, Kenya",
    timeAgo: "4 hours ago", 
    seller: { name: "James Ochieng", rating: 4.8, verified: true },
    isPremium: true,
    isOwner: false
  }
];

const RecentListings = () => {
  const [listings, setListings] = useState(mockListings);
  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      // Randomize the order to simulate new listings
      const shuffled = [...mockListings].sort(() => 0.5 - Math.random());
      setListings(shuffled);
      setLoading(false);
    }, 1000);
  };

  const handleFavorite = (id: string) => {
    console.log("Favoriting listing:", id);
    // Implement favorite logic
  };

  const handleContact = (id: string) => {
    console.log("Contacting seller for listing:", id);
    // Implement contact logic
  };

  return (
    <section className="py-12 bg-gradient-card">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-foreground mb-2">
              Recently Listed
            </h2>
            <p className="text-muted-foreground">
              Fresh items from verified sellers across Kenya
            </p>
          </div>
          
          <Button 
            variant="outline" 
            onClick={handleRefresh}
            disabled={loading}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
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
        </div>

        {/* Load More */}
        <div className="text-center mt-12">
          <Button size="lg" variant="outline" className="min-w-[200px]">
            Load More Listings
          </Button>
        </div>
      </div>
    </section>
  );
};

export default RecentListings;