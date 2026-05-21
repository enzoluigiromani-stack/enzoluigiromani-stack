import { redirect } from "next/navigation";

// Root route redirects to dashboard; the actual dashboard page lives at (dashboard)/dashboard/page.tsx
export default function RootPage() {
  redirect("/dashboard");
}
