import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Heart } from "lucide-react";

const Favorites = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5" />
              My Favorites
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-center py-8">
              Your favorite listings will appear here.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Favorites;