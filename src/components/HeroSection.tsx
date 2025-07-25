import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Search,
  TrendingUp,
  Users,
  MapPin,
  CheckCircle,
  Zap,
  Crown,
  ArrowRight,
  Star,
  Shield,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import HotDealsCarousel from "./HotDealsCarousel";
import CategoryGrid from "./CategoryGrid";

const HeroSection = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const stats = [
    { label: "Active Users", value: "50K+", icon: Users, color: "text-blue-600" },
    { label: "Live Listings", value: "25K+", icon: TrendingUp, color: "text-green-600" },
    { label: "Counties Covered", value: "47", icon: MapPin, color: "text-purple-600" },
    { label: "Success Rate", value: "94%", icon: CheckCircle, color: "text-emerald-600" },
  ];

  const features = [
    {
      icon: Shield,
      title: "Verified Sellers",
      description: "All sellers are verified with phone and ID verification",
    },
    {
      icon: Zap,
      title: "Instant Connect",
      description: "Direct WhatsApp and phone contact with sellers",
    },
    {
      icon: Crown,
      title: "Premium Listings",
      description: "Boost your ads for maximum visibility and faster sales",
    },
  ];

  return (
    <div className="relative">
      {/* Main Hero Section */}
      <section className="relative bg-gradient-hero text-white overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-black/20"></div>
        <div
          className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-30"
        ></div>

        <div className="relative container mx-auto px-4 py-20 lg:py-32">
          <div className="max-w-4xl mx-auto text-center">
            {/* Main Headline */}
            <div className="mb-8">
              <Badge className="bg-white/10 text-white border-white/20 mb-4">
                🇰🇪 Kenya's #1 Marketplace
              </Badge>
              <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                Buy, Sell & Connect
                <span className="block bg-gradient-to-r from-secondary to-white bg-clip-text text-transparent">
                  Across Kenya
                </span>
              </h1>
              <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-2xl mx-auto">
                Join thousands of Kenyans buying and selling everything from electronics to vehicles.
                Safe, fast, and trusted.
              </p>
            </div>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto mb-12">
              <form onSubmit={handleSearch} className="relative">
                <div className="relative">
                  <Input
                    type="text"
                    placeholder="Search for anything in Kenya... (phones, cars, houses)"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="h-14 pl-14 pr-32 text-lg bg-white/95 backdrop-blur-sm border-white/20 text-foreground placeholder:text-muted-foreground"
                  />
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-6 w-6 text-muted-foreground" />
                  <Button
                    type="submit"
                    size="lg"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary hover:bg-primary/90"
                  >
                    Search
                  </Button>
                </div>
              </form>
              <div className="flex flex-wrap justify-center gap-2 mt-4">
                {["iPhone", "Toyota", "Apartment", "Laptop", "Motorcycle"].map((term) => (
                  <Button
                    key={term}
                    variant="ghost"
                    size="sm"
                    className="text-white/80 hover:text-white hover:bg-white/10"
                    onClick={() => {
                      setSearchQuery(term);
                      navigate(`/search?q=${encodeURIComponent(term)}`);
                    }}
                  >
                    {term}
                  </Button>
                ))}
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Button size="xl" variant="secondary" asChild>
                <Link to="/create-listing">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Start Selling Today
                </Link>
              </Button>
              <Button
                size="xl"
                variant="outline"
                className="border-white/30 text-white hover:bg-white/10"
                asChild
              >
                <Link to="/auth">
                  <Users className="h-5 w-5 mr-2" />
                  Join Community
                </Link>
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="flex justify-center mb-2">
                    <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center">
                      <stat.icon className={`h-6 w-6 ${stat.color}`} />
                    </div>
                  </div>
                  <div className="text-2xl md:text-3xl font-bold mb-1">{stat.value}</div>
                  <div className="text-white/80 text-sm">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose PeerStorm?</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              We've built the most trusted and efficient marketplace in Kenya,
              connecting buyers and sellers with cutting-edge features.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="text-center hover:shadow-elegant transition-all duration-300 border-2 hover:border-primary/20"
              >
                <CardContent className="p-8">
                  <div className="w-16 h-16 bg-gradient-primary rounded-lg flex items-center justify-center mx-auto mb-4">
                    <feature.icon className="h-8 w-8 text-primary-foreground" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Hot Deals Section */}
      <HotDealsCarousel />

      {/* Categories Section */}
      <CategoryGrid />

      {/* Call to Action Section */}
      <section className="py-16 bg-gradient-primary text-primary-foreground">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Start Your Journey?</h2>
            <p className="text-xl text-primary-foreground/90 mb-8">
              Join thousands of successful sellers and buyers on Kenya's most trusted marketplace.
              List your first item in under 2 minutes!
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="xl" variant="secondary" asChild>
                <Link to="/create-listing">
                  <Crown className="h-5 w-5 mr-2" />
                  List Your First Item
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Link>
              </Button>
              <Button
                size="xl"
                variant="outline"
                className="border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10"
                asChild
              >
                <Link to="/premium">
                  <Star className="h-5 w-5 mr-2" />
                  View Premium Plans
                </Link>
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="mt-12 pt-8 border-t border-primary-foreground/20">
              <div className="flex flex-wrap justify-center items-center gap-8 text-primary-foreground/80">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  <span>Secure Payments</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  <span>Verified Sellers</span>
                </div>
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5" />
                  <span>4.8/5 Rating</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  <span>50K+ Happy Users</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HeroSection;
