import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import SearchFilters from "./SearchFilters";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Search, 
  Plus, 
  Heart, 
  User, 
  Bell, 
  Menu,
  ShoppingBag,
  MapPin,
  Filter
} from "lucide-react";

const Navbar = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const { isAuthenticated, user } = useAuthStore();
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-md border-b border-border shadow-elegant">
      <div className="container mx-auto px-4">
        {/* Top Bar */}
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
              <ShoppingBag className="h-6 w-6 text-primary-foreground" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                PeerStorm
              </h1>
              <p className="text-xs text-muted-foreground -mt-1">Nexus Arena</p>
            </div>
          </Link>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl mx-4">
            <form onSubmit={handleSearch} className="relative">
              <Input
                type="text"
                placeholder="Search for anything in Kenya..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-24 h-11 bg-muted/50 border-border/50 focus:bg-background"
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Button 
                type="submit"
                size="sm" 
                className="absolute right-1 top-1/2 transform -translate-y-1/2"
              >
                Search
              </Button>
            </form>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <Button variant="hero" size="lg" asChild className="hidden sm:flex">
              <Link to="/create-listing">
                <Plus className="h-4 w-4" />
                List Item
              </Link>
            </Button>

            {/* User Actions */}
            <div className="flex items-center space-x-1">
              <Button variant="ghost" size="icon" asChild>
                <Link to="/favorites">
                  <Heart className="h-5 w-5" />
                </Link>
              </Button>
              
              {isAuthenticated && (
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="h-5 w-5" />
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs bg-secondary">
                    3
                  </Badge>
                </Button>
              )}

              {isAuthenticated ? (
                <Button variant="ghost" size="icon" asChild>
                  <Link to="/dashboard">
                    <User className="h-5 w-5" />
                  </Link>
                </Button>
              ) : (
                <Button variant="outline" asChild>
                  <Link to="/auth">Sign In</Link>
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Secondary Navigation */}
        <div className="hidden md:flex items-center justify-between py-2 border-t border-border/50">
          <div className="flex items-center space-x-6">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/categories">All Categories</Link>
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/electronics">Electronics</Link>
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/vehicles">Vehicles</Link>
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/property">Property</Link>
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/fashion">Fashion</Link>
            </Button>
          </div>

          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4" />
            <span>{user?.location || "Kenya"}</span>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setShowFilters(true)}
            >
              <Filter className="h-4 w-4" />
              Filter
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Button */}
      <div className="md:hidden px-4 pb-2">
        <Button variant="outline" size="sm" className="w-full">
          <Menu className="h-4 w-4 mr-2" />
          Browse Categories
        </Button>
      </div>
      
      <SearchFilters 
        isOpen={showFilters} 
        onClose={() => setShowFilters(false)} 
      />
    </nav>
  );
};

export default Navbar;