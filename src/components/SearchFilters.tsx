import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { X, Filter, MapPin, DollarSign, Grid3X3 } from "lucide-react";
import { useListingStore } from "@/store/listingStore";

const categories = [
  { name: "Electronics & Gadgets", count: 12500 },
  { name: "Vehicles & Transport", count: 8200 },
  { name: "Property & Real Estate", count: 5800 },
  { name: "Fashion & Beauty", count: 15300 },
  { name: "Home & Garden", count: 9100 },
  { name: "Sports & Hobbies", count: 4200 },
  { name: "Jobs & Services", count: 3100 },
  { name: "Education & Learning", count: 2800 },
  { name: "Health & Wellness", count: 1900 },
  { name: "Children & Baby Items", count: 6700 }
];

const kenyanCounties = [
  "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Kikuyu", "Machakos", "Meru", "Nyeri", "Thika",
  "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo-Marakwet", "Embu", "Garissa", "Homa Bay", "Isiolo", "Kajiado",
  "Kakamega", "Kericho", "Kiambu", "Kilifi", "Kirinyaga", "Kitui", "Kwale", "Laikipia", "Lamu", "Makueni",
  "Mandera", "Marsabit", "Migori", "Murang'a", "Nandi", "Narok", "Nyandarua", "Nyamira", "Samburu",
  "Siaya", "Taita-Taveta", "Tana River", "Tharaka-Nithi", "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
];

interface SearchFiltersProps {
  isOpen: boolean;
  onClose: () => void;
}

const SearchFilters = ({ isOpen, onClose }: SearchFiltersProps) => {
  const {
    selectedCategory,
    priceRange,
    selectedLocation,
    setSelectedCategory,
    setPriceRange,
    setSelectedLocation
  } = useListingStore();

  const [tempPriceRange, setTempPriceRange] = useState(priceRange);

  const handleApplyFilters = () => {
    setPriceRange(tempPriceRange);
    onClose();
  };

  const handleClearFilters = () => {
    setSelectedCategory('');
    setSelectedLocation('');
    setPriceRange([0, 10000000]);
    setTempPriceRange([0, 10000000]);
  };

  const formatPrice = (amount: number) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(0)}K`;
    }
    return amount.toString();
  };

  const activeFiltersCount = [
    selectedCategory,
    selectedLocation,
    priceRange[0] > 0 || priceRange[1] < 10000000
  ].filter(Boolean).length;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
      <div className="fixed inset-y-0 right-0 w-full max-w-md bg-background shadow-xl">
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              <h2 className="text-lg font-semibold">Filters</h2>
              {activeFiltersCount > 0 && (
                <Badge variant="secondary">{activeFiltersCount}</Badge>
              )}
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Filters Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Category Filter */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Grid3X3 className="h-4 w-4" />
                  Category
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.name} value={category.name}>
                        <div className="flex items-center justify-between w-full">
                          <span>{category.name}</span>
                          <Badge variant="outline" className="ml-2">
                            {category.count.toLocaleString()}
                          </Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Location Filter */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Location
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Locations" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Locations</SelectItem>
                    {kenyanCounties.map((county) => (
                      <SelectItem key={county} value={county}>
                        {county}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Price Range Filter */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  Price Range
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="px-2">
                  <Slider
                    value={tempPriceRange}
                    onValueChange={setTempPriceRange}
                    max={10000000}
                    min={0}
                    step={1000}
                    className="w-full"
                  />
                </div>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>KES {formatPrice(tempPriceRange[0])}</span>
                  <span>KES {formatPrice(tempPriceRange[1])}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label htmlFor="min-price" className="text-xs">Min Price</Label>
                    <Input
                      id="min-price"
                      type="number"
                      value={tempPriceRange[0]}
                      onChange={(e) => setTempPriceRange([Number(e.target.value), tempPriceRange[1]])}
                      className="h-8"
                    />
                  </div>
                  <div>
                    <Label htmlFor="max-price" className="text-xs">Max Price</Label>
                    <Input
                      id="max-price"
                      type="number"
                      value={tempPriceRange[1]}
                      onChange={(e) => setTempPriceRange([tempPriceRange[0], Number(e.target.value)])}
                      className="h-8"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Footer Actions */}
          <div className="border-t p-6 space-y-3">
            <Button onClick={handleApplyFilters} className="w-full">
              Apply Filters
            </Button>
            <Button 
              variant="outline" 
              onClick={handleClearFilters}
              className="w-full"
            >
              Clear All Filters
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchFilters;