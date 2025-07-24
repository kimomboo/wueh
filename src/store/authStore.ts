import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  fullName: string;
  email: string;
  phone: string;
  location: string;
  profilePicture?: string;
  verified: boolean;
  freeAdsUsed: number;
  premiumSubscription?: {
    plan: string;
    expiryDate: Date;
    isActive: boolean;
  };
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
}

interface RegisterData {
  username: string;
  fullName: string;
  email: string;
  phone: string;
  password: string;
  location: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          // Mock API call - replace with actual API
          const mockUser: User = {
            id: '1',
            username: 'john_kamau',
            fullName: 'John Kamau',
            email: email,
            phone: '+254712345678',
            location: 'Nairobi',
            verified: true,
            freeAdsUsed: 2,
          };
          
          set({ 
            user: mockUser, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true });
        try {
          // Mock API call - replace with actual API
          const newUser: User = {
            id: Date.now().toString(),
            ...userData,
            verified: false,
            freeAdsUsed: 0,
          };
          
          set({ 
            user: newUser, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({ 
          user: null, 
          isAuthenticated: false 
        });
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ 
            user: { ...currentUser, ...userData } 
          });
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);