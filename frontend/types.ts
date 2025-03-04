export interface Client {
  id: string
  name: string
  email?: string
  phone?: string
  companyId?: string
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
  status: 'pending' | 'completed' | 'failed' | 'Processed' | 'Pending'
  description?: string
  paymentMethod?: string
  method?: PaymentMethodType | string
  reference?: string
  notes?: string
  documentUrl?: string
  period?: string
  appliedPeriods?: PaymentPeriod[]
  expectedFee?: number
  // Added properties for split payments
  isSplitPayment?: boolean
  splitGroupId?: string
  aum?: number
}

export interface PaymentFormData {
  date?: string
  receivedDate: string
  amount: number | string
  method: PaymentMethodType | string
  reference?: string
  notes: string
  documentUrl?: string
  attachmentUrl?: string
  appliedPeriod: string
  periodValue: string
  startPeriod: string
  endPeriod: string
  aum: string
}