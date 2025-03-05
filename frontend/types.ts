export interface Client {
  id: string
  name: string
  email?: string
  phone?: string
  planProvider: string
  paymentFrequency: "Monthly" | "Quarterly"
  feeStructure: "Flat Rate" | "Percentage of AUM"
  feeAmount?: number
  feePercentage?: number
  aum?: number
  lastPayment: string
  lastPaymentAmount: number
  complianceStatus: "Compliant" | "Review Needed" | "Payment Overdue"
  contractNumber?: string
}

export type PaymentMethodType = "Check" | "ACH" | "Wire" | "Credit Card"

export type PaymentPeriod = {
  period: string;
  amount?: number;
}

export interface Payment {
  id: string
  clientId: string
  amount: number
  date: string
  status: 'Processed' | 'Pending'
  description?: string
  method?: PaymentMethodType | string
  notes?: string
  documentUrl?: string
  period?: string
  appliedPeriods?: PaymentPeriod[]
  expectedFee?: number
  // Flag for split payments (determined by different start/end periods)
  isSplitPayment?: boolean
  aum?: number
}

export interface PaymentFormData {
  receivedDate: string
  amount: number | string
  method: PaymentMethodType | string
  notes: string
  documentUrl?: string
  attachmentUrl?: string
  appliedPeriod: string
  periodValue: string
  startPeriod: string
  endPeriod: string
  aum: string
}