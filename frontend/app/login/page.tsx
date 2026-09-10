"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { GalleryVerticalEnd } from "lucide-react";

import { LoginForm } from "@/components/login-form";
import { login as loginApi } from "@/service/login";
import { setToken } from "@/lib/auth";
import { toast } from "sonner";

export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function login(e: React.FormEvent) {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const formData = new URLSearchParams({
        username,
        password,
      });

      const accessToken = await loginApi(formData);

      setToken(accessToken);
      toast.success("Login successful!");
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      toast.error(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="grid min-h-svh lg:grid-cols-1">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <LoginForm
              username={username}
              password={password}
              loading={loading}
              error={error}
              onUsernameChange={setUsername}
              onPasswordChange={setPassword}
              onSubmit={login}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
