import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Crown, Clock, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";

interface ListingUpgradePromptProps {
  listingId: string;
  daysLeft: number;
  isOwner?: boolean;
}

const ListingUpgradePrompt = ({ listingId, daysLeft, isOwner = false }: ListingUpgradePromptProps) => {
  if (!isOwner || daysLeft > 2) return null;

  const urgencyLevel = daysLeft <= 1 ? "critical" : "warning";
  
  return (
    <Card className={`border-2 ${urgencyLevel === "critical" ? "border-destructive/50 bg-destructive/5" : "border-warning/50 bg-warning/5"}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {urgencyLevel === "critical" ? (
            <Clock className="h-5 w-5 text-destructive mt-0.5" />
          ) : (
            <TrendingUp className="h-5 w-5 text-warning mt-0.5" />
          )}
          <div className="flex-1">
            <h4 className={`font-semibold ${urgencyLevel === "critical" ? "text-destructive" : "text-warning"} mb-1`}>
              {urgencyLevel === "critical" ? "⚠️ Ad Expires Soon!" : "💡 Boost Your Ad"}
            </h4>
            <p className="text-sm text-muted-foreground mb-3">
              {urgencyLevel === "critical" 
                ? "Your ad will disappear soon. Upgrade to Premium to keep it visible and reach more buyers."
                : "Upgrade to Premium for extended visibility, better placement, and more buyer engagement."
              }
            </p>
            <div className="flex gap-2">
              <Button 
                variant={urgencyLevel === "critical" ? "destructive" : "warning"} 
                size="sm" 
                asChild
              >
                <Link to={`/premium?listing=${listingId}`}>
                  <Crown className="h-3 w-3 mr-1" />
                  Upgrade Now
                </Link>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <Link to="/premium">View Plans</Link>
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ListingUpgradePrompt;