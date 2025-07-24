import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  User, 
  Settings, 
  Heart, 
  Plus, 
  Crown, 
  BarChart3,
  Calendar,
  MapPin,
  Phone,
  Mail,
  Edit,
  Trash2
} from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import ListingCard from "@/components/ListingCard";

// Mock user data
const mockUser = {
  id: "user-1",
  name: "John Kamau",
  email: "john.kamau@email.com",
  phone: "+254712345678",
  location: "Nairobi, Kenya",
  avatar: "/placeholder.svg",
  joinDate: "January 2024",
  verified: true,
  rating: 4.8,
  totalListings: 8,
  activeListings: 5,
  freeAdsUsed: 2,
  premiumListings: 3
};

// Mock user listings with countdown data
const mockUserListings = [
  {
    id: "1",
    title: "iPhone 14 Pro Max - Excellent Condition",
    price: 120000,
    images: ["/placeholder.svg"],
    location: "Nairobi, Kenya",
    timeAgo: "2 hours ago",
    seller: mockUser,
    isPremium: true,
    isOwner: true,
    status: "active"
  },
  {
    id: "2", 
    title: "Toyota Fielder 2018 - Well Maintained",
    price: 1850000,
    images: ["/placeholder.svg"],
    location: "Mombasa, Kenya",
    timeAgo: "5 hours ago",
    seller: mockUser,
    isPremium: false,
    expiryDate: new Date(Date.now() + 1.5 * 24 * 60 * 60 * 1000), // 1.5 days from now
    daysLeft: 1,
    isOwner: true,
    status: "expires_soon"
  },
  {
    id: "3",
    title: "MacBook Air M2 - Like New",
    price: 185000,
    images: ["/placeholder.svg"],
    location: "Nakuru, Kenya",
    timeAgo: "1 day ago",
    seller: mockUser,
    isPremium: false,
    expiryDate: new Date(Date.now() + 12 * 60 * 60 * 1000), // 12 hours from now
    daysLeft: 0,
    isOwner: true,
    status: "critical"
  },
  {
    id: "4",
    title: "Samsung Galaxy S23 Ultra",
    price: 95000,
    images: ["/placeholder.svg"],
    location: "Nairobi, Kenya",
    timeAgo: "3 days ago",
    seller: mockUser,
    isPremium: false,
    isExpired: true,
    isOwner: true,
    status: "expired"
  },
  {
    id: "5",
    title: "Honda CBR 600RR Motorcycle",
    price: 980000,
    images: ["/placeholder.svg"],
    location: "Kisumu, Kenya",
    timeAgo: "2 days ago",
    seller: mockUser,
    isPremium: true,
    isOwner: true,
    status: "active"
  }
];

