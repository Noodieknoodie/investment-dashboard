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

export interface Payment {
  id: string
  clientId: string
  amount: number
  date: string
  status: 'pending' | 'completed' | 'failed' | 'Processed' | 'Pending'
  description?: string
  paymentMethod?: string
  method?: string
  reference?: string
  notes?: string
  documentUrl?: string
}

export interface PaymentFormData {
  date: string
  amount: number
  method: "Check" | "ACH" | "Wire" | "Credit Card"
  reference: string
  notes?: string
  documentUrl?: string
}

export type PaymentMethodType = "Check" | "ACH" | "Wire" | "Credit Card"

export interface PaymentFormData {
  date: string
  amount: number
  method: PaymentMethodType
  reference?: string
  notes: string
  documentUrl?: string
}

export interface Payment {
  id: string
  clientId: string
  amount: number
  date: string
  status: 'pending' | 'completed' | 'failed' | 'Processed' | 'Pending'
  description?: string
  paymentMethod?: string
  method?: PaymentMethodType
  reference?: string
  notes?: string
  documentUrl?: string
}