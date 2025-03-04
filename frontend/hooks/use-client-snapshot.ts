import { useState, useEffect } from 'react';
import { clientApi, ClientSnapshot, FeeSummary } from '@/lib/api';

interface UseClientSnapshotReturn {
  clientSnapshot: ClientSnapshot | null;
  feeSummary: FeeSummary | null;
  isLoading: boolean;
  error: Error | null;
  refreshData: () => Promise<void>;
}

export function useClientSnapshot(clientId: number | null): UseClientSnapshotReturn {
  const [clientSnapshot, setClientSnapshot] = useState<ClientSnapshot | null>(null);
  const [feeSummary, setFeeSummary] = useState<FeeSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // Function to load client snapshot and fee summary
  const loadData = async () => {
    if (!clientId) {
      setClientSnapshot(null);
      setFeeSummary(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch client details with contracts
      const snapshot = await clientApi.getClientDetails(clientId);
      setClientSnapshot(snapshot);
      
      // Fetch fee summary
      const fees = await clientApi.getClientFeeSummary(clientId);
      setFeeSummary(fees);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load client details'));
      console.error('Error loading client details:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load data when clientId changes
  useEffect(() => {
    loadData();
  }, [clientId]);
  
  return {
    clientSnapshot,
    feeSummary,
    isLoading,
    error,
    refreshData: loadData
  };
}