import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Shield, Mail, Phone, MapPin, Eye, EyeOff } from "lucide-react";
import { Link } from "react-router-dom";

const Auth = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState("login");

  const kenyanCounties = [
    "Nairobi", "Mombasa", "Kiambu", "Nakuru", "Machakos", "Kajiado", 
    "Kisumu", "Uasin Gishu", "Meru", "Kilifi", "Nyeri", "Murang'a",
    "Kwale", "Makueni", "Nyandarua", "Laikipia", "Kericho", "Bomet",
    "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya", "Kisii",
    "Nyamira", "Migori", "Homa Bay", "Turkana", "West Pokot", "Samburu",
    "Trans Nzoia", "Nandi", "Baringo", "Elgeyo-Marakwet", "Garissa",
    "Wajir", "Mandera", "Marsabit", "Isiolo", "Tana River", "Lamu",
    "Taita-Taveta", "Embu", "Tharaka-Nithi", "Kitui", "Kirinyaga"
  ];

  return (
    <div className="min-h-screen bg-gradient-hero flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2 mb-4">
            <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">PeerStorm</h1>
              <p className="text-sm text-white/70">Nexus Arena</p>
            </div>
          </Link>
          <h2 className="text-2xl font-bold text-white mb-2">
            Join Kenya's Premier Marketplace
          </h2>
          <p className="text-white/80">Connect, trade, and grow your business</p>
        </div>

        <Card className="bg-white/95 backdrop-blur-sm border-white/20">
          <CardHeader className="pb-4">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login">Sign In</TabsTrigger>
                <TabsTrigger value="register">Register</TabsTrigger>
              </TabsList>
            </Tabs>
          </CardHeader>

          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              {/* Login Form */}
              <TabsContent value="login" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="login-email">Email or Phone</Label>
                  <div className="relative">
                    <Input 
                      id="login-email"
                      type="text" 
                      placeholder="Enter your email or phone"
                      className="pl-10"
                    />
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="login-password">Password</Label>
                  <div className="relative">
                    <Input 
                      id="login-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <Button className="w-full" size="lg">
                  Sign In
                </Button>

                <div className="text-center">
                  <Button variant="link" className="text-sm">
                    Forgot your password?
                  </Button>
                </div>
              </TabsContent>

              {/* Register Form */}
              <TabsContent value="register" className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input id="username" placeholder="Choose username" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input id="fullName" placeholder="Your full name" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email Address *</Label>
                  <div className="relative">
                    <Input 
                      id="email"
                      type="email" 
                      placeholder="your.email@example.com"
                      className="pl-10"
                      required
                    />
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number *</Label>
                  <div className="flex gap-2">
                    <Select defaultValue="+254">
                      <SelectTrigger className="w-20">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="+254">🇰🇪 +254</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="relative flex-1">
                      <Input 
                        id="phone"
                        type="tel" 
                        placeholder="7XX XXX XXX"
                        className="pl-10"
                        required
                      />
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Must be a valid Kenyan mobile number (07XX or 01XX)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">County</Label>
                  <div className="relative">
                    <Select>
                      <SelectTrigger className="pl-10">
                        <SelectValue placeholder="Select your county" />
                      </SelectTrigger>
                      <SelectContent>
                        {kenyanCounties.map((county) => (
                          <SelectItem key={county} value={county.toLowerCase()}>
                            {county}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="register-password">Password</Label>
                  <div className="relative">
                    <Input 
                      id="register-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a strong password"
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="bg-warning/10 border border-warning/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <div className="text-warning">⚠️</div>
                    <div className="text-sm">
                      <p className="font-medium text-warning mb-1">Free Account Limits:</p>
                      <p className="text-muted-foreground">
                        • Only 3 free ads per account (lifetime)
                        • Free ads expire after 4 days
                        • All future ads must be Premium
                      </p>
                    </div>
                  </div>
                </div>

                <Button className="w-full" size="lg">
                  Create Account
                </Button>

                <p className="text-xs text-center text-muted-foreground">
                  By registering, you agree to our Terms of Service and Privacy Policy
                </p>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <div className="text-center mt-6">
          <Button variant="link" asChild className="text-white/80 hover:text-white">
            <Link to="/">← Back to Home</Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Auth;