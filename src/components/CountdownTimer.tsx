import { useState, useEffect } from "react";
import { Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface CountdownTimerProps {
  expiryDate: Date;
  isPremium?: boolean;
  showIcon?: boolean;
  className?: string;
}

const CountdownTimer = ({ expiryDate, isPremium = false, showIcon = true, className = "" }: CountdownTimerProps) => {
  const [timeLeft, setTimeLeft] = useState("");
  const [isExpired, setIsExpired] = useState(false);

  useEffect(() => {
    const updateTimer = () => {
      const now = new Date().getTime();
      const expiry = expiryDate.getTime();
      const difference = expiry - now;

      if (difference <= 0) {
        setIsExpired(true);
        setTimeLeft("Expired");
        return;
      }

      const days = Math.floor(difference / (1000 * 60 * 60 * 24));
      const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));

      if (days > 0) {
        setTimeLeft(`${days}d ${hours}h left`);
      } else if (hours > 0) {
        setTimeLeft(`${hours}h ${minutes}m left`);
      } else {
        setTimeLeft(`${minutes}m left`);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [expiryDate]);

  if (isPremium) {
    return null; // Don't show countdown for premium ads
  }

  const getVariant = () => {
    if (isExpired) return "destructive";
    
    const now = new Date().getTime();
    const expiry = expiryDate.getTime();
    const hoursLeft = (expiry - now) / (1000 * 60 * 60);
    
    if (hoursLeft <= 24) return "destructive";
    if (hoursLeft <= 48) return "warning";
    return "secondary";
  };

  return (
    <Badge variant={getVariant()} className={className}>
      {showIcon && <Clock className="h-3 w-3 mr-1" />}
      {timeLeft}
    </Badge>
  );
};

export default CountdownTimer;