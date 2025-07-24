import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Crown, Heart, MapPin, Star, ChevronLeft, ChevronRight } from "lucide-react";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";

// Mock hot deals data
const hotDeals = [
  {
    id: "hot-1",
    title: "iPhone 15 Pro Max - Brand New",
    price: 180000,
    originalPrice: 220000,
    discount: 18,
    images: ["/placeholder.svg"],
    location: "Nairobi, Kenya",
    seller: { name: "TechHub Kenya", rating: 4.9, verified: true },
    timeLeft: "2 days left",
    views: 1250,
    category: "Electronics"
  },
  {
    id: "hot-2", 
    title: "Toyota Prado 2020 - Excellent Condition",
    price: 4500000,
    originalPrice: 5200000,
    discount: 13,
    images: ["/placeholder.svg"],
    location: "Mombasa, Kenya",
    seller: { name: "AutoDeals Kenya", rating: 4.8, verified: true },
    timeLeft: "5 days left",
    views: 890,
    category: "Vehicles"
  },
  {
    id: "hot-3",
    title: "3BR Apartment - Kilimani",
    price: 85000,
    originalPrice: 95000,
    discount: 11,
    images: ["/placeholder.svg"],
    location: "Nairobi, Kenya",
    seller: { name: "Prime Properties", rating: 4.7, verified: true },
    timeLeft: "1 day left",
    views: 2100,
    category: "Property"
  },
  {
    id: "hot-4",
    title: "MacBook Pro M3 - Like New",
    price: 220000,
    originalPrice: 280000,
    discount: 21,
    images: ["/placeholder.svg"],
    location: "Nakuru, Kenya",
    seller: { name: "Digital Solutions", rating: 4.9, verified: true },
    timeLeft: "3 days left",
    views: 670,
    category: "Electronics"
  },
  {
    id: "hot-5",
    title: "Honda CBR 1000RR - 2022",
    price: 1200000,
    originalPrice: 1400000,
    discount: 14,
    images: ["/placeholder.svg"],
    location: "Kisumu, Kenya",
    seller: { name: "Moto Kenya", rating: 4.6, verified: true },
    timeLeft: "4 days left",
    views: 445,
    category: "Vehicles"
  }
];

const HotDealsCarousel = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [favorites, setFavorites] = useState<string[]>([]);

  // Auto-scroll functionality
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % hotDeals.length);
    }, 5000); // Change slide every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const toggleFavorite = (dealId: string) => {
    setFavorites(prev => 
      prev.includes(dealId) 
        ? prev.filter(id => id !== dealId)
        : [...prev, dealId]
    );
  };

  return (
    <section className="py-12 bg-gradient-to-r from-secondary/10 to-primary/10">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-secondary/20 rounded-full px-4 py-2 mb-4">
            <Crown className="h-4 w-4 text-secondary" />
            <span className="text-sm font-medium text-secondary">Hot Deals</span>
          </div>
          <h2 className="text-3xl font-bold mb-2">🔥 Limited Time Offers</h2>
          <p className="text-muted-foreground">Premium deals with amazing discounts - don't miss out!</p>
        </div>

        <Carousel className="w-full max-w-6xl mx-auto">
          <CarouselContent>
            {hotDeals.map((deal) => (
              <CarouselItem key={deal.id} className="md:basis-1/2 lg:basis-1/3">
                <Card className="group overflow-hidden hover:shadow-premium transition-all duration-300 border-2 border-secondary/20">
                  <div className="relative">
                    {/* Deal Image */}
                    <div className="aspect-[4/3] overflow-hidden bg-muted">
                      <img 
                        src={deal.images[0]} 
                        alt={deal.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                    
                    {/* Badges */}
                    <div className="absolute top-2 left-2 flex gap-2">
                      <Badge className="bg-secondary text-secondary-foreground">
                        -{deal.discount}% OFF
                      </Badge>
                      <Badge variant="outline" className="bg-white/90">
                        Hot Deal 🔥
                      </Badge>
                    </div>

                    {/* Favorite Button */}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 bg-white/80 hover:bg-white/90"
                      onClick={() => toggleFavorite(deal.id)}
                    >
                      <Heart 
                        className={`h-4 w-4 ${
                          favorites.includes(deal.id) 
                            ? 'fill-red-500 text-red-500' 
                            : 'text-muted-foreground'
                        }`} 
                      />
                    </Button>

                    {/* Time Left */}
                    <div className="absolute bottom-2 left-2">
                      <Badge variant="destructive" className="animate-pulse">
                        ⏰ {deal.timeLeft}
                      </Badge>
                    </div>
                  </div>

                  <CardContent className="p-4">
                    {/* Pricing */}
                    <div className="flex items-center gap-2 mb-2">
                      <div className="text-xl font-bold text-primary">
                        {formatPrice(deal.price)}
                      </div>
                      <div className="text-sm text-muted-foreground line-through">
                        {formatPrice(deal.originalPrice)}
                      </div>
                    </div>

                    {/* Title */}
                    <h3 className="font-semibold text-foreground line-clamp-2 mb-2 group-hover:text-primary transition-colors">
                      {deal.title}
                    </h3>

                    {/* Location & Views */}
                    <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        <span>{deal.location}</span>
                      </div>
                      <span>{deal.views.toLocaleString()} views</span>
                    </div>

                    {/* Seller Info */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium">
                          {deal.seller.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="text-sm font-medium flex items-center gap-1">
                            {deal.seller.name}
                            {deal.seller.verified && (
                              <Badge variant="outline" className="text-xs bg-success/10 text-success border-success/30 px-1 py-0">
                                ✓
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-1">
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            <span className="text-xs text-muted-foreground">{deal.seller.rating}</span>
                          </div>
                        </div>
                      </div>

                      <Button size="sm" className="bg-secondary hover:bg-secondary/90">
                        View Deal
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious className="left-4" />
          <CarouselNext className="right-4" />
        </Carousel>

        {/* Carousel Indicators */}
        <div className="flex justify-center mt-6 gap-2">
          {hotDeals.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentIndex % hotDeals.length
                  ? 'bg-secondary w-6'
                  : 'bg-muted-foreground/30'
              }`}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default HotDealsCarousel;