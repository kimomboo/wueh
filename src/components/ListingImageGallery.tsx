import { useState } from "react";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, X, ZoomIn, Share2, Heart } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ListingImageGalleryProps {
  images: string[];
  title: string;
  isPremium?: boolean;
  onShare?: () => void;
  onFavorite?: () => void;
  isFavorited?: boolean;
}

const ListingImageGallery = ({ 
  images, 
  title, 
  isPremium = false,
  onShare,
  onFavorite,
  isFavorited = false
}: ListingImageGalleryProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isZoomed, setIsZoomed] = useState(false);

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const goToImage = (index: number) => {
    setCurrentIndex(index);
  };

  return (
    <div className="space-y-4">
      {/* Main Image Display */}
      <div className="relative aspect-[4/3] overflow-hidden rounded-lg bg-muted group">
        <img
          src={images[currentIndex] || "/placeholder.svg"}
          alt={`${title} - Image ${currentIndex + 1}`}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        
        {/* Overlay Badges */}
        <div className="absolute top-4 left-4 flex gap-2">
          {isPremium && (
            <Badge className="bg-secondary text-secondary-foreground">
              Premium
            </Badge>
          )}
          <Badge variant="outline" className="bg-black/50 text-white border-white/20">
            {currentIndex + 1} / {images.length}
          </Badge>
        </div>

        {/* Action Buttons */}
        <div className="absolute top-4 right-4 flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="bg-black/50 hover:bg-black/70 text-white"
            onClick={onFavorite}
          >
            <Heart className={`h-4 w-4 ${isFavorited ? 'fill-red-500 text-red-500' : ''}`} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="bg-black/50 hover:bg-black/70 text-white"
            onClick={onShare}
          >
            <Share2 className="h-4 w-4" />
          </Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="bg-black/50 hover:bg-black/70 text-white"
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl w-full h-[80vh] p-0">
              <div className="relative w-full h-full bg-black">
                <img
                  src={images[currentIndex]}
                  alt={`${title} - Full size`}
                  className="w-full h-full object-contain"
                />
                
                {/* Navigation in fullscreen */}
                {images.length > 1 && (
                  <>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                      onClick={prevImage}
                    >
                      <ChevronLeft className="h-6 w-6" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                      onClick={nextImage}
                    >
                      <ChevronRight className="h-6 w-6" />
                    </Button>
                  </>
                )}
                
                {/* Image counter in fullscreen */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                  <Badge variant="outline" className="bg-black/50 text-white border-white/20">
                    {currentIndex + 1} of {images.length}
                  </Badge>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Navigation Arrows */}
        {images.length > 1 && (
          <>
            <Button
              variant="ghost"
              size="icon"
              className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={prevImage}
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={nextImage}
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </>
        )}
      </div>

      {/* Thumbnail Strip */}
      {images.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          {images.map((image, index) => (
            <button
              key={index}
              onClick={() => goToImage(index)}
              className={`flex-shrink-0 w-16 h-16 rounded-md overflow-hidden border-2 transition-all ${
                index === currentIndex
                  ? 'border-primary shadow-md'
                  : 'border-transparent hover:border-muted-foreground/50'
              }`}
            >
              <img
                src={image}
                alt={`Thumbnail ${index + 1}`}
                className="w-full h-full object-cover"
              />
            </button>
          ))}
        </div>
      )}

      {/* Swipe Indicators for Mobile */}
      {images.length > 1 && (
        <div className="flex justify-center gap-1 md:hidden">
          {images.map((_, index) => (
            <button
              key={index}
              onClick={() => goToImage(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentIndex
                  ? 'bg-primary w-4'
                  : 'bg-muted-foreground/30'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ListingImageGallery;