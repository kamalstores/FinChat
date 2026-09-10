"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { toast } from "sonner";

import { register } from "@/service/register";
import { setToken } from "@/lib/auth";
import { SignupForm } from "@/components/signup-form";

export default function SignupPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function signup(e: React.FormEvent) {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      if (password !== confirmPassword) {
        throw new Error("Passwords do not match");
      }

      const payload = { username, password };
      const accessToken = await register(payload);
      setToken(accessToken);

      toast.success("Account created successfully!");
      router.replace("/");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Signup failed";

      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-svh lg:grid-cols-1">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <SignupForm
              username={username}
              password={password}
              confirmPassword={confirmPassword}
              loading={loading}
              error={error}
              onUsernameChange={setUsername}
              onPasswordChange={setPassword}
              onConfirmPasswordChange={setConfirmPassword}
              onSubmit={signup}
            />
          </div>
        </div>
      </div>
    </div>
  );
}