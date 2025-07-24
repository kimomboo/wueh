import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
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
  Trash2,
  TrendingUp,
  Clock,
  DollarSign,
  Eye
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useListingStore } from "@/store/listingStore";

const UserDashboard = () => {
  const { user } = useAuthStore();
  const { getUserListings } = useListingStore();
  const [activeTab, setActiveTab] = useState("overview");

  if (!user) return null;

  const userListings = getUserListings(user.id);
  const activeListings = userListings.filter(l => l.status === 'active');
  const expiredListings = userListings.filter(l => l.status === 'expired');
  const premiumListings = userListings.filter(l => l.isPremium);

  const totalViews = userListings.reduce((sum, listing) => sum + listing.views, 0);
  const totalFavorites = userListings.reduce((sum, listing) => sum + listing.favorites, 0);

  const freeAdsProgress = (user.freeAdsUsed / 3) * 100;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Dashboard Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user.fullName}! Here's your marketplace overview.
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="listings">My Listings</TabsTrigger>
            <TabsTrigger value="favorites">Favorites</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Listings</p>
                      <p className="text-2xl font-bold">{userListings.length}</p>
                    </div>
                    <BarChart3 className="h-8 w-8 text-primary" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Active Ads</p>
                      <p className="text-2xl font-bold text-green-600">{activeListings.length}</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Views</p>
                      <p className="text-2xl font-bold">{totalViews.toLocaleString()}</p>
                    </div>
                    <Eye className="h-8 w-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Favorites</p>
                      <p className="text-2xl font-bold">{totalFavorites}</p>
                    </div>
                    <Heart className="h-8 w-8 text-red-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Free Ads Usage */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Free Ads Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Used {user.freeAdsUsed} of 3 free ads
                    </span>
                    <Badge variant={user.freeAdsUsed >= 3 ? "destructive" : "secondary"}>
                      {3 - user.freeAdsUsed} remaining
                    </Badge>
                  </div>
                  <Progress value={freeAdsProgress} className="w-full" />
                  {user.freeAdsUsed >= 3 && (
                    <div className="p-4 bg-warning/10 border border-warning/30 rounded-lg">
                      <p className="text-sm text-warning font-medium">
                        ⚠️ Free ad limit reached! All future listings must be Premium.
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {userListings.slice(0, 5).map((listing) => (
                    <div key={listing.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <img 
                          src={listing.images[0]} 
                          alt={listing.title}
                          className="w-12 h-12 rounded-lg object-cover"
                        />
                        <div>
                          <p className="font-medium line-clamp-1">{listing.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {listing.views} views • {listing.favorites} favorites
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">
                          KES {listing.price.toLocaleString()}
                        </p>
                        <Badge variant={listing.isPremium ? "default" : "outline"}>
                          {listing.isPremium ? "Premium" : "Free"}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Listings Tab */}
          <TabsContent value="listings" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">My Listings</h2>
              <Button asChild>
                <a href="/create-listing">
                  <Plus className="h-4 w-4 mr-2" />
                  Create New Listing
                </a>
              </Button>
            </div>

            {/* Listings Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {userListings.map((listing) => (
                <Card key={listing.id} className="overflow-hidden">
                  <div className="relative">
                    <img 
                      src={listing.images[0]} 
                      alt={listing.title}
                      className="w-full h-48 object-cover"
                    />
                    <div className="absolute top-2 left-2 flex gap-2">
                      {listing.isPremium && (
                        <Badge className="bg-secondary">Premium</Badge>
                      )}
                      <Badge variant={listing.status === 'active' ? 'default' : 'destructive'}>
                        {listing.status}
                      </Badge>
                    </div>
                    <div className="absolute top-2 right-2 flex gap-1">
                      <Button variant="outline" size="icon" className="h-8 w-8 bg-white/90">
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button variant="outline" size="icon" className="h-8 w-8 bg-white/90 hover:bg-destructive hover:text-destructive-foreground">
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <h3 className="font-semibold line-clamp-2 mb-2">{listing.title}</h3>
                    <p className="text-lg font-bold text-primary mb-2">
                      KES {listing.price.toLocaleString()}
                    </p>
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>{listing.views} views</span>
                      <span>{listing.favorites} favorites</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Other tabs would be implemented similarly */}
          <TabsContent value="favorites">
            <Card>
              <CardHeader>
                <CardTitle>Your Favorites</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Your favorite listings will appear here.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>Analytics & Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Detailed analytics coming soon.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Account settings panel coming soon.</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default UserDashboard;