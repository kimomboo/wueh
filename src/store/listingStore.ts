import { create } from 'zustand';

export interface Listing {
  id: string;
  title: string;
  description: string;
  price: number;
  currency: string;
  images: string[];
  category: string;
  condition: string;
  location: string;
  delivery: string;
  seller: {
    id: string;
    name: string;
    phone: string;
    rating: number;
    verified: boolean;
  };
  isPremium: boolean;
  isExpired: boolean;
  createdAt: Date;
  expiryDate?: Date;
  views: number;
  favorites: number;
  status: 'active' | 'expired' | 'sold' | 'draft';
}

interface ListingState {
  listings: Listing[];
  favorites: string[];
  searchQuery: string;
  selectedCategory: string;
  priceRange: [number, number];
  selectedLocation: string;
  isLoading: boolean;
  
  // Actions
  setListings: (listings: Listing[]) => void;
  addListing: (listing: Listing) => void;
  updateListing: (id: string, updates: Partial<Listing>) => void;
  deleteListing: (id: string) => void;
  toggleFavorite: (listingId: string) => void;
  setSearchQuery: (query: string) => void;
  setSelectedCategory: (category: string) => void;
  setPriceRange: (range: [number, number]) => void;
  setSelectedLocation: (location: string) => void;
  setLoading: (loading: boolean) => void;
  
  // Computed
  getFilteredListings: () => Listing[];
  getFavoriteListings: () => Listing[];
  getUserListings: (userId: string) => Listing[];
}

export const useListingStore = create<ListingState>((set, get) => ({
  listings: [],
  favorites: [],
  searchQuery: '',
  selectedCategory: '',
  priceRange: [0, 10000000],
  selectedLocation: '',
  isLoading: false,

  setListings: (listings) => set({ listings }),
  
  addListing: (listing) => set((state) => ({ 
    listings: [listing, ...state.listings] 
  })),
  
  updateListing: (id, updates) => set((state) => ({
    listings: state.listings.map(listing => 
      listing.id === id ? { ...listing, ...updates } : listing
    )
  })),
  
  deleteListing: (id) => set((state) => ({
    listings: state.listings.filter(listing => listing.id !== id)
  })),
  
  toggleFavorite: (listingId) => set((state) => ({
    favorites: state.favorites.includes(listingId)
      ? state.favorites.filter(id => id !== listingId)
      : [...state.favorites, listingId]
  })),
  
  setSearchQuery: (query) => set({ searchQuery: query }),
  setSelectedCategory: (category) => set({ selectedCategory: category }),
  setPriceRange: (range) => set({ priceRange: range }),
  setSelectedLocation: (location) => set({ selectedLocation: location }),
  setLoading: (loading) => set({ isLoading: loading }),
  
  getFilteredListings: () => {
    const { listings, searchQuery, selectedCategory, priceRange, selectedLocation } = get();
    
    return listings.filter(listing => {
      const matchesSearch = !searchQuery || 
        listing.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        listing.description.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesCategory = !selectedCategory || listing.category === selectedCategory;
      const matchesPrice = listing.price >= priceRange[0] && listing.price <= priceRange[1];
      const matchesLocation = !selectedLocation || listing.location === selectedLocation;
      
      return matchesSearch && matchesCategory && matchesPrice && matchesLocation;
    });
  },
  
  getFavoriteListings: () => {
    const { listings, favorites } = get();
    return listings.filter(listing => favorites.includes(listing.id));
  },
  
  getUserListings: (userId) => {
    const { listings } = get();
    return listings.filter(listing => listing.seller.id === userId);
  },
}));