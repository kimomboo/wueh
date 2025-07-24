import { useState } from "react";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import RecentListings from "@/components/RecentListings";
import WelcomeOverlay from "@/components/WelcomeOverlay";

const Index = () => {
  const [showWelcome] = useState(true);
  const userName = "John"; // This would come from auth context

  return (
    <div className="min-h-screen bg-background">
      {showWelcome && <WelcomeOverlay username={userName} />}
      
      <Navbar />
      <HeroSection />
      <RecentListings />
      
      {/* Footer placeholder */}
      <footer className="bg-primary text-primary-foreground py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 PeerStorm Nexus Arena. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
