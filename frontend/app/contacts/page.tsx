"use client"

import React from 'react'

export default function ContactsPage() {
  return (
    <div className="flex flex-1 overflow-hidden">
      <main className="flex-1 overflow-hidden p-6">
        <h1 className="text-2xl font-bold mb-6">Contacts Management</h1>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 mb-4">This page will allow you to manage client and provider contacts.</p>
          <div className="p-4 bg-gray-50 rounded border border-gray-200">
            <p className="text-sm text-gray-500">This page is under development. Contact management features will be implemented in future iterations.</p>
          </div>
        </div>
      </main>
    </div>
  )
} 