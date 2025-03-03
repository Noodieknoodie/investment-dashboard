"use client"

import DashboardLayout from "./payments/components/dashboard-layout"

export default function Home() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="bg-white shadow-md rounded-lg p-6">
        <p className="text-gray-500">Main dashboard content will be displayed here.</p>
      </div>
    </div>
  );
}