"use client"

import { useState, useEffect } from "react"
import { FileText, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ClientDetails } from "./client-details"
import { PaymentForm } from "./payment-form"
import { PaymentHistory } from "./payment-history"
import { DocumentViewer } from "@/components/document-viewer"
import { useClientSnapshot } from "@/hooks/use-client-snapshot"
import { usePayments, usePaymentDetails } from "@/hooks/use-payments"
import { mapComplianceStatus } from "@/hooks/use-client-data"
import { mapClientSnapshotToUI, mapPaymentToUI } from "@/lib/mappers"
import { ComplianceStatus } from "@/lib/api"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import type { Payment } from "@/types"
import { toast } from "@/components/ui/use-toast"

interface ClientPaymentPageProps {
  clientId: number
  complianceStatus: ComplianceStatus
  onViewDocument: (documentUrl: string) => void
  toggleDocumentViewer: () => void
  documentViewerOpen: boolean
}

export function ClientPaymentPage({
  clientId,
  complianceStatus,
  onViewDocument,
  toggleDocumentViewer,
  documentViewerOpen,
}: ClientPaymentPageProps) {
  // Get client snapshot data
  const {
    clientSnapshot,
    feeSummary,
    isLoading: isClientLoading,
    error: clientError
  } = useClientSnapshot(clientId);

  // Get payments for this client
  const {
    payments,
    isLoading: isPaymentsLoading,
    error: paymentsError,
    createPayment,
    updatePayment,
    deletePayment,
    refreshPayments
  } = usePayments(clientId);

  // State for payment editing
  const [editingPaymentId, setEditingPaymentId] = useState<number | null>(null);
  const [currentDocumentUrl, setCurrentDocumentUrl] = useState<string | null>(null);

  // Fetch payment details when editing
  const {
    payment: editingPayment,
    isLoading: isPaymentDetailLoading,
    error: paymentDetailError
  } = usePaymentDetails(editingPaymentId);

  // Map backend data to UI format
  const uiClient = clientSnapshot ? mapClientSnapshotToUI(clientSnapshot, complianceStatus) : null;
  const uiPayments = payments.map(payment => mapPaymentToUI(payment));
  
  // Use the first contract from the client's contracts
  const activeContract = clientSnapshot?.contracts?.[0] || null;

  // Simple approach: only render the form when we have real data
  const hasValidContractData = clientSnapshot && activeContract;

  // #####################################################
  // CRITICAL DEBUGGING FOR CLIENT/CONTRACT RELATIONSHIPS
  // #####################################################
  useEffect(() => {
    if (clientId) {
      console.log(`🔄 [DEBUG] Client changed to: ${clientId}`);
    }
  }, [clientId]);

  useEffect(() => {
    if (activeContract) {
      console.log(`🔄 [DEBUG] Contract changed to: ${activeContract.contract_id} (belongs to client ${activeContract.client_id})`);
      
      // Check if there's a mismatch
      if (activeContract.client_id !== clientId) {
        console.error(`⚠️ [CRITICAL ERROR] Contract belongs to client ${activeContract.client_id} but we're in client ${clientId} context!`);
      }
    }
  }, [activeContract, clientId]);

  useEffect(() => {
    if (clientSnapshot) {
      console.log(`🔄 [DEBUG] Client snapshot loaded: ${clientSnapshot.client.client_id}`);
      
      if (clientSnapshot.contracts && clientSnapshot.contracts.length > 0) {
        console.log(`🔄 [DEBUG] Contracts available: ${clientSnapshot.contracts.map(c => c.contract_id).join(', ')}`);
      } else {
        console.warn(`⚠️ [WARNING] No contracts found for client ${clientSnapshot.client.client_id}`);
      }
    }
  }, [clientSnapshot]);
  // #####################################################

  // Reset editing state when clientId changes
  useEffect(() => {
    if (editingPaymentId) {
      setEditingPaymentId(null);
    }
  }, [clientId]);

  // Handle edit payment
  const handleEditPayment = (payment: Payment) => {
    setEditingPaymentId(parseInt(payment.id, 10));
    // Scroll to the payment form
    document.getElementById("payment-form-section")?.scrollIntoView({ behavior: "smooth" });
  }

  const handleCancelEdit = () => {
    setEditingPaymentId(null);
  }

  const handleViewDocument = (documentUrl: string) => {
    setCurrentDocumentUrl(documentUrl);
    onViewDocument(documentUrl);
  }

  // Handle delete payment (updated for revised split payment implementation)
  const handleDeletePayment = async (paymentId: string) => {
    try {
      const numericPaymentId = parseInt(paymentId, 10);
      const success = await deletePayment(numericPaymentId);
      return success;
    } catch (error) {
      console.error("Error deleting payment:", error);
      return false;
    }
  };

  // Map form submission to API call
  const handleCreatePayment = async (formData: any) => {
    try {
      const isSplitPayment = formData.appliedPeriod === "multiple";

      await createPayment({
        client_id: clientId,
        contract_id: activeContract?.contract_id as number,
        received_date: formData.receivedDate,
        total_assets: formData.aum ? parseInt(formData.aum, 10) : undefined,
        actual_fee: parseFloat(formData.amount),
        method: formData.method,
        notes: formData.notes,
        is_split_payment: isSplitPayment,
        start_period: parseInt(formData.startPeriod?.split('-')[0] || "1", 10),
        start_period_year: parseInt(formData.startPeriod?.split('-')[1] || new Date().getFullYear().toString(), 10),
        end_period: isSplitPayment ? parseInt(formData.endPeriod?.split('-')[0], 10) : undefined,
        end_period_year: isSplitPayment ? parseInt(formData.endPeriod?.split('-')[1], 10) : undefined
      });

      // Refresh payments
      await refreshPayments();

      return true;
    } catch (error) {
      console.error("Error creating payment:", error);
      return false;
    }
  };

  const handleUpdatePayment = async (formData: any) => {
    if (!editingPaymentId) return false;

    // Check if they're trying to change split payment settings
    const isCurrentlySplit = editingPayment?.is_split_payment;
    const wantsToBeSplit = formData.appliedPeriod === "multiple";
    
    // Check if they're trying to change periods
    const currentStartPeriod = editingPayment?.applied_start_quarter 
      ? `${editingPayment.applied_start_quarter}-${editingPayment.applied_start_quarter_year}`
      : editingPayment?.applied_start_month 
        ? `${editingPayment.applied_start_month}-${editingPayment.applied_start_month_year}` 
        : "";
    
    const currentEndPeriod = editingPayment?.applied_end_quarter 
      ? `${editingPayment.applied_end_quarter}-${editingPayment.applied_end_quarter_year}` 
      : editingPayment?.applied_end_month 
        ? `${editingPayment.applied_end_month}-${editingPayment.applied_end_month_year}` 
        : "";
    
    // If trying to change split state or periods, warn user
    if (isCurrentlySplit !== wantsToBeSplit || 
        (isCurrentlySplit && wantsToBeSplit && 
         (formData.startPeriod !== currentStartPeriod || formData.endPeriod !== currentEndPeriod)) ||
        (!isCurrentlySplit && !wantsToBeSplit && formData.periodValue !== currentStartPeriod)) {
      
      const confirmDelete = window.confirm(
        "Changing payment periods requires deleting and recreating the payment. " +
        "Would you like to delete this payment and create a new one with the updated periods?"
      );
      
      if (confirmDelete) {
        // Delete current payment
        const deleteSuccess = await deletePayment(editingPaymentId);
        
        if (!deleteSuccess) {
          toast({
            title: "Error",
            description: "Failed to delete the original payment. Please try again.",
            variant: "destructive",
          });
          return false;
        }
        
        // Create new payment with updated data
        const createSuccess = await handleCreatePayment(formData);
        
        // Reset editing state
        setEditingPaymentId(null);
        
        return createSuccess;
      } else {
        return false;
      }
    }

    try {
      await updatePayment(editingPaymentId, {
        received_date: formData.receivedDate,
        total_assets: formData.aum ? parseInt(formData.aum, 10) : undefined,
        actual_fee: parseFloat(formData.amount),
        method: formData.method,
        notes: formData.notes
      });

      // Refresh payments
      await refreshPayments();

      // Reset editing state
      setEditingPaymentId(null);

      return true;
    } catch (error) {
      console.error("Error updating payment:", error);
      return false;
    }
  };

  // Show loading state
  if (isClientLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between mb-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-10 w-32" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-5 w-32 mb-2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {[1, 2, 3, 4].map(j => (
                    <div key={j} className="flex justify-between">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-32" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
              <Skeleton className="h-20 w-full" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show error state
  if (clientError || !clientSnapshot) {
    return (
      <Alert variant="destructive" className="mb-6">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {(clientError as Error)?.message || "Failed to load client data. Please try again."}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className={`flex h-full ${documentViewerOpen ? "space-x-4" : ""}`}>
      <div className={`flex flex-col overflow-hidden ${documentViewerOpen ? "w-3/5" : "w-full"}`}>
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800">{clientSnapshot.client.display_name}</h1>
          <Button variant="outline" onClick={toggleDocumentViewer} className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            {documentViewerOpen ? "Hide Documents" : "View Documents"}
          </Button>
        </div>

        {clientError && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {(clientError as Error)?.message || "Failed to load client data. Please try again."}
            </AlertDescription>
          </Alert>
        )}

        {paymentsError && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {paymentsError.message || "Failed to load payment data. Please try again."}
            </AlertDescription>
          </Alert>
        )}

        <ScrollArea className="flex-grow">
          <div className="space-y-6 pr-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {uiClient && (
                <ClientDetails
                  client={uiClient}
                  feeSummary={feeSummary}
                />
              )}
            </div>

            <div id="payment-form-section" className={documentViewerOpen ? "" : "px-[20%]"}>
              <Card className={`transition-all duration-300 ${editingPaymentId ? "border-amber-500 shadow-md" : ""}`}>
                <CardHeader className={`${editingPaymentId ? "bg-amber-50" : ""}`}>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-xl font-semibold text-gray-800">
                      {editingPaymentId ? "Edit Payment" : "Add Payment"}
                      <span className="ml-2 font-normal text-gray-600">- {clientSnapshot.client.display_name}</span>
                    </h2>
                  </div>
                  {editingPayment && (
                    <CardDescription>
                      Payment from {new Date(editingPayment.received_date).toLocaleDateString()}
                      {editingPayment.is_split_payment && (
                        <span className="ml-2">(Split payment)</span>
                      )}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  {!hasValidContractData ? (
                    <div className="flex justify-center items-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-primary" />
                      <span className="ml-3 text-sm text-gray-500">
                        {isClientLoading ? "Loading client data..." : "No valid contract found"}
                      </span>
                    </div>
                  ) : (
                    <PaymentForm
                      key={`payment-form-${clientId}-${activeContract?.contract_id}`}
                      clientId={clientId.toString()}
                      contractId={String(activeContract?.contract_id)}
                      initialData={
                        editingPayment
                          ? {
                            receivedDate: editingPayment.received_date,
                            appliedPeriod: editingPayment.is_split_payment ? "multiple" : "single",
                            periodValue: editingPayment.applied_start_quarter
                              ? `${editingPayment.applied_start_quarter}-${editingPayment.applied_start_quarter_year}`
                              : editingPayment.applied_start_month
                                ? `${editingPayment.applied_start_month}-${editingPayment.applied_start_month_year}`
                                : "",
                            startPeriod: editingPayment.applied_start_quarter
                              ? `${editingPayment.applied_start_quarter}-${editingPayment.applied_start_quarter_year}`
                              : editingPayment.applied_start_month
                                ? `${editingPayment.applied_start_month}-${editingPayment.applied_start_month_year}`
                                : "",
                            endPeriod: editingPayment.applied_end_quarter
                              ? `${editingPayment.applied_end_quarter}-${editingPayment.applied_end_quarter_year}`
                              : editingPayment.applied_end_month
                                ? `${editingPayment.applied_end_month}-${editingPayment.applied_end_month_year}`                              : "",
                            aum: editingPayment.total_assets?.toString() || "",
                            amount: editingPayment.actual_fee.toString(),
                            method: editingPayment.method || "",
                            notes: editingPayment.notes || "",
                            attachmentUrl: "", // We'll handle this separately
                          }
                          : undefined
                      }
                      onCancel={handleCancelEdit}
                      onSubmit={editingPaymentId ? handleUpdatePayment : handleCreatePayment}
                      isEditing={!!editingPaymentId}
                      isLoading={isPaymentDetailLoading}
                    />
                  )}
                </CardContent>
              </Card>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Payment History</h2>
              <PaymentHistory
                payments={uiPayments}
                client={uiClient}
                onEdit={handleEditPayment}
                onDelete={handleDeletePayment}
                onViewDocument={handleViewDocument}
                isLoading={isPaymentsLoading}
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
