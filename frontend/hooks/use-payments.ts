// frontend/hooks/use-payments.ts
import { useState, useEffect } from 'react';
import { paymentApi, Payment, PaymentWithDetails, PaymentCreate, PaymentUpdate } from '@/lib/api';

interface UsePaymentsReturn {
  payments: Payment[];
  isLoading: boolean;
  error: Error | null;
  createPayment: (data: PaymentCreate) => Promise<Payment>;
  updatePayment: (paymentId: number, data: PaymentUpdate) => Promise<Payment>;
  deletePayment: (paymentId: number) => Promise<boolean>;
  refreshPayments: () => Promise<void>;
}

export function usePayments(clientId: number | null): UsePaymentsReturn {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const loadPayments = async () => {
    if (!clientId) {
      setPayments([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const paymentsData = await paymentApi.getClientPayments(clientId);
      setPayments(paymentsData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load payments'));
      console.error('Error loading payments:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load payments when clientId changes
  useEffect(() => {
    loadPayments();
  }, [clientId]);

  // Create a new payment
  const createPayment = async (data: PaymentCreate): Promise<Payment> => {
    try {
      const newPayment = await paymentApi.createPayment(data);
      await loadPayments(); // Refresh the payments list
      return newPayment;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to create payment');
      setError(error);
      throw error;
    }
  };

  // Update an existing payment
  const updatePayment = async (paymentId: number, data: PaymentUpdate): Promise<Payment> => {
    try {
      const updatedPayment = await paymentApi.updatePayment(paymentId, data);
      await loadPayments(); // Refresh the payments list
      return updatedPayment;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update payment');
      setError(error);
      throw error;
    }
  };

  // Delete a payment
  const deletePayment = async (paymentId: number): Promise<boolean> => {
    try {
      const result = await paymentApi.deletePayment(paymentId);
      if (result.success) {
        await loadPayments(); // Refresh the payments list
      }
      return result.success;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete payment');
      setError(error);
      throw error;
    }
  };

  return {
    payments,
    isLoading,
    error,
    createPayment,
    updatePayment,
    deletePayment,
    refreshPayments: loadPayments
  };
}

// Custom hook for handling a single payment with details
interface UsePaymentDetailsReturn {
  payment: PaymentWithDetails | null;
  isLoading: boolean;
  error: Error | null;
  refreshPayment: () => Promise<void>;
}

export function usePaymentDetails(paymentId: number | null): UsePaymentDetailsReturn {
  const [payment, setPayment] = useState<PaymentWithDetails | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const loadPayment = async () => {
    if (!paymentId) {
      setPayment(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const paymentData = await paymentApi.getPaymentDetails(paymentId);
      setPayment(paymentData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load payment details'));
      console.error('Error loading payment details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load payment when paymentId changes
  useEffect(() => {
    loadPayment();
  }, [paymentId]);

  return {
    payment,
    isLoading,
    error,
    refreshPayment: loadPayment
  };
}

// Custom hook for calculating expected fee
interface UseExpectedFeeReturn {
  expectedFee: number | null;
  isLoading: boolean;
  error: Error | null;
  calculateFee: (params: {
    clientId: number;
    contractId: number;
    assets?: number;
    periodType: 'month' | 'quarter';
    period: number;
    year: number;
  }) => Promise<number | null>;
}

export function useExpectedFee(): UseExpectedFeeReturn {
  const [expectedFee, setExpectedFee] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const calculateFee = async (params: {
    clientId: number;
    contractId: number;
    assets?: number;
    periodType: 'month' | 'quarter';
    period: number;
    year: number;
  }): Promise<number | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await paymentApi.calculateExpectedFee({
        client_id: params.clientId,
        contract_id: params.contractId,
        total_assets: params.assets,
        period_type: params.periodType,
        period: params.period,
        year: params.year
      });

      const fee = result.expected_fee ? Number(result.expected_fee) : null;
      setExpectedFee(fee);
      return fee;
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Failed to calculate expected fee');
      setError(errorObj);
      console.error('Error calculating expected fee:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    expectedFee,
    isLoading,
    error,
    calculateFee
  };
}