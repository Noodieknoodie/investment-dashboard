"use client"

import { useState } from "react"
import { FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ClientDetails } from "./client-details"
import { PaymentForm } from "./payment-form"
import { PaymentHistory } from "./payment-history"
import { DocumentViewer } from "./document-viewer"
import type { Client, Payment, PaymentPeriod } from "./types"

// Sample payment data with updated fields
const samplePayments: Payment[] = [
  {
    id: "1",
    clientId: "1",
    date: "2023-12-15",
    amount: 2500,
    method: "Check",
    reference: "CHK-12345",
    notes: "Q4 2023 payment",
    documentUrl: "/sample-check.pdf",
    status: "Processed",
    period: "Q4 2023",
    expectedFee: 2500
  },
  {
    id: "2",
    clientId: "1",
    date: "2023-09-15",
    amount: 2500,
    method: "ACH",
    reference: "ACH-67890",
    notes: "Q3 2023 payment",
    documentUrl: "/sample-ach.pdf",
    status: "Processed",
    period: "Q3 2023",
    expectedFee: 2500
  },
  {
    id: "3",
    clientId: "2",
    date: "2024-02-01",
    amount: 781.25,
    method: "Wire",
    reference: "WIRE-54321",
    notes: "February 2024 payment",
    documentUrl: "/sample-wire.pdf",
    status: "Processed",
    period: "February 2024",
    expectedFee: 781.25
  },
  {
    id: "4",
    clientId: "2",
    date: "2024-01-01",
    amount: 781.25,
    method: "Wire",
    reference: "WIRE-98765",
    notes: "January 2024 payment",
    documentUrl: "/sample-wire.pdf",
    status: "Processed",
    period: "January 2024",
    expectedFee: 781.25
  },
  // Example of a split payment
  {
    id: "5",
    clientId: "5",
    date: "2024-01-15",
    amount: 10000,
    method: "Wire",
    reference: "WIRE-SPLIT-001",
    notes: "Catch-up payment covering multiple quarters",
    documentUrl: "/sample-wire-split.pdf",
    status: "Processed",
    appliedPeriods: [
      { period: "Q1 2023", amount: 2500 },
      { period: "Q2 2023", amount: 2500 },
      { period: "Q3 2023", amount: 2500 },
      { period: "Q4 2023", amount: 2500 }
    ]
  }
]

interface ClientPaymentPageProps {
  client: Client
  allClients: Client[] // Added to pass to PaymentHistory
  onViewDocument: (documentUrl: string) => void
  toggleDocumentViewer: () => void
  documentViewerOpen: boolean
}

export function ClientPaymentPage({
  client,
  allClients,
  onViewDocument,
  toggleDocumentViewer,
  documentViewerOpen,
}: ClientPaymentPageProps) {
  const [editingPayment, setEditingPayment] = useState<Payment | null>(null)
  const [currentDocumentUrl, setCurrentDocumentUrl] = useState<string | null>(null)

  // Filter payments for the current client
  const clientPayments = samplePayments.filter((payment) => payment.clientId === client.id)

  const handleEditPayment = (payment: Payment) => {
    setEditingPayment(payment)
    // Scroll to the payment form
    document.getElementById("payment-form-section")?.scrollIntoView({ behavior: "smooth" })
  }

  const handleCancelEdit = () => {
    setEditingPayment(null)
  }

  const handleViewDocument = (documentUrl: string) => {
    setCurrentDocumentUrl(documentUrl)
    onViewDocument(documentUrl)
  }

  return (
    <div className={`flex h-full ${documentViewerOpen ? "space-x-4" : ""}`}>
      <div className={`flex flex-col overflow-hidden ${documentViewerOpen ? "w-3/5" : "w-full"}`}>
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800">{client.name}</h1>
          <Button variant="outline" onClick={toggleDocumentViewer} className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            {documentViewerOpen ? "Hide Documents" : "View Documents"}
          </Button>
        </div>

        <ScrollArea className="flex-grow">
          <div className="space-y-6 pr-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <ClientDetails client={client} />
            </div>

            <div id="payment-form-section" className={documentViewerOpen ? "" : "px-[20%]"}>
              <Card className={`transition-all duration-300 ${editingPayment ? "border-amber-500 shadow-md" : ""}`}>
                <CardHeader className={`${editingPayment ? "bg-amber-50" : ""}`}>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-xl font-semibold text-gray-800">
                      {editingPayment ? "Edit Payment" : "Add Payment"}
                      <span className="ml-2 font-normal text-gray-600">- {client.name}</span>
                    </h2>
                  </div>
                  {editingPayment && (
                    <CardDescription>
                      Payment from {new Date(editingPayment.date).toLocaleDateString()}
                      {editingPayment.appliedPeriods && editingPayment.appliedPeriods.length > 0 && (
                        <span className="ml-2">(Split payment across {editingPayment.appliedPeriods.length} periods)</span>
                      )}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <PaymentForm
                    clientId={client.id}
                    initialData={
                      editingPayment
                        ? {
                            receivedDate: editingPayment.date,
                            appliedPeriod: editingPayment.appliedPeriods ? "multiple" : "single",
                            periodValue: editingPayment.period || "",
                            startPeriod: editingPayment.appliedPeriods?.[0]?.period || "",
                            endPeriod: editingPayment.appliedPeriods?.[editingPayment.appliedPeriods.length - 1]?.period || "",
                            aum: client.aum?.toString() || "",
                            amount: editingPayment.amount.toString(),
                            method: editingPayment.method || "",
                            notes: editingPayment.notes || "",
                            attachmentUrl: editingPayment.documentUrl || "",
                          }
                        : undefined
                    }
                    onCancel={handleCancelEdit}
                    isEditing={!!editingPayment}
                  />
                </CardContent>
              </Card>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Payment History</h2>
              <PaymentHistory
                payments={clientPayments}
                clients={allClients}
                onEdit={handleEditPayment}
                onViewDocument={handleViewDocument}
              />
            </div>
          </div>
        </ScrollArea>
      </div>

      {documentViewerOpen && (
        <div className="w-2/5">
          <DocumentViewer documentUrl={currentDocumentUrl} onClose={toggleDocumentViewer} className="h-full" />
        </div>
      )}
    </div>
  )
}