const Profile = () => {
  const [activeTab, setActiveTab] = useState("listings");

  const getListingsByStatus = (status: string) => {
    switch (status) {
      case "active":
        return mockUserListings.filter(listing => !listing.isExpired && (listing.isPremium || (listing.daysLeft && listing.daysLeft > 0)));
      case "expires_soon":
        return mockUserListings.filter(listing => !listing.isPremium && listing.daysLeft !== undefined && listing.daysLeft <= 1 && !listing.isExpired);
      case "expired":
        return mockUserListings.filter(listing => listing.isExpired);
      default:
        return mockUserListings;
    }
  };

  const handleEditListing = (id: string) => {
    console.log("Edit listing:", id);
    // Navigate to edit form
  };

  const handleDeleteListing = (id: string) => {
    console.log("Delete listing:", id);
    // Show confirmation dialog
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Profile Header */}
          <Card className="mb-8">
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex flex-col items-center md:items-start">
                  <Avatar className="w-24 h-24 mb-4">
                    <AvatarImage src={mockUser.avatar} alt={mockUser.name} />
                    <AvatarFallback className="text-xl">{mockUser.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  {mockUser.verified && (
                    <Badge variant="outline" className="bg-success/10 text-success border-success/30">
                      <Crown className="h-3 w-3 mr-1" />
                      Verified User
                    </Badge>
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex flex-col md:flex-row justify-between items-start mb-4">
                    <div>
                      <h1 className="text-3xl font-bold mb-2">{mockUser.name}</h1>
                      <div className="space-y-1 text-muted-foreground">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          <span>{mockUser.email}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4" />
                          <span>{mockUser.phone}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4" />
                          <span>{mockUser.location}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          <span>Joined {mockUser.joinDate}</span>
                        </div>
                      </div>
                    </div>
                    
                    <Button variant="outline" className="mt-4 md:mt-0">
                      <Settings className="h-4 w-4 mr-2" />
                      Edit Profile
                    </Button>
                  </div>
                  
                  {/* Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">{mockUser.totalListings}</div>
                      <div className="text-sm text-muted-foreground">Total Listings</div>
                    </div>
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{mockUser.activeListings}</div>
                      <div className="text-sm text-muted-foreground">Active</div>
                    </div>
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <div className="text-2xl font-bold text-secondary">{mockUser.premiumListings}</div>
                      <div className="text-sm text-muted-foreground">Premium</div>
                    </div>
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <div className="text-2xl font-bold text-warning">{mockUser.freeAdsUsed}/3</div>
                      <div className="text-sm text-muted-foreground">Free Ads Used</div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Account Status Warning */}
          {mockUser.freeAdsUsed >= 3 && (
            <Card className="mb-6 border-warning/30 bg-warning/5">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <Crown className="h-5 w-5 text-warning mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-warning mb-2">Free Ad Limit Reached</h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      You've used all 3 free ads. All future listings must be Premium to maintain visibility.
                    </p>
                    <Button variant="warning" size="sm" asChild>
                      <Link to="/premium">Upgrade to Premium</Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="listings" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                My Listings
              </TabsTrigger>
              <TabsTrigger value="favorites" className="flex items-center gap-2">
                <Heart className="h-4 w-4" />
                Favorites
              </TabsTrigger>
              <TabsTrigger value="expired" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Expired
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Settings
              </TabsTrigger>
            </TabsList>

            {/* My Listings Tab */}
            <TabsContent value="listings" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">My Listings</h2>
                <Button asChild>
                  <Link to="/create-listing">
                    <Plus className="h-4 w-4 mr-2" />
                    Create New Listing
                  </Link>
                </Button>
              </div>

              {/* Active Listings */}
              <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  Active Listings
                  <Badge>{getListingsByStatus("active").length}</Badge>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {getListingsByStatus("active").map((listing) => (
                    <div key={listing.id} className="relative">
                      <ListingCard
                        {...listing}
                        onFavorite={() => {}}
                        onContact={() => {}}
                      />
                      {/* Owner Actions */}
                      <div className="absolute top-2 left-2 flex gap-1">
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 bg-white/90"
                          onClick={() => handleEditListing(listing.id)}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 bg-white/90 hover:bg-destructive hover:text-destructive-foreground"
                          onClick={() => handleDeleteListing(listing.id)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expiring Soon */}
              {getListingsByStatus("expires_soon").length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-warning">
                    Expiring Soon
                    <Badge variant="warning">{getListingsByStatus("expires_soon").length}</Badge>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {getListingsByStatus("expires_soon").map((listing) => (
                      <div key={listing.id} className="relative">
                        <ListingCard
                          {...listing}
                          onFavorite={() => {}}
                          onContact={() => {}}
                        />
                        {/* Owner Actions */}
                        <div className="absolute top-2 left-2 flex gap-1">
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8 bg-white/90"
                            onClick={() => handleEditListing(listing.id)}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8 bg-white/90 hover:bg-destructive hover:text-destructive-foreground"
                            onClick={() => handleDeleteListing(listing.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>

            {/* Favorites Tab */}
            <TabsContent value="favorites">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Heart className="h-5 w-5" />
                    Your Favorites
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-center py-8">
                    You haven't favorited any listings yet. Browse the marketplace to find items you like!
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Expired Tab */}
            <TabsContent value="expired">
              <div>
                <h2 className="text-2xl font-bold mb-6">Expired Listings</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {getListingsByStatus("expired").map((listing) => (
                    <div key={listing.id} className="relative">
                      <ListingCard
                        {...listing}
                        onFavorite={() => {}}
                        onContact={() => {}}
                      />
                      <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                        <div className="text-center text-white">
                          <h4 className="font-semibold mb-2">Listing Expired</h4>
                          <Button variant="secondary" size="sm" asChild>
                            <Link to={`/premium?listing=${listing.id}`}>
                              Renew with Premium
                            </Link>
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            {/* Settings Tab */}
            <TabsContent value="settings">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Account Settings
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-center py-8">
                    Account settings panel will be implemented with profile editing,
                    notification preferences, and security options.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Profile;