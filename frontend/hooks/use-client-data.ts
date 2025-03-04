import { useState, useEffect } from 'react';
import { clientApi, Client, ProviderClientGroup, ComplianceStatus } from '@/lib/api';

interface UseClientDataReturn {
  clients: Client[];
  clientsByProvider: ProviderClientGroup[];
  selectedClient: Client | null;
  complianceStatuses: Record<number, ComplianceStatus>;
  isLoading: boolean;
  error: Error | null;
  selectClient: (clientId: number) => void;
  refreshData: () => void;
}

export function useClientData(): UseClientDataReturn {
  const [clients, setClients] = useState<Client[]>([]);
  const [clientsByProvider, setClientsByProvider] = useState<ProviderClientGroup[]>([]);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [complianceStatuses, setComplianceStatuses] = useState<Record<number, ComplianceStatus>>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  // Function to load all client data
  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch all clients
      const clientsData = await clientApi.getAllClients();
      setClients(clientsData);
      
      // Fetch clients by provider
      const providerData = await clientApi.getClientsByProvider();
      setClientsByProvider(providerData);
      
      // Load compliance statuses for all clients
      const statuses: Record<number, ComplianceStatus> = {};
      
      // Using Promise.all to fetch compliance statuses in parallel
      await Promise.all(
        clientsData.map(async (client) => {
          try {
            const status = await clientApi.getClientComplianceStatus(client.client_id);
            statuses[client.client_id] = status;
          } catch (e) {
            console.error(`Failed to fetch compliance status for client ${client.client_id}:`, e);
            // Set a default status if fetch fails
            statuses[client.client_id] = {
              status: 'yellow',
              reason: 'Unable to determine compliance status'
            };
          }
        })
      );
      
      setComplianceStatuses(statuses);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load client data'));
      console.error('Error loading client data:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);
  
  // Function to select a client by ID
  const selectClient = (clientId: number) => {
    const client = clients.find(c => c.client_id === clientId) || null;
    setSelectedClient(client);
  };
  
  return {
    clients,
    clientsByProvider,
    selectedClient,
    complianceStatuses,
    isLoading,
    error,
    selectClient,
    refreshData: loadData
  };
}

// Helper function to map backend compliance status to frontend format
export const mapComplianceStatus = (status: ComplianceStatus): 'Compliant' | 'Review Needed' | 'Payment Overdue' => {
  switch (status.status) {
    case 'green':
      return 'Compliant';
    case 'yellow':
      return 'Review Needed';
    case 'red':
      return 'Payment Overdue';
    default:
      return 'Review Needed';
  }
};