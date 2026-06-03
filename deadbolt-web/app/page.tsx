import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { SignInButton, SignUpButton } from "@clerk/nextjs";

export default async function Home() {
  const { userId } = await auth();
  if (userId) {
    // Redirect to your original Sentinel Grid UI
    redirect("/sentinel-grid");
  }

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-gray-50 p-6">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">
        Deadbolt Endpoint Shield
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        Please sign in to access the Sentinel Grid security portal
      </p>
      <div className="flex gap-4">
        <SignInButton mode="modal">
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Sign In
          </button>
        </SignInButton>
        <SignUpButton mode="modal">
          <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-100">
            Sign Up
          </button>
        </SignUpButton>
      </div>
    </div>
  );
}
