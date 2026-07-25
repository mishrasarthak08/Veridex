import Link from "next/link";
import { FileQuestion, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex h-screen w-full flex-col items-center justify-center bg-zinc-950 text-white">
      <FileQuestion className="h-16 w-16 text-indigo-500 mb-6" />
      <h2 className="text-3xl font-bold mb-2">404 - Not Found</h2>
      <p className="text-zinc-400 mb-8 max-w-md text-center">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Link href="/">
        <Button variant="default" className="flex items-center gap-2">
          <Home className="h-4 w-4" />
          Return Home
        </Button>
      </Link>
    </div>
  );
}
