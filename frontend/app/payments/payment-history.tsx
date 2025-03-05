"use client"
import React, { useState } from "react"
import { ChevronDown, ChevronRight, Edit, FileText, MoreHorizontal, Trash2, Loader2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { useToast } from "@/hooks/use-toast"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import type { Client, Payment, PaymentPeriod } from "@/types"

interface PaymentHistoryProps {
  payments: Payment[]
  client: Client | null
  onEdit: (payment: Payment) => void
  onDelete: (paymentId: string) => Promise<boolean>
  onViewDocument: (documentUrl: string) => void
  isLoading?: boolean
}

export function PaymentHistory({
  payments,
  client,
  onEdit,
  onDelete,
  onViewDocument,
  isLoading = false
}: PaymentHistoryProps) {
  const { toast } = useToast();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [paymentToDelete, setPaymentToDelete] = useState<Payment | null>(null)
  const [expandedPayments, setExpandedPayments] = useState<string[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deletingSplitGroup, setDeletingSplitGroup] = useState(false)
  const [splitGroupToDelete, setSplitGroupToDelete] = useState<string | null>(null)
  const [splitGroupPaymentCount, setSplitGroupPaymentCount] = useState(0)
  const rowsPerPage = 20

  // Pagination
  const totalPages = Math.ceil(payments.length / rowsPerPage)
  const paginatedPayments = payments.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  )

  const handleDeleteClick = (payment: Payment) => {
    if (payment.isSplitPayment) {
      setSplitGroupToDelete(payment.id || null);
      setSplitGroupPaymentCount(payment.appliedPeriods?.length || 0);
      setDeletingSplitGroup(true);
    } else {
      setPaymentToDelete(payment);
      setDeletingSplitGroup(false);
    }
    setDeleteDialogOpen(true);
  }

  const handleConfirmDelete = async () => {
    setIsDeleting(true);

    try {
      let success = false;

      if (deletingSplitGroup && splitGroupToDelete) {
        // Delete the payment directly since we now have a single record for split payments
        success = await onDelete(splitGroupToDelete);
      } else if (paymentToDelete) {
        success = await onDelete(paymentToDelete.id);
      }

      if (success) {
        toast({
          title: "Payment Deleted",
          description: deletingSplitGroup
            ? `All ${splitGroupPaymentCount} payments in this group have been deleted.`
            : "The payment has been successfully deleted.",
        });
      } else {
        toast({
          title: "Deletion Failed",
          description: "Failed to delete the payment. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error deleting payment:", error);
      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setDeleteDialogOpen(false);
      setPaymentToDelete(null);
      setSplitGroupToDelete(null);
      setDeletingSplitGroup(false);
      setIsDeleting(false);
    }
  }

  const toggleExpand = (paymentId: string) => {
    setExpandedPayments(prev =>
      prev.includes(paymentId)
        ? prev.filter(id => id !== paymentId)
        : [...prev, paymentId]
    )
  }

  // Use different thresholds to determine how to display fee differences
  // - Exact match: Blue (extremely rare in percentage-based fees)
  // - Within 5% difference: Green with checkmark (acceptable variance)
  // - Within 5-15% difference: Yellow (borderline acceptable)
  // - Beyond 15% difference: Red (significant variance that needs attention)
  
  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
  }

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount)
  }

  if (isLoading) {
    return (
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-8"></TableHead>
              <TableHead>Received Date</TableHead>
              <TableHead>Provider</TableHead>
              <TableHead>Applied Period</TableHead>
              <TableHead>AUM</TableHead>
              <TableHead>Payment Schedule</TableHead>
              <TableHead>Fee Structure</TableHead>
              <TableHead>Expected Fee</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Remainder</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[1, 2, 3, 4, 5].map((i) => (
              <TableRow key={i}>
                <TableCell className="p-2"></TableCell>
                <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                <TableCell><Skeleton className="h-5 w-24" /></TableCell>
                <TableCell className="text-right"><Skeleton className="h-8 w-8 rounded-full ml-auto" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-8"></TableHead>
              <TableHead>Received Date</TableHead>
              <TableHead>Provider</TableHead>
              <TableHead>Applied Period</TableHead>
              <TableHead>AUM</TableHead>
              <TableHead>Payment Schedule</TableHead>
              <TableHead>Fee Structure</TableHead>
              <TableHead>Expected Fee</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Remainder</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedPayments.length > 0 ? (
              paginatedPayments.map((payment) => {
                const isSplitPayment = payment.isSplitPayment && payment.appliedPeriods && payment.appliedPeriods.length > 0;
                const isExpanded = expandedPayments.includes(payment.id);

                return (
                  <React.Fragment key={payment.id}>
                    <TableRow className={isExpanded ? "bg-gray-50" : ""}>
                      <TableCell className="p-2">
                        {isSplitPayment && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => toggleExpand(payment.id)}
                          >
                            {isExpanded ?
                              <ChevronDown className="h-4 w-4" /> :
                              <ChevronRight className="h-4 w-4" />
                            }
                          </Button>
                        )}
                      </TableCell>
                      <TableCell>{formatDate(payment.date)}</TableCell>
                      <TableCell>{client?.planProvider || "N/A"}</TableCell>
                      <TableCell>
                        {isSplitPayment ? (
                          <div className="flex items-center">
                            <Badge variant="outline" className="font-normal">
                              Split
                            </Badge>
                            <span className="ml-2">
                              {payment.appliedPeriods?.length || 0} periods
                            </span>
                          </div>
                        ) : (
                          payment.period || "N/A"
                        )}
                      </TableCell>
                      <TableCell>
                        {payment.aum ? formatCurrency(payment.aum) : "No AUM data"}
                      </TableCell>
                      <TableCell>{client?.paymentFrequency || "N/A"}</TableCell>
                      <TableCell>
                        {client?.feeStructure === "Flat Rate"
                          ? "Flat Rate"
                          : client?.feePercentage
                            ? `${client.feePercentage.toFixed(3)}% of AUM`
                            : "N/A"
                        }
                      </TableCell>
                      <TableCell>
                        {/* FIXED: Expected Fee Display - remove incorrect division */}
                        {payment.expectedFee ? formatCurrency(payment.expectedFee) :
                          payment.aum && client?.feePercentage
                            ? formatCurrency(payment.aum * (client.feePercentage / 100))
                            : (
                              <span className="text-muted-foreground">
                                ~{formatCurrency(payment.amount)}
                                <span className="text-xs block">(based on payment)</span>
                              </span>
                            )
                        }
                      </TableCell>
                      <TableCell>
                        {formatCurrency(payment.amount)}
                        {isSplitPayment && !isExpanded && (
                          <div className="text-xs text-muted-foreground">
                            Click to view details
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        {(() => {
                          // Use the same expected fee calculation as in the expected fee column
                          const effectiveExpectedFee = payment.expectedFee !== undefined && payment.expectedFee !== null
                            ? payment.expectedFee
                            : payment.aum && client?.feePercentage
                              ? payment.aum * (client.feePercentage / 100)
                              : null;
                          
                          if (effectiveExpectedFee === null) {
                            return (
                              <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                Cannot calculate
                              </span>
                            );
                          }
                          
                          const difference = payment.amount - effectiveExpectedFee;
                          const percentDifference = (difference / effectiveExpectedFee) * 100;
                          const absPercentDifference = Math.abs(percentDifference);
                          
                          // Determine style based on difference percentage
                          const badgeClass = payment.amount === effectiveExpectedFee
                            ? "bg-blue-100 text-blue-800"
                            : absPercentDifference <= 5
                              ? "bg-green-100 text-green-800"
                              : absPercentDifference <= 15
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-red-100 text-red-800";
                          
                          return (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${badgeClass}`}>
                              {payment.amount === effectiveExpectedFee
                                ? "Exact Match"
                                : payment.amount > effectiveExpectedFee
                                  ? `+${formatCurrency(difference)}`
                                  : `-${formatCurrency(Math.abs(difference))}`
                              }
                              {effectiveExpectedFee > 0 && payment.amount !== effectiveExpectedFee && (
                                <span className="ml-1">
                                  ({absPercentDifference.toFixed(1)}%)
                                  {absPercentDifference <= 5 && payment.amount !== effectiveExpectedFee && " ✓"}
                                </span>
                              )}
                            </span>
                          );
                        })()}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Actions</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => onEdit(payment)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            {payment.documentUrl && (
                              <DropdownMenuItem onClick={() => onViewDocument(payment.documentUrl!)}>
                                <FileText className="mr-2 h-4 w-4" />
                                View Document
                              </DropdownMenuItem>
                            )}
                            <DropdownMenuItem className="text-red-600" onClick={() => handleDeleteClick(payment)}>
                              <Trash2 className="mr-2 h-4 w-4" />
                              {isSplitPayment ? "Delete Split Payment" : "Delete"}
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>

                    {/* Expandable detail rows for split payments */}
                    {isExpanded && isSplitPayment && payment.appliedPeriods?.map((periodData: PaymentPeriod, index: number) => (
                      <TableRow key={`${payment.id}-period-${index}`} className="bg-gray-50 border-t border-gray-100">
                        <TableCell></TableCell>
                        <TableCell></TableCell>
                        <TableCell></TableCell>
                        <TableCell className="pl-8 text-sm text-gray-600">
                          {periodData.period}
                        </TableCell>
                        <TableCell></TableCell>
                        <TableCell></TableCell>
                        <TableCell></TableCell>
                        <TableCell></TableCell>
                        <TableCell className="text-sm font-medium text-gray-700">
                          {periodData.amount !== undefined ? formatCurrency(periodData.amount) : '-'}
                        </TableCell>
                        <TableCell>
                          {/* No remainder calculation needed for individual split payment periods */}
                          <span className="text-xs text-gray-500">Part of split</span>
                        </TableCell>
                        <TableCell></TableCell>
                      </TableRow>
                    ))}
                  </React.Fragment>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={11} className="text-center py-6 text-gray-500">
                  No payment history available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination controls */}
      {payments.length > rowsPerPage && (
        <div className="flex items-center justify-end space-x-2 py-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
          >
            &lt;&lt;
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            &lt;
          </Button>
          <span className="text-sm text-gray-600">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            &gt;
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage === totalPages}
          >
            &gt;&gt;
          </Button>
        </div>
      )}

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {deletingSplitGroup
                ? "Delete Split Payment Group?"
                : "Delete Payment?"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {deletingSplitGroup ? (
                <div>
                  <p>
                    This will permanently delete all {splitGroupPaymentCount} payments in this split payment group.
                    This action cannot be undone.
                  </p>
                </div>
              ) : (
                <p>
                  This will permanently delete the payment record from{" "}
                  {paymentToDelete ? formatDate(paymentToDelete.date) : ""}
                  for {paymentToDelete ? formatCurrency(paymentToDelete.amount) : "$0.00"}. This action cannot be undone.
                </p>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-red-600 hover:bg-red-700"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                deletingSplitGroup ? "Delete All" : "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}