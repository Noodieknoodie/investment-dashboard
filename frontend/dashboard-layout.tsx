"use client"

import { useState } from "react"
import { ClientSidebar } from "./client-sidebar"
import { TopNavigation } from "./top-navigation"
import { ClientPaymentPage } from "./client-payment-page"
import type { Client } from "./types"

// Sample data
const sampleClients: Client[] = [
  {
    id: "1",
    name: "Acme Corporation",
    planProvider: "John Hancock",
    paymentFrequency: "Quarterly",
    feeStructure: "Flat Rate",
    feeAmount: 2500,
    aum: 2250000,
    lastPayment: "2023-12-15",
    lastPaymentAmount: 2500,
    complianceStatus: "Compliant",
  },
  {
    id: "2",
    name: "Globex Industries",
    planProvider: "Voya",
    paymentFrequency: "Monthly",
    feeStructure: "Percentage of AUM",
    feePercentage: 0.75,
    aum: 1250000,
    lastPayment: "2024-02-01",
    lastPaymentAmount: 781.25,
    complianceStatus: "Review Needed",
  },
  {
    id: "3",
    name: "Initech LLC",
    planProvider: "John Hancock",
    paymentFrequency: "Quarterly",
    feeStructure: "Flat Rate",
    feeAmount: 3750,
    aum: 6250000,
    lastPayment: "2024-01-10",
    lastPaymentAmount: 3750,
    complianceStatus: "Compliant",
  },
  {
    id: "4",
    name: "Massive Dynamic",
    planProvider: "Voya",
    paymentFrequency: "Monthly",
    feeStructure: "Percentage of AUM",
    feePercentage: 0.65,
    aum: 3450000,
    lastPayment: "2024-02-05",
    lastPaymentAmount: 1871.25,
    complianceStatus: "Compliant",
  },
  {
    id: "5",
    name: "Stark Industries",
    planProvider: "Fidelity",
    paymentFrequency: "Quarterly",
    feeStructure: "Flat Rate",
    feeAmount: 5000,
    aum: 9250000,
    lastPayment: "2023-11-20",
    lastPaymentAmount: 5000,
    complianceStatus: "Payment Overdue",
  },
]

export default function DashboardLayout() {
  const [selectedClient, setSelectedClient] = useState<Client | null>(null)
  const [documentViewerOpen, setDocumentViewerOpen] = useState(false)
  const [currentDocument, setCurrentDocument] = useState<string | null>(null)

  const toggleDocumentViewer = () => {
    setDocumentViewerOpen(!documentViewerOpen)
  }

  const viewDocument = (documentUrl: string) => {
    setCurrentDocument(documentUrl)
    if (!documentViewerOpen) {
      setDocumentViewerOpen(true)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <TopNavigation />

      <div className="flex flex-1 overflow-hidden">
        <ClientSidebar clients={sampleClients} selectedClient={selectedClient} onSelectClient={setSelectedClient} />

        <main className="flex-1 overflow-hidden p-6">
          {selectedClient ? (
            <ClientPaymentPage
              client={selectedClient}
              onViewDocument={viewDocument}
              toggleDocumentViewer={toggleDocumentViewer}
              documentViewerOpen={documentViewerOpen}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center p-8 max-w-md">
                <h2 className="text-2xl font-semibold text-gray-700 mb-2">Welcome to the Payment Dashboard</h2>
                <p className="text-gray-500 mb-6">
                  Select a client from the sidebar to view and manage their payment details.
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

