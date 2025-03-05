import { CalendarClock, CreditCard, AlertTriangle, CheckCircle, Clock, FileText } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Client } from "../../types"
import { FeeSummary } from "@/lib/api"

interface ClientDetailsProps {
  client: Client
  feeSummary?: FeeSummary | null
}

export function ClientDetails({ client, feeSummary }: ClientDetailsProps) {
  // Calculate expected fee - use the value directly without adjustments
  // The backend already calculates this correctly for the payment frequency
  const expectedFee = feeSummary
    ? (client.paymentFrequency === "Monthly" ? feeSummary.monthly : feeSummary.quarterly) || 0
    : client.feeStructure === "Flat Rate"
      ? client.feeAmount || 0  // For flat rate, use the flat rate directly
      : client.aum && client.feePercentage
        ? (client.aum * (client.feePercentage / 100))  // For percentage, apply directly
        : 0

  // Format date
  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
    } catch (e) {
      return "Invalid date";
    }
  }

  // Calculate next payment date
  const calculateNextPaymentDate = () => {
    if (!client.lastPayment) return new Date();

    const lastPaymentDate = new Date(client.lastPayment)
    if (client.paymentFrequency === "Monthly") {
      return new Date(lastPaymentDate.setMonth(lastPaymentDate.getMonth() + 1))
    } else {
      return new Date(lastPaymentDate.setMonth(lastPaymentDate.getMonth() + 3))
    }
  }

  const nextPaymentDate = calculateNextPaymentDate()

  // Check if payment is overdue
  const isOverdue = nextPaymentDate < new Date()

  return (
    <>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-gray-800">Contract Details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 gap-1 text-sm">
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Contract Number</dt>
              <dd className="font-medium text-gray-900">{client.contractNumber || "N/A"}</dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Plan Provider</dt>
              <dd className="font-medium text-gray-900">{client.planProvider}</dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Payment Frequency</dt>
              <dd className="font-medium text-gray-900">{client.paymentFrequency}</dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Fee Structure</dt>
              <dd className="font-medium text-gray-900">{client.feeStructure}</dd>
            </div>
            {client.feeStructure === "Flat Rate" ? (
              <div className="flex justify-between py-1">
                <dt className="text-gray-500">Fee Amount</dt>
                <dd className="font-medium text-gray-900">${client.feeAmount?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || "N/A"}</dd>
              </div>
            ) : (
              <div className="flex justify-between py-1">
                <dt className="text-gray-500">Fee Percentage</dt>
                <dd className="font-medium text-gray-900">
                  <div className="inline-flex items-center bg-gray-100 rounded-lg overflow-hidden">
                    {client.paymentFrequency === "Monthly" ? (
                      <>
                        <span className="px-2 py-1 text-xs border-r border-gray-200">
                          M: {client.feePercentage?.toFixed(3)}%
                        </span>
                        <span className="px-2 py-1 text-xs border-r border-gray-200">
                          Q: {((client.feePercentage || 0) * 3).toFixed(3)}%
                        </span>
                        <span className="px-2 py-1 text-xs">
                          A: {((client.feePercentage || 0) * 12).toFixed(3)}%
                        </span>
                      </>
                    ) : (
                      <>
                        <span className="px-2 py-1 text-xs border-r border-gray-200">
                          M: {((client.feePercentage || 0) / 3).toFixed(3)}%
                        </span>
                        <span className="px-2 py-1 text-xs border-r border-gray-200">
                          Q: {client.feePercentage?.toFixed(3)}%
                        </span>
                        <span className="px-2 py-1 text-xs">
                          A: {((client.feePercentage || 0) * 4).toFixed(3)}%
                        </span>
                      </>
                    )}
                  </div>
                </dd>
              </div>
            )}
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-gray-800">Payment Information</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 gap-1 text-sm">
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">AUM</dt>
              <dd className="font-medium text-gray-900">
                {client.aum ? `$${client.aum.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : "No AUM data available"}
              </dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Expected Fee</dt>
              <dd className="font-medium text-gray-900">
                {client.feeStructure === "Flat Rate" && client.feeAmount
                  ? `$${client.feeAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                  : client.aum && client.feePercentage
                    ? `$${(client.aum * (client.feePercentage / 100)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                    : client.lastPaymentAmount
                      ? `~$${client.lastPaymentAmount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} (based on last payment)`
                      : "N/A"
                }
              </dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Last Payment</dt>
              <dd className="font-medium text-gray-900">{client.lastPayment ? formatDate(client.lastPayment) : "N/A"}</dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Last Payment Amount</dt>
              <dd className="font-medium text-gray-900">
                ${client.lastPaymentAmount.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Next Payment Due</dt>
              <dd className={`font-medium ${isOverdue ? "text-red-600" : "text-gray-900"}`}>
                {formatDate(nextPaymentDate.toISOString().split("T")[0])}
                {isOverdue && <span className="ml-2 text-red-600">(Overdue)</span>}
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-gray-800">Compliance Status</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Two-column layout container */}
          <div className="flex flex-col md:flex-row gap-4">
            {/* Left column - status indicator and general info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                {client.complianceStatus === "Compliant" ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : client.complianceStatus === "Review Needed" ? (
                  <Clock className="h-5 w-5 text-yellow-500" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                )}
                <span
                  className={`font-medium ${client.complianceStatus === "Compliant"
                    ? "text-green-700"
                    : client.complianceStatus === "Review Needed"
                      ? "text-yellow-700"
                      : "text-red-700"
                    }`}
                >
                  {client.complianceStatus}
                </span>
              </div>

              <div className="grid grid-cols-1 gap-3">
                <div className="flex items-center gap-2">
                  <CalendarClock className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    {client.paymentFrequency === "Monthly" ? "Monthly" : "Quarterly"} payment schedule
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    {client.feeStructure === "Flat Rate"
                      ? `Flat fee of $${client.feeAmount?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || "N/A"}`
                      : client.aum 
                        ? client.paymentFrequency === "Monthly"
                          ? `Annually: ${((client.feePercentage || 0) * 12).toFixed(3)}% ($${(client.aum * (client.feePercentage! / 100) * 12).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})`
                          : `Annually: ${((client.feePercentage || 0) * 4).toFixed(3)}% ($${(client.aum * (client.feePercentage! / 100) * 4).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})`
                        : client.paymentFrequency === "Monthly"
                          ? `Annually: ${((client.feePercentage || 0) * 12).toFixed(3)}% rate (no AUM data)`
                          : `Annually: ${((client.feePercentage || 0) * 4).toFixed(3)}% rate (no AUM data)`}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    Contract #{client.contractNumber || "N/A"}
                  </span>
                </div>
              </div>
            </div>

            {/* Right column - fee reference (stacked) */}
            <div className="md:w-2/5">
              <div className="bg-gray-50 rounded-md p-3">
                <h4 className="text-xs font-medium text-gray-500 mb-2">Fee Reference</h4>

                {/* FIXED: Fee Reference Display for Percentage of AUM */}
                {client.feeStructure === "Percentage of AUM" ? (
                  <>
                    {!client.aum && (
                      <div className="text-xs italic text-gray-500 mb-2">
                        No AUM data available. Based on rate only.
                      </div>
                    )}
                    <div className="grid grid-cols-1 gap-2 text-xs">
                      {/* Monthly display - base percentage rate for monthly, or divided by 3 for quarterly */}
                      <div>
                        <span className="text-gray-500">Monthly:</span>
                        {client.aum ? (
                          <span className="font-medium ml-1">
                            {client.paymentFrequency === "Monthly" 
                              ? client.feePercentage?.toFixed(4)
                              : ((client.feePercentage || 0) / 3).toFixed(4)}% (${(client.aum * (client.feePercentage! / 100) * (client.paymentFrequency === "Monthly" ? 1 : 1/3)).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})
                          </span>
                        ) : (
                          <span className="font-medium ml-1">
                            {client.paymentFrequency === "Monthly" 
                              ? client.feePercentage?.toFixed(4)
                              : ((client.feePercentage || 0) / 3).toFixed(4)}%
                          </span>
                        )}
                      </div>
                      
                      {/* Quarterly display - 3x the monthly percentage, or base rate for quarterly */}
                      <div>
                        <span className="text-gray-500">Quarterly:</span>
                        {client.aum ? (
                          <span className="font-medium ml-1">
                            {client.paymentFrequency === "Monthly" 
                              ? ((client.feePercentage || 0) * 3).toFixed(4) 
                              : client.feePercentage?.toFixed(4)}% (${(client.aum * (client.feePercentage! / 100) * (client.paymentFrequency === "Monthly" ? 3 : 1)).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})
                          </span>
                        ) : (
                          <span className="font-medium ml-1">
                            {client.paymentFrequency === "Monthly" 
                              ? ((client.feePercentage || 0) * 3).toFixed(4) 
                              : client.feePercentage?.toFixed(4)}% {client.paymentFrequency === "Monthly" ? "× 3 months" : ""}
                          </span>
                        )}
                      </div>
                      
                      {/* Annual display - 12x the monthly or 4x the quarterly */}
                      <div>
                        <span className="text-gray-500">Annually:</span>
                        {client.aum ? (
                          <span className="font-medium ml-1">
                            {client.paymentFrequency === "Monthly" 
                              ? ((client.feePercentage || 0) * 12).toFixed(4) 
                              : ((client.feePercentage || 0) * 4).toFixed(4)}% (${(client.aum * (client.feePercentage! / 100) * (client.paymentFrequency === "Monthly" ? 12 : 4)).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})})
                          </span>
                        ) : (
                          <span className="font-medium ml-1">
                            {client.paymentFrequency === "Monthly" 
                              ? ((client.feePercentage || 0) * 12).toFixed(4) 
                              : ((client.feePercentage || 0) * 4).toFixed(4)}% {client.paymentFrequency === "Monthly" ? "× 12 months" : "× 4 quarters"}
                          </span>
                        )}
                      </div>
                    </div>
                  </>
                ) : (
                  client.feeAmount ? (
                    <div className="grid grid-cols-1 gap-2 text-xs">
                      {/* For Flat Rate, show the correct fee based on payment schedule */}
                      {client.paymentFrequency === "Monthly" ? (
                        <>
                          {/* If Monthly payment schedule */}
                          <div>
                            <span className="text-gray-500">Monthly:</span>
                            <span className="font-medium ml-1">${client.feeAmount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Quarterly:</span>
                            <span className="font-medium ml-1">${(client.feeAmount * 3).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Annually:</span>
                            <span className="font-medium ml-1">${(client.feeAmount * 12).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                          </div>
                        </>
                      ) : (
                        <>
                          {/* If Quarterly payment schedule */}
                          <div>
                            <span className="text-gray-500">Monthly:</span>
                            <span className="font-medium ml-1">${(client.feeAmount / 3).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Quarterly:</span>
                            <span className="font-medium ml-1">${client.feeAmount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Annually:</span>
                            <span className="font-medium ml-1">${(client.feeAmount * 4).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <div className="text-xs text-gray-500">
                      Flat fee information not available
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  )
}