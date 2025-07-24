import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Crown, Check, Smartphone, Clock, TrendingUp, Zap, ArrowLeft } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import Navbar from "@/components/Navbar";

interface PremiumPlan {
  days: number;
  price: number;
  popular?: boolean;
  savings?: string;
}

const premiumPlans: PremiumPlan[] = [
  { days: 5, price: 150 },
  { days: 7, price: 200, popular: true },
  { days: 10, price: 230 },
  { days: 13, price: 250 },
  { days: 15, price: 280, savings: "Best Value" },
  { days: 20, price: 315 },
  { days: 25, price: 335 },
  { days: 30, price: 379, savings: "Maximum Exposure" }
];

const PremiumPlans = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const listingId = searchParams.get("listing");
  
  const [selectedPlan, setSelectedPlan] = useState<PremiumPlan | null>(null);
  const [mpesaNumber, setMpesaNumber] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [paymentStep, setPaymentStep] = useState<"input" | "processing" | "success" | "failed">("input");

  const handlePlanSelect = (plan: PremiumPlan) => {
    setSelectedPlan(plan);
    setShowPaymentDialog(true);
    setPaymentStep("input");
  };

  const validateKenyanNumber = (number: string): boolean => {
    // Remove any spaces, dashes, or plus signs
    const cleaned = number.replace(/[\s\-\+]/g, "");
    
    // Check if it's a valid Kenyan mobile number
    const kenyanPatterns = [
      /^(07\d{8})$/, // 07xxxxxxxx
      /^(01\d{8})$/, // 01xxxxxxxx  
      /^(254\d{9})$/, // 254xxxxxxxxx
      /^(\+254\d{9})$/ // +254xxxxxxxxx
    ];
    
    return kenyanPatterns.some(pattern => pattern.test(cleaned));
  };

  const formatKenyanNumber = (number: string): string => {
    const cleaned = number.replace(/[\s\-\+]/g, "");
    
    if (cleaned.startsWith("07") || cleaned.startsWith("01")) {
      return `254${cleaned.substring(1)}`;
    }
    if (cleaned.startsWith("254")) {
      return cleaned;
    }
    if (cleaned.startsWith("+254")) {
      return cleaned.substring(1);
    }
    
    return cleaned;
  };

  const initiateSTKPush = async () => {
    if (!selectedPlan || !mpesaNumber) return;

    if (!validateKenyanNumber(mpesaNumber)) {
      toast({
        title: "Invalid Phone Number",
        description: "Please enter a valid Kenyan mobile number (07xx or 01xx)",
        variant: "destructive"
      });
      return;
    }

    setIsProcessing(true);
    setPaymentStep("processing");

    try {
      // Mock M-PESA STK Push API call
      const formattedNumber = formatKenyanNumber(mpesaNumber);
      
      // Simulate API call to Safaricom Daraja API
      const response = await fetch("/api/mpesa/stkpush", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          phoneNumber: formattedNumber,
          amount: selectedPlan.price,
          accountReference: listingId || "PREMIUM_UPGRADE",
          transactionDesc: `PeerStorm Premium - ${selectedPlan.days} days`
        })
      });

      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Mock success response
      const mockSuccess = Math.random() > 0.2; // 80% success rate for demo

      if (mockSuccess) {
        setPaymentStep("success");
        
        // Show success message
        toast({
          title: "Payment Successful!",
          description: `Your listing has been upgraded to Premium for ${selectedPlan.days} days.`,
        });

        // Redirect after success
        setTimeout(() => {
          setShowPaymentDialog(false);
          if (listingId) {
            navigate("/profile");
          } else {
            navigate("/");
          }
        }, 2000);

      } else {
        throw new Error("Payment failed");
      }

    } catch (error) {
      setPaymentStep("failed");
      toast({
        title: "Payment Failed",
        description: "Transaction was cancelled or failed. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const renderPaymentDialog = () => {
    switch (paymentStep) {
      case "input":
        return (
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Smartphone className="h-5 w-5" />
                M-PESA Payment
              </DialogTitle>
              <DialogDescription>
                Pay Ksh {selectedPlan?.price.toLocaleString()} to upgrade your listing
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="p-4 bg-primary/5 rounded-lg border">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Premium Upgrade</span>
                  <Badge variant="secondary">{selectedPlan?.days} days</Badge>
                </div>
                <div className="text-2xl font-bold">Ksh {selectedPlan?.price.toLocaleString()}</div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="mpesa-number">M-PESA Number</Label>
                <Input
                  id="mpesa-number"
                  placeholder="07xxxxxxxx or 01xxxxxxxx"
                  value={mpesaNumber}
                  onChange={(e) => setMpesaNumber(e.target.value)}
                  className="text-lg"
                />
                <p className="text-sm text-muted-foreground">
                  Enter your M-PESA registered phone number
                </p>
              </div>

              <div className="space-y-2">
                <Button 
                  onClick={initiateSTKPush}
                  className="w-full"
                  disabled={!mpesaNumber || isProcessing}
                >
                  {isProcessing ? "Processing..." : "Pay with M-PESA"}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowPaymentDialog(false)}
                  className="w-full"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        );

      case "processing":
        return (
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 animate-spin" />
                Processing Payment
              </DialogTitle>
              <DialogDescription>
                Please check your phone for M-PESA prompt
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 text-center py-6">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                <Smartphone className="h-8 w-8 text-primary animate-pulse" />
              </div>
              <div>
                <p className="font-medium">STK Push sent to {mpesaNumber}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Enter your M-PESA PIN to complete payment
                </p>
              </div>
              <div className="text-lg font-bold">
                Ksh {selectedPlan?.price.toLocaleString()}
              </div>
            </div>
          </DialogContent>
        );

      case "success":
        return (
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-green-600">
                <Check className="h-5 w-5" />
                Payment Successful!
              </DialogTitle>
              <DialogDescription>
                Your listing has been upgraded to Premium
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 text-center py-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <Crown className="h-8 w-8 text-green-600" />
              </div>
              <div>
                <p className="font-medium text-green-600">Upgrade Complete!</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Your ad will be featured for {selectedPlan?.days} days
                </p>
              </div>
            </div>
          </DialogContent>
        );

      case "failed":
        return (
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-destructive">Payment Failed</DialogTitle>
              <DialogDescription>
                The transaction could not be completed
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 text-center py-6">
              <div className="text-destructive text-sm">
                Payment was cancelled or failed. Please try again.
              </div>
              <div className="space-y-2">
                <Button 
                  onClick={() => setPaymentStep("input")}
                  className="w-full"
                >
                  Try Again
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowPaymentDialog(false)}
                  className="w-full"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        );
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </div>
            
            <h1 className="text-4xl font-bold mb-4 bg-gradient-primary bg-clip-text text-transparent">
              Premium Plans
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Boost your listings with Premium features for maximum visibility and faster sales
            </p>
            
            {listingId && (
              <Badge variant="warning" className="mt-4">
                Upgrading specific listing: #{listingId}
              </Badge>
            )}
          </div>

          {/* Premium Benefits */}
          <Card className="mb-12 border-primary/20 bg-gradient-subtle">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold text-center mb-6">Premium Benefits</h3>
              <div className="grid md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <TrendingUp className="h-6 w-6 text-primary" />
                  </div>
                  <h4 className="font-semibold mb-2">Priority Placement</h4>
                  <p className="text-sm text-muted-foreground">Featured in hero banner and top results</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Zap className="h-6 w-6 text-primary" />
                  </div>
                  <h4 className="font-semibold mb-2">Extended Visibility</h4>
                  <p className="text-sm text-muted-foreground">No 4-day expiration limit</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Crown className="h-6 w-6 text-primary" />
                  </div>
                  <h4 className="font-semibold mb-2">Premium Badge</h4>
                  <p className="text-sm text-muted-foreground">Stand out with premium branding</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Check className="h-6 w-6 text-primary" />
                  </div>
                  <h4 className="font-semibold mb-2">Instant Activation</h4>
                  <p className="text-sm text-muted-foreground">Immediate upgrade via M-PESA</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pricing Plans */}
          <div className="grid md:grid-cols-4 gap-6">
            {premiumPlans.map((plan) => (
              <Card 
                key={plan.days}
                className={`relative transition-all duration-300 hover:shadow-elegant ${
                  plan.popular ? 'ring-2 ring-primary/50 shadow-premium' : ''
                }`}
              >
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary">
                    Most Popular
                  </Badge>
                )}
                {plan.savings && (
                  <Badge 
                    variant="secondary" 
                    className="absolute -top-3 right-4 bg-secondary"
                  >
                    {plan.savings}
                  </Badge>
                )}
                
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">{plan.days} Days</CardTitle>
                  <div className="text-3xl font-bold">
                    Ksh {plan.price.toLocaleString()}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    ~Ksh {Math.round(plan.price / plan.days)}/day
                  </p>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-3 mb-6">
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>No expiration for {plan.days} days</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Priority search placement</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Premium badge display</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Featured in hero banner</span>
                    </div>
                  </div>
                  
                  <Dialog open={showPaymentDialog && selectedPlan?.days === plan.days} onOpenChange={setShowPaymentDialog}>
                    <DialogTrigger asChild>
                      <Button 
                        className="w-full" 
                        variant={plan.popular ? "default" : "outline"}
                        onClick={() => handlePlanSelect(plan)}
                      >
                        <Crown className="h-4 w-4 mr-2" />
                        Upgrade Now
                      </Button>
                    </DialogTrigger>
                    {renderPaymentDialog()}
                  </Dialog>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Payment Info */}
          <Card className="mt-12 border-muted">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <Smartphone className="h-6 w-6 text-primary" />
                <h3 className="text-lg font-semibold">Secure M-PESA Payment</h3>
              </div>
              <div className="grid md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                <div>
                  <strong>Instant Processing:</strong> Payment is processed immediately via Safaricom M-PESA STK Push
                </div>
                <div>
                  <strong>Secure Transaction:</strong> All payments are encrypted and processed through official Daraja API
                </div>
                <div>
                  <strong>Immediate Upgrade:</strong> Your listing is upgraded instantly upon successful payment
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PremiumPlans;