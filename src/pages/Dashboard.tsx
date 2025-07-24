import { useAuthStore } from "@/store/authStore";
import { Navigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import UserDashboard from "@/components/UserDashboard";

const Dashboard = () => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <UserDashboard />
    </div>
  );
};

export default Dashboard;