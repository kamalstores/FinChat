"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Assistant } from "./assistant";
import { isAuthenticated } from "@/lib/auth";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  return (
    <>
      <Assistant />
    </>

  );
}
