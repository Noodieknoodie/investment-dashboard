import { CalendarClock, CreditCard, AlertTriangle, CheckCircle, Clock, FileText } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Client } from "../../types"
import { FeeSummary } from "@/lib/api"

interface ClientDetailsProps {
  client: Client
  feeSummary?: FeeSummary | null
}

export function ClientDetails({ client, feeSummary }: ClientDetailsProps) {
  // Calculate expected fee (using fee summary if available)
  const expectedFee = feeSummary
    ? (client.paymentFrequency === "Monthly" ? feeSummary.monthly : feeSummary.quarterly) || 0
    : client.feeStructure === "Flat Rate"
      ? client.feeAmount || 0
      : client.aum && client.feePercentage
        ? (client.aum * (client.feePercentage / 100)) / (client.paymentFrequency === "Monthly" ? 12 : 4)
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
                <dd className="font-medium text-gray-900">${client.feeAmount?.toLocaleString() || "N/A"}</dd>
              </div>
            ) : (
              <div className="flex justify-between py-1">
                <dt className="text-gray-500">Fee Percentage</dt>
                <dd className="font-medium text-gray-900">{client.feePercentage?.toFixed(3) || "N/A"}%</dd>
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
                {client.aum ? `$${client.aum.toLocaleString()}` : "No AUM data available"}
              </dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-gray-500">Expected Fee</dt>
              <dd className="font-medium text-gray-900">
                {client.feeStructure === "Flat Rate" && client.feeAmount
                  ? `$${(client.feeAmount / (client.paymentFrequency === "Monthly" ? 12 : 4)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                  : client.aum && client.feePercentage
                    ? `$${((client.aum * (client.feePercentage / 100)) / (client.paymentFrequency === "Monthly" ? 12 : 4)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                    : client.lastPaymentAmount
                      ? `~$${client.lastPaymentAmount.toFixed(2)} (based on last payment)`
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
                      ? `Flat fee of $${client.feeAmount?.toLocaleString() || "N/A"}`
                      // FIXED: Better handling of missing AUM
                      : client.aum
                        ? `${client.feePercentage?.toFixed(3)}% of AUM ($${client.aum.toLocaleString()})`
                        : `${client.feePercentage?.toFixed(3)}% rate (no AUM data)`}
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

                {/* IMPROVED: Fee Reference Display */}
                {client.feeStructure === "Percentage of AUM" ? (
                  <>
                    {!client.aum && (
                      <div className="text-xs italic text-gray-500 mb-2">
                        No AUM data available. Based on rate only.
                      </div>
                    )}
                    <div className="grid grid-cols-1 gap-2 text-xs">
                      <div>
                        <span className="text-gray-500">Monthly:</span>
                        {client.aum && client.feePercentage ? (
                          <span className="font-medium ml-1">
                            ${((client.aum * (client.feePercentage / 100)) / 12).toFixed(2)}
                          </span>
                        ) : client.feePercentage ? (
                          <span className="font-medium ml-1">
                            {(client.feePercentage / 12).toFixed(4)}% × AUM
                          </span>
                        ) : (
                          <span className="font-medium ml-1">N/A</span>
                        )}
                      </div>
                      <div>
                        <span className="text-gray-500">Quarterly:</span>
                        {client.aum && client.feePercentage ? (
                          <span className="font-medium ml-1">
                            ${((client.aum * (client.feePercentage / 100)) / 4).toFixed(2)}
                          </span>
                        ) : client.feePercentage ? (
                          <span className="font-medium ml-1">
                            {(client.feePercentage / 4).toFixed(4)}% × AUM
                          </span>
                        ) : (
                          <span className="font-medium ml-1">N/A</span>
                        )}
                      </div>
                      <div>
                        <span className="text-gray-500">Annually:</span>
                        {client.aum && client.feePercentage ? (
                          <span className="font-medium ml-1">
                            ${(client.aum * (client.feePercentage / 100)).toFixed(2)}
                          </span>
                        ) : client.feePercentage ? (
                          <span className="font-medium ml-1">
                            {client.feePercentage.toFixed(4)}% × AUM
                          </span>
                        ) : (
                          <span className="font-medium ml-1">N/A</span>
                        )}
                      </div>
                    </div>
                  </>
                ) : (
                  client.feeAmount ? (
                    <div className="grid grid-cols-1 gap-2 text-xs">
                      <div>
                        <span className="text-gray-500">Monthly:</span>
                        <span className="font-medium ml-1">${(client.feeAmount / 12).toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Quarterly:</span>
                        <span className="font-medium ml-1">${(client.feeAmount / 4).toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Annually:</span>
                        <span className="font-medium ml-1">${client.feeAmount.toFixed(2)}</span>
                      </div>
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