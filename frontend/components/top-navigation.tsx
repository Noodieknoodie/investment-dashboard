import Link from "next/link";

export default function TopNavigation() {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-xl font-bold">Investment Dashboard</h1>
        <div className="flex space-x-4">
          <Link href="/" className="hover:text-gray-300">Dashboard</Link>
          <Link href="/payments" className="hover:text-gray-300">Payments</Link>
          <Link href="/companies" className="hover:text-gray-300">Companies</Link>
          <Link href="/plans" className="hover:text-gray-300">Plans</Link>
          <Link href="/participants" className="hover:text-gray-300">Participants</Link>
        </div>
      </div>
    </nav>
  );
} 