import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Badge } from "@/components/ui/badge";
import { Plus, AlertTriangle, Upload, X, MapPin } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import Navbar from "@/components/Navbar";

const formSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters").max(100, "Title too long"),
  description: z.string().min(20, "Description must be at least 20 characters").max(1000, "Description too long"),
  price: z.number().min(1, "Price must be greater than 0"),
  currency: z.string().default("KES"),
  category: z.string().min(1, "Please select a category"),
  condition: z.string().min(1, "Please select item condition"),
  location: z.string().min(1, "Please select your location"),
  delivery: z.string().min(1, "Please select delivery option"),
  images: z.array(z.string()).min(1, "At least one image is required").max(10, "Maximum 10 images allowed")
});

type FormData = z.infer<typeof formSchema>;

const categories = [
  "Electronics & Gadgets",
  "Vehicles & Transport", 
  "Property & Real Estate",
  "Fashion & Beauty",
  "Home & Garden",
  "Sports & Hobbies",
  "Jobs & Services",
  "Education & Learning",
  "Health & Wellness",
  "Children & Baby Items"
];

const conditions = [
  "Brand New",
  "Like New", 
  "Excellent",
  "Good",
  "Fair",
  "Poor"
];

const kenyanCounties = [
  "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Kikuyu", "Machakos", "Meru", "Nyeri", "Thika",
  "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo-Marakwet", "Embu", "Garissa", "Homa Bay", "Isiolo", "Kajiado",
  "Kakamega", "Kericho", "Kiambu", "Kilifi", "Kirinyaga", "Kitui", "Kwale", "Laikipia", "Lamu", "Machakos",
  "Makueni", "Mandera", "Marsabit", "Migori", "Murang'a", "Nandi", "Narok", "Nyandarua", "Nyamira", "Samburu",
  "Siaya", "Taita-Taveta", "Tana River", "Tharaka-Nithi", "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
];

const deliveryOptions = [
  "Pickup Only",
  "Delivery Available", 
  "Both Pickup & Delivery"
];

const CreateListing = () => {
  const [images, setImages] = useState<string[]>([]);
  const [freeAdsUsed] = useState(2); // Mock user having used 2/3 free ads
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      currency: "KES",
      images: []
    }
  });

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    // Mock image upload - in real app, upload to Cloudinary
    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setImages(prev => [...prev, result]);
        form.setValue("images", [...images, result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index);
    setImages(newImages);
    form.setValue("images", newImages);
  };

  const onSubmit = async (data: FormData) => {
    if (freeAdsUsed >= 3) {
      toast({
        title: "Free Ads Limit Reached",
        description: "You've used all 3 free ads. Future listings must be Premium.",
        variant: "destructive"
      });
      navigate("/premium");
      return;
    }

    setIsSubmitting(true);
    try {
      // Mock API call - in real app, send to backend
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast({
        title: "Listing Created Successfully!",
        description: "Your ad will expire in 4 days unless upgraded to Premium.",
      });
      
      navigate("/profile");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create listing. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4">Create New Listing</h1>
            <p className="text-muted-foreground">List your item and reach thousands of potential buyers</p>
          </div>

          {/* Free Account Warning */}
          <Card className="mb-6 border-warning/30 bg-warning/5">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-warning mt-0.5" />
                <div>
                  <h3 className="font-semibold text-warning mb-2">Free Account Limits</h3>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Free ads expire after 4 days unless upgraded</li>
                    <li>• You are allowed to post only 3 free ads ever on this account</li>
                    <li>• All future listings must be Premium</li>
                  </ul>
                  <div className="flex items-center justify-between mt-3">
                    <Badge variant={freeAdsUsed >= 3 ? "destructive" : "secondary"}>
                      {freeAdsUsed}/3 Free Ads Used
                    </Badge>
                    <Button variant="warning" size="sm" asChild>
                      <Link to="/premium">View Premium Plans</Link>
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Listing Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Create Your Listing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  {/* Images Upload */}
                  <FormField
                    control={form.control}
                    name="images"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Product Images (Max 10)</FormLabel>
                        <FormControl>
                          <div className="space-y-4">
                            <div className="flex items-center justify-center w-full">
                              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-border border-dashed rounded-lg cursor-pointer bg-muted/50 hover:bg-muted">
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                  <Upload className="w-8 h-8 mb-4 text-muted-foreground" />
                                  <p className="mb-2 text-sm text-muted-foreground">
                                    <span className="font-semibold">Click to upload</span> or drag and drop
                                  </p>
                                  <p className="text-xs text-muted-foreground">PNG, JPG or JPEG (MAX. 5MB each)</p>
                                </div>
                                <input 
                                  type="file" 
                                  className="hidden" 
                                  multiple 
                                  accept="image/*"
                                  onChange={handleImageUpload}
                                />
                              </label>
                            </div>
                            
                            {images.length > 0 && (
                              <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                                {images.map((image, index) => (
                                  <div key={index} className="relative aspect-square">
                                    <img 
                                      src={image} 
                                      alt={`Upload ${index + 1}`}
                                      className="w-full h-full object-cover rounded-lg"
                                    />
                                    <Button
                                      type="button"
                                      variant="destructive"
                                      size="icon"
                                      className="absolute -top-2 -right-2 h-6 w-6"
                                      onClick={() => removeImage(index)}
                                    >
                                      <X className="h-3 w-3" />
                                    </Button>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Title */}
                  <FormField
                    control={form.control}
                    name="title"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Product Title</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. iPhone 14 Pro Max - Excellent Condition" {...field} />
                        </FormControl>
                        <FormDescription>
                          Make it descriptive and specific to attract buyers
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Price and Currency */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="md:col-span-3">
                      <FormField
                        control={form.control}
                        name="price"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Price</FormLabel>
                            <FormControl>
                              <Input 
                                type="number" 
                                placeholder="120000" 
                                {...field}
                                onChange={(e) => field.onChange(Number(e.target.value))}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    <FormField
                      control={form.control}
                      name="currency"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Currency</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="KES">KES (Ksh)</SelectItem>
                              <SelectItem value="USD">USD ($)</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Category and Condition */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="category"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Category</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select category" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {categories.map((category) => (
                                <SelectItem key={category} value={category}>
                                  {category}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="condition"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Condition</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select condition" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {conditions.map((condition) => (
                                <SelectItem key={condition} value={condition}>
                                  {condition}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Location and Delivery */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="location"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Location</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select county" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {kenyanCounties.map((county) => (
                                <SelectItem key={county} value={county}>
                                  <div className="flex items-center gap-2">
                                    <MapPin className="h-3 w-3" />
                                    {county}
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="delivery"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Delivery Options</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select delivery option" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {deliveryOptions.map((option) => (
                                <SelectItem key={option} value={option}>
                                  {option}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Description */}
                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Textarea 
                            placeholder="Describe your item in detail. Include features, specifications, reasons for selling, etc."
                            className="min-h-[120px]"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          Detailed descriptions get more interest and faster sales
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Submit Button */}
                  <div className="flex gap-4 pt-6">
                    <Button 
                      type="submit" 
                      className="flex-1" 
                      disabled={isSubmitting || freeAdsUsed >= 3}
                    >
                      {isSubmitting ? "Creating Listing..." : 
                       freeAdsUsed >= 3 ? "Upgrade to Premium Required" : "Create Free Listing"}
                    </Button>
                    <Button type="button" variant="outline" asChild>
                      <Link to="/">Cancel</Link>
                    </Button>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CreateListing;