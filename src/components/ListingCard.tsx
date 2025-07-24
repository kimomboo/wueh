import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Heart, 
  MapPin, 
  Phone, 
  MessageCircle, 
  Clock, 
  Star,
  Crown
} from "lucide-react";
import CountdownTimer from "./CountdownTimer";
import ListingUpgradePrompt from "./ListingUpgradePrompt";

interface ListingCardProps {
  id: string;
  title: string;
  price: number;
  images: string[];
  location: string;
  timeAgo: string;
  seller: {
    name: string;
    rating: number;
    verified: boolean;
  };
  isPremium?: boolean;
  isExpired?: boolean;
  daysLeft?: number;
  expiryDate?: Date;
  isOwner?: boolean;
  onFavorite?: () => void;
  onContact?: () => void;
}

const ListingCard = ({ 
  id, 
  title, 
  price, 
  images, 
  location, 
  timeAgo, 
  seller, 
  isPremium = false,
  isExpired = false,
  daysLeft,
  expiryDate,
  isOwner = false,
  onFavorite,
  onContact 
}: ListingCardProps) => {
  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <Card className={`group overflow-hidden hover:shadow-elegant transition-all duration-300 ${
      isPremium ? 'ring-2 ring-secondary/30 shadow-premium' : ''
    } ${isExpired ? 'opacity-60' : ''}`}>
      <div className="relative">
        {/* Image */}
        <div className="aspect-[4/3] overflow-hidden bg-muted">
          <img 
            src={images[0] || "/placeholder.svg"} 
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        
        {/* Badges */}
        <div className="absolute top-2 left-2 flex gap-2">
          {isPremium && (
            <Badge className="bg-secondary text-secondary-foreground border-secondary/30">
              <Crown className="h-3 w-3 mr-1" />
              Premium
            </Badge>
          )}
          {isExpired && (
            <Badge variant="destructive">
              Expired
            </Badge>
          )}
        </div>

        {/* Countdown Timer (for owner) */}
        {isOwner && expiryDate && !isPremium && (
          <div className="absolute top-2 right-12">
            <CountdownTimer 
              expiryDate={expiryDate} 
              isPremium={isPremium}
              className="bg-background/90 text-foreground"
            />
          </div>
        )}

        {/* Favorite Button */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 bg-white/80 hover:bg-white/90"
          onClick={onFavorite}
        >
          <Heart className="h-4 w-4" />
        </Button>
      </div>

      <CardContent className="p-4">
        {/* Price */}
        <div className="flex items-center justify-between mb-2">
          <div className="text-xl font-bold text-primary">
            {formatPrice(price)}
          </div>
          {seller.verified && (
            <Badge variant="outline" className="text-xs bg-success/10 text-success border-success/30">
              <Star className="h-3 w-3 mr-1" />
              Verified
            </Badge>
          )}
        </div>

        {/* Title */}
        <h3 className="font-semibold text-foreground line-clamp-2 mb-2 group-hover:text-primary transition-colors">
          {title}
        </h3>

        {/* Location & Time */}
        <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
          <div className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            <span>{location}</span>
          </div>
          <span>{timeAgo}</span>
        </div>

        {/* Seller Info */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium">
              {seller.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-sm font-medium">{seller.name}</div>
              <div className="flex items-center gap-1">
                <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                <span className="text-xs text-muted-foreground">{seller.rating.toFixed(1)}</span>
              </div>
            </div>
          </div>

          {/* Contact Buttons */}
          <div className="flex gap-1">
            <Button 
              variant="outline" 
              size="sm"
              onClick={onContact}
              className="h-8 w-8 p-0"
            >
              <Phone className="h-3 w-3" />
            </Button>
            <Button 
              variant="secondary" 
              size="sm"
              onClick={onContact}
              className="h-8 w-8 p-0"
            >
              <MessageCircle className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Upgrade Prompt for Owner */}
        {isOwner && daysLeft !== undefined && (
          <div className="mt-3">
            <ListingUpgradePrompt 
              listingId={id}
              daysLeft={daysLeft}
              isOwner={isOwner}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ListingCard;