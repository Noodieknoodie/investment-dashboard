import React from 'react';

/**
 * CLIENT/CONTRACT RELATIONSHIP DEBUGGING SCRIPT
 * 
 * This script traces state changes to identify when client/contract mismatches occur.
 * To use it, import and call the setupDebugTracking() function early in your app.
 */

// Store original methods
const originalMethods = {
  fetch: window.fetch,
  useState: React.useState,
};

// Track the current client and contract
let currentState = {
  clientId: null as number | null,
  contractId: null as number | null,
  clientSnapshot: null as any,
  previousStateStack: [] as string[],
};

// Setup debug tracking
export function setupDebugTracking() {
  // Intercept all fetch requests
  window.fetch = function(...args) {
    const url = args[0].toString();
    
    // Look for available-periods calls
    if (url.includes('/payments/available-periods/')) {
      // Extract client and contract IDs
      const match = url.match(/\/payments\/available-periods\/(\d+)\/(\d+)/);
      if (match) {
        const clientId = parseInt(match[1], 10);
        const contractId = parseInt(match[2], 10);
        
        console.group(`🔍 DEBUG: API Call to ${url}`);
        console.log(`Client ID: ${clientId}, Contract ID: ${contractId}`);
        
        // Check for mismatch
        if (currentState.clientId !== clientId) {
          console.warn(`⚠️ POTENTIAL ISSUE: Using clientId=${clientId} but current state has clientId=${currentState.clientId}`);
        }
        
        // Log the call stack to see where this is coming from
        console.log('Call stack:', new Error().stack);
        
        // Log the previous state changes
        console.log('Recent state changes:');
        currentState.previousStateStack.slice(-10).forEach((entry, i) => {
          console.log(`  ${i+1}. ${entry}`);
        });
        
        console.groupEnd();
      }
    }
    
    // Call original fetch
    return originalMethods.fetch.apply(this, args);
  };
  
  // Track useState calls for clientId and contractId
  // @ts-ignore - Override the React.useState function for debugging
  React.useState = function<T>(initialState: T | (() => T)) {
    // @ts-ignore - Call the original useState with the same args
    const [state, setState] = originalMethods.useState(initialState);
    
    // Create a wrapped setState function
    const wrappedSetState = (newState: T) => {
      // Identify what's changing based on the call stack
      const stack = new Error().stack || '';
      let stateType = 'unknown';
      
      if (stack.includes('ClientPaymentPage')) {
        if (newState !== null && typeof newState === 'number') {
          if (stack.includes('editingPaymentId')) {
            stateType = 'editingPaymentId';
          } else if (stack.includes('clientId')) {
            stateType = 'clientId';
            currentState.clientId = newState as unknown as number;
            currentState.previousStateStack.push(`Changed clientId to ${newState}`);
          }
        } else if (newState !== null && typeof newState === 'object' && 'contract_id' in (newState as any)) {
          stateType = 'activeContract';
          currentState.contractId = (newState as any).contract_id;
          currentState.previousStateStack.push(`Changed contractId to ${(newState as any).contract_id}`);
        } else if (newState !== null && typeof newState === 'object' && 'client' in (newState as any)) {
          stateType = 'clientSnapshot';
          currentState.clientSnapshot = newState;
          currentState.previousStateStack.push('Updated clientSnapshot');
        }
        
        console.log(`State change: ${stateType} = `, newState);
      }
      
      // Call the original setState
      return setState(newState);
    };
    
    return [state, wrappedSetState];
  };
  
  console.log('🔧 DEBUG: Client/Contract relationship tracing enabled');
}

// Add a client switching test
export function testClientSwitching() {
  console.log('Running client switching test...');
  
  // Simulate client switches to test behavior
  const simulateClientSwitch = (fromClientId: number, toClientId: number) => {
    console.group(`Testing switch from client ${fromClientId} to ${toClientId}`);
    
    // Log the current state before switch
    console.log('Before switch:', {...currentState});
    
    // Simulate a client switch by calling the endpoint manually
    fetch(`/clients/${toClientId}`).then(response => {
      console.log(`Fetched client ${toClientId} data`);
      return response.json();
    }).catch(err => {
      console.error('Error fetching client:', err);
    });
    
    // Check what happens when we try to get periods immediately
    fetch(`/payments/available-periods/${toClientId}/${currentState.contractId}`).then(response => {
      console.log(`Tried to fetch periods for new client with old contract`);
      return response.json();
    }).catch(err => {
      console.error('Expected error with mismatched client/contract:', err);
    });
    
    console.groupEnd();
  };
  
  // Queue test scenarios with delays to see state transitions
  setTimeout(() => simulateClientSwitch(5, 6), 1000);
  setTimeout(() => simulateClientSwitch(6, 2), 3000);
  setTimeout(() => simulateClientSwitch(2, 5), 5000);
} 