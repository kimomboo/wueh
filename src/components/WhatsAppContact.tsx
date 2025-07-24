import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { MessageCircle, Phone, Copy, ExternalLink } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

interface WhatsAppContactProps {
  sellerName: string;
  sellerPhone: string;
  listingTitle: string;
  listingPrice: number;
  listingId: string;
}

const WhatsAppContact = ({ 
  sellerName, 
  sellerPhone, 
  listingTitle, 
  listingPrice, 
  listingId 
}: WhatsAppContactProps) => {
  const [customMessage, setCustomMessage] = useState("");
  const { toast } = useToast();

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const defaultMessage = `Hi ${sellerName}! I'm interested in your listing: "${listingTitle}" priced at ${formatPrice(listingPrice)}. Is it still available?`;

  const generateWhatsAppLink = (message: string) => {
    const cleanPhone = sellerPhone.replace(/\D/g, '');
    const formattedPhone = cleanPhone.startsWith('254') ? cleanPhone : `254${cleanPhone.substring(1)}`;
    const encodedMessage = encodeURIComponent(message);
    return `https://wa.me/${formattedPhone}?text=${encodedMessage}`;
  };

  const handleWhatsAppContact = (message: string) => {
    const whatsappUrl = generateWhatsAppLink(message);
    window.open(whatsappUrl, '_blank');
    
    toast({
      title: "Opening WhatsApp",
      description: "Redirecting you to WhatsApp to contact the seller.",
    });
  };

  const handlePhoneCall = () => {
    window.location.href = `tel:${sellerPhone}`;
    
    toast({
      title: "Initiating Call",
      description: `Calling ${sellerName} at ${sellerPhone}`,
    });
  };

  const copyPhoneNumber = () => {
    navigator.clipboard.writeText(sellerPhone);
    toast({
      title: "Phone Number Copied",
      description: "Phone number has been copied to clipboard.",
    });
  };

  return (
    <div className="flex gap-2">
      {/* Direct Call Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handlePhoneCall}
        className="flex items-center gap-2"
      >
        <Phone className="h-4 w-4" />
        Call
      </Button>

      {/* WhatsApp Contact Dialog */}
      <Dialog>
        <DialogTrigger asChild>
          <Button
            variant="default"
            size="sm"
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
          >
            <MessageCircle className="h-4 w-4" />
            WhatsApp
          </Button>
        </DialogTrigger>
        
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-green-600" />
              Contact {sellerName}
            </DialogTitle>
            <DialogDescription>
              Choose how you'd like to contact the seller about this listing.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Seller Info */}
            <div className="p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{sellerName}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">{sellerPhone}</span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={copyPhoneNumber}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>
              <div className="text-sm text-muted-foreground">
                {listingTitle} • {formatPrice(listingPrice)}
              </div>
            </div>

            {/* Quick WhatsApp */}
            <div>
              <Label className="text-sm font-medium">Quick Message</Label>
              <div className="mt-2">
                <Button
                  onClick={() => handleWhatsAppContact(defaultMessage)}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Send Default Message
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                "Hi! I'm interested in your listing..."
              </p>
            </div>

            {/* Custom Message */}
            <div>
              <Label htmlFor="custom-message" className="text-sm font-medium">
                Custom Message
              </Label>
              <Textarea
                id="custom-message"
                placeholder="Type your custom message here..."
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                className="mt-2 min-h-[80px]"
              />
              <Button
                onClick={() => handleWhatsAppContact(customMessage || defaultMessage)}
                disabled={!customMessage.trim()}
                variant="outline"
                className="w-full mt-2"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Send Custom Message
              </Button>
            </div>

            {/* Direct Call Option */}
            <div className="pt-4 border-t">
              <Button
                onClick={handlePhoneCall}
                variant="outline"
                className="w-full"
              >
                <Phone className="h-4 w-4 mr-2" />
                Call {sellerName} Directly
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WhatsAppContact;