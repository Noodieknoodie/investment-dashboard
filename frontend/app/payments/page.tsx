"use client"

import { useState, useEffect } from "react"
import { ClientSidebar } from "./client-sidebar"
import { ClientPaymentPage } from "./client-payment-page"
import { useClientData, mapComplianceStatus } from "@/hooks/use-client-data"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

export default function PaymentsPage() {
    const {
        clients,
        clientsByProvider,
        selectedClient,
        complianceStatuses,
        isLoading,
        error,
        selectClient
    } = useClientData()

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

    // Map the API clients to the UI client format
    const mappedClients = clients.map(client => {
        const complianceStatus = complianceStatuses[client.client_id] || { status: 'yellow', reason: 'Unknown status' };
        return {
            id: client.client_id.toString(),
            name: client.display_name,
            planProvider: clientsByProvider.find(g =>
                g.clients.some(c => c.client_id === client.client_id)
            )?.provider || "Unknown",
            paymentFrequency: "Quarterly" as "Monthly" | "Quarterly",
            feeStructure: "Flat Rate" as "Flat Rate" | "Percentage of AUM",
            aum: 0, // Will be updated in client details
            lastPayment: "", // Will be updated in client details
            lastPaymentAmount: 0, // Will be updated in client details
            complianceStatus: mapComplianceStatus(complianceStatus),
            contractNumber: "" // Will be updated in client details
        };
    });

    const handleSelectClient = (clientId: string) => {
        selectClient(parseInt(clientId, 10));
    };

    return (
        <div className="flex flex-1 overflow-hidden">
            {isLoading ? (
                // Loading state
                <div className="w-80 border-r border-gray-200 bg-white">
                    <div className="p-4 border-b border-gray-200">
                        <div className="h-8 w-40 bg-gray-200 rounded mb-4"></div>
                        <Skeleton className="h-10 w-full mb-4" />
                        <div className="flex items-center justify-between">
                            <Skeleton className="h-5 w-32" />
                            <Skeleton className="h-5 w-10" />
                        </div>
                    </div>
                    <div className="p-2">
                        {[1, 2, 3, 4, 5].map((i) => (
                            <Skeleton key={i} className="h-10 w-full mb-1" />
                        ))}
                    </div>
                </div>
            ) : (
                <ClientSidebar
                    clients={mappedClients}
                    selectedClient={selectedClient ? {
                        id: selectedClient.client_id.toString(),
                        name: selectedClient.display_name,
                        planProvider: clientsByProvider.find(g =>
                            g.clients.some(c => c.client_id === selectedClient.client_id)
                        )?.provider || "Unknown",
                        paymentFrequency: "Quarterly" as "Monthly" | "Quarterly",
                        feeStructure: "Flat Rate" as "Flat Rate" | "Percentage of AUM",
                        aum: 0, // Placeholder
                        lastPayment: "", // Placeholder
                        lastPaymentAmount: 0, // Placeholder
                        complianceStatus: mapComplianceStatus(
                            complianceStatuses[selectedClient.client_id] || { status: 'yellow', reason: 'Unknown status' }
                        ),
                        contractNumber: "" // Placeholder
                    } : null}
                    onSelectClient={(client) => handleSelectClient(client.id)}
                />
            )}

            <main className="flex-1 overflow-hidden p-6">
                {error ? (
                    <Alert variant="destructive" className="mb-6">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                            {error.message || "Failed to load client data. Please try again."}
                        </AlertDescription>
                    </Alert>
                ) : null}

                {selectedClient ? (
                    <ClientPaymentPage
                        clientId={selectedClient.client_id}
                        complianceStatus={complianceStatuses[selectedClient.client_id] || { status: 'yellow', reason: 'Unknown status' }}
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
    )
}