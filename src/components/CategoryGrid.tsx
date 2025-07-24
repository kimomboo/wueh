import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp } from "lucide-react";
import { useListingStore } from "@/store/listingStore";

const categories = [
  { 
    name: "Electronics & Gadgets", 
    count: 12500, 
    icon: "📱",
    subcategories: ["Phones", "Laptops", "Cameras", "Audio", "Gaming"]
  },
  { 
    name: "Vehicles & Transport", 
    count: 8200, 
    icon: "🚗",
    subcategories: ["Cars", "Motorcycles", "Trucks", "Spare Parts", "Boats"]
  },
  { 
    name: "Property & Real Estate", 
    count: 5800, 
    icon: "🏠",
    subcategories: ["Houses", "Apartments", "Land", "Commercial", "Vacation Rentals"]
  },
  { 
    name: "Fashion & Beauty", 
    count: 15300, 
    icon: "👕",
    subcategories: ["Clothing", "Shoes", "Accessories", "Beauty Products", "Jewelry"]
  },
  { 
    name: "Home & Garden", 
    count: 9100, 
    icon: "🏡",
    subcategories: ["Furniture", "Appliances", "Decor", "Garden Tools", "Kitchen"]
  },
  { 
    name: "Sports & Hobbies", 
    count: 4200, 
    icon: "⚽",
    subcategories: ["Sports Equipment", "Fitness", "Outdoor Gear", "Collectibles", "Musical Instruments"]
  },
  { 
    name: "Jobs & Services", 
    count: 3100, 
    icon: "💼",
    subcategories: ["Full-time Jobs", "Part-time", "Freelance", "Services", "Internships"]
  },
  { 
    name: "Education & Learning", 
    count: 2800, 
    icon: "📚",
    subcategories: ["Books", "Courses", "Tutoring", "Educational Materials", "Software"]
  },
  { 
    name: "Health & Wellness", 
    count: 1900, 
    icon: "🏥",
    subcategories: ["Medical Equipment", "Supplements", "Fitness Equipment", "Healthcare Services", "Beauty Treatments"]
  },
  { 
    name: "Children & Baby Items", 
    count: 6700, 
    icon: "👶",
    subcategories: ["Baby Gear", "Toys", "Clothing", "Furniture", "Educational Toys"]
  }
];

const CategoryGrid = () => {
  const [showAll, setShowAll] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const { setSelectedCategory } = useListingStore();

  const displayedCategories = showAll ? categories : categories.slice(0, 6);

  const handleCategoryClick = (categoryName: string) => {
    setSelectedCategory(categoryName);
    // Navigate to search results or trigger search
  };

  const toggleCategoryExpansion = (categoryName: string) => {
    setExpandedCategory(expandedCategory === categoryName ? null : categoryName);
  };

  return (
    <section className="py-12 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-2">Browse by Category</h2>
          <p className="text-muted-foreground">Find exactly what you're looking for</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayedCategories.map((category) => (
            <Card 
              key={category.name}
              className="group hover:shadow-elegant transition-all duration-300 cursor-pointer border-2 hover:border-primary/20"
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-3xl group-hover:scale-110 transition-transform">
                      {category.icon}
                    </div>
                    <div>
                      <h3 
                        className="font-semibold text-lg group-hover:text-primary transition-colors"
                        onClick={() => handleCategoryClick(category.name)}
                      >
                        {category.name}
                      </h3>
                      <Badge variant="secondary" className="mt-1">
                        {category.count.toLocaleString()} items
                      </Badge>
                    </div>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleCategoryExpansion(category.name)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    {expandedCategory === category.name ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {/* Subcategories */}
                {expandedCategory === category.name && (
                  <div className="space-y-2 animate-fade-in">
                    <div className="text-sm font-medium text-muted-foreground mb-2">
                      Popular in {category.name}:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {category.subcategories.map((sub) => (
                        <Badge
                          key={sub}
                          variant="outline"
                          className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                          onClick={() => handleCategoryClick(sub)}
                        >
                          {sub}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quick Stats */}
                <div className="mt-4 pt-4 border-t border-border/50">
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>New today: {Math.floor(category.count * 0.02)}</span>
                    <span>This week: {Math.floor(category.count * 0.15)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Show More/Less Button */}
        <div className="text-center mt-8">
          <Button
            variant="outline"
            onClick={() => setShowAll(!showAll)}
            className="min-w-[200px]"
          >
            {showAll ? (
              <>
                <ChevronUp className="h-4 w-4 mr-2" />
                Show Less Categories
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-2" />
                Show All Categories
              </>
            )}
          </Button>
        </div>
      </div>
    </section>
  );
};

export default CategoryGrid;