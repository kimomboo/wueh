import { useEffect, useState } from "react";
import { X } from "lucide-react";

interface WelcomeOverlayProps {
  username?: string;
}

const WelcomeOverlay = ({ username = "Friend" }: WelcomeOverlayProps) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center animate-fade-in">
      <div className="bg-background rounded-2xl p-8 mx-4 max-w-md w-full shadow-glow border border-primary/20 animate-slide-in">
        <button
          onClick={() => setIsVisible(false)}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
        >
          <X className="h-5 w-5" />
        </button>
        
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">👋</span>
          </div>
          
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Hey there, {username}!
          </h2>
          
          <p className="text-muted-foreground mb-4">
            Hope you're doing good. Welcome back to PeerStorm Nexus Arena!
          </p>
          
          <div className="w-full bg-muted rounded-full h-1">
            <div className="bg-gradient-primary h-1 rounded-full animate-pulse" style={{ width: '100%' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeOverlay;