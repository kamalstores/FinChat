import { getProfile } from "@/service/user";
import { create } from "zustand";
import { logout } from "./auth";
import { toast } from "sonner";

type Profile = {
    id: string;
    username: string;
    role: string;
};

type AuthState = {
    profile: Profile | null;
    loading: boolean;

    setProfile: (p: Profile) => void;
    setLoading: (v: boolean) => void;
    clearProfile: () => void;

    loadProfile: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
    profile: null,
    loading: false,

    setProfile: (p) => set({ profile: p }),
    setLoading: (v) => set({ loading: v }),

    clearProfile: () => set({ profile: null }),

    loadProfile: async () => {
        try {
            set({ loading: true });

            const profile = await getProfile();
            set({ profile });
        } catch (err) {
            toast.error("Failed to load profile. Please log in again.");
            set({ profile: null });
            logout();
            window.location.href = "/login";
        } finally {
            set({ loading: false });
        }
    },
}));