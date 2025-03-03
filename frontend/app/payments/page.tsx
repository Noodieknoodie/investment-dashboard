"use client"
import { useState } from "react"
import { FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ClientDetails } from "./components/client-details"
import { PaymentForm } from "./components/payment-form"
import { PaymentHistory } from "./components/payment-history"
import { DocumentViewer } from "./components/document-viewer"
import type { Client, Payment } from "@/types"
// Sample payment data
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
  },
]
interface ClientPaymentPageProps {
  client: Client
  onViewDocument: (documentUrl: string) => void
  toggleDocumentViewer: () => void
  documentViewerOpen: boolean
}
export function ClientPaymentPage({
  client,
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
  // Helper function to ensure payment method is valid
  function validatePaymentMethod(method: string | undefined): import("@/types").PaymentMethodType {
    const validMethods = ["Check", "ACH", "Wire", "Credit Card"];
    return (method && validMethods.includes(method)) 
      ? method as import("@/types").PaymentMethodType
      : "Check"; // Default to Check if invalid or undefined
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
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <PaymentForm
                    clientId={client.id}
                    initialData={
                      editingPayment
                        ? {
                            date: editingPayment.date,
                            amount: editingPayment.amount,
                            method: validatePaymentMethod(editingPayment.method),
                            reference: editingPayment.reference,
                            notes: editingPayment.notes || "",
                            documentUrl: editingPayment.documentUrl,
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
export default function PaymentsPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Payment Management</h1>
      <div className="bg-white shadow-md rounded-lg p-6">
        <p className="text-gray-500">Payment management interface will be implemented here.</p>
        
        {/* Payment management content will go here */}
        {/* This is the most important part of the app according to requirements */}
      </div>
    </div>
  );
}