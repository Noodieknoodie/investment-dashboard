export interface Client {
  id: string
  name: string
  planProvider: string
  paymentFrequency: "Monthly" | "Quarterly"
  feeStructure: "Flat Rate" | "Percentage of AUM"
  feeAmount?: number
  feePercentage?: number
  aum?: number
  lastPayment: string
  lastPaymentAmount: number
  complianceStatus: "Compliant" | "Review Needed" | "Payment Overdue"
}

export interface Payment {
  id: string
  clientId: string
  date: string
  amount: number
  method: "Check" | "ACH" | "Wire" | "Credit Card"
  reference: string
  notes?: string
  documentUrl?: string
  status: "Pending" | "Processed" | "Failed"
}

export interface PaymentFormData {
  date: string
  amount: number
  method: "Check" | "ACH" | "Wire" | "Credit Card"
  reference: string
  notes?: string
  documentUrl?: string
}

