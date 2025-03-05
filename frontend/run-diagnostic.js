/**
 * PASTE THIS DIRECTLY INTO THE BROWSER CONSOLE
 * 
 * This diagnostic script will show you what's happening with client/contract relationships
 * when errors occur.
 */

(function() {
  console.clear();
  console.log('🧠 RUNNING DIAGNOSTIC: Fuck This Client/Contract Bullshit');
  
  // Save original fetch
  const originalFetch = window.fetch;
  
  // Store last known good data
  const state = {
    clientContracts: {},
    activeClientId: null,
    activeContract: null,
    recentApiCalls: []
  };
  
  // Replace fetch to intercept API calls
  window.fetch = function(...args) {
    const url = typeof args[0] === 'string' ? args[0] : args[0].url;
    
    // Track all API calls
    state.recentApiCalls.push({
      url,
      time: new Date().toLocaleTimeString()
    });
    
    if (state.recentApiCalls.length > 20) {
      state.recentApiCalls.shift();
    }
    
    // Check for client calls
    if (url.includes('/clients/') && !url.includes('fee-summary') && !url.includes('compliance')) {
      const match = url.match(/\/clients\/(\d+)/);
      if (match) {
        const clientId = parseInt(match[1], 10);
        state.activeClientId = clientId;
        
        // After getting the data, extract contract info
        return originalFetch.apply(this, args).then(response => {
          const clone = response.clone();
          
          clone.json().then(data => {
            if (data && data.contracts && Array.isArray(data.contracts)) {
              const contractIds = data.contracts.map(c => c.contract_id);
              state.clientContracts[clientId] = contractIds;
              console.log(`📁 Client ${clientId} has contracts: ${contractIds.join(', ')}`);
            }
          }).catch(() => {});
          
          return response;
        });
      }
    }
    
    // Check for periods calls
    if (url.includes('/payments/available-periods/')) {
      const match = url.match(/\/payments\/available-periods\/(\d+)\/(\d+)/);
      if (match) {
        const clientId = parseInt(match[1], 10);
        const contractId = parseInt(match[2], 10);
        
        console.group(`${new Date().toLocaleTimeString()} - Periods API Call: client=${clientId}, contract=${contractId}`);
        
        // Check if this is a valid relationship
        const validContracts = state.clientContracts[clientId];
        if (validContracts) {
          if (!validContracts.includes(contractId)) {
            console.error(`❌ INVALID RELATIONSHIP DETECTED: Contract ${contractId} does not belong to client ${clientId}`);
            console.error(`Valid contracts for client ${clientId} are: ${validContracts.join(', ')}`);
            
            // Find components that might be causing the issue
            console.log('Recent API calls that may have triggered this:');
            state.recentApiCalls.slice(-5).forEach((call, i) => {
              console.log(`  ${call.time} - ${call.url}`);
            });
            
            // Show call stack
            console.log('Call stack:');
            const stack = new Error().stack.split('\n');
            stack.slice(1, 6).forEach(line => console.log('  ' + line.trim()));
          } else {
            console.log(`✅ Valid relationship: Contract ${contractId} belongs to client ${clientId}`);
          }
        } else {
          console.warn(`⚠️ Unknown client ${clientId} contracts - can't validate`);
        }
        
        console.groupEnd();
      }
    }
    
    return originalFetch.apply(this, args);
  };
  
  // Function to manually inspect component state
  window.inspectComponentState = function() {
    // Try to find state in React DevTools
    console.log('Current known state:');
    console.log('Active client ID:', state.activeClientId);
    console.log('Known client->contract mappings:', state.clientContracts);
    console.log('Recent API calls:', state.recentApiCalls);
    
    // Log Next.js router state if available
    if (window.__NEXT_DATA__) {
      console.log('Current route:', window.__NEXT_DATA__.page);
    }
    
    return 'State inspection complete';
  };
  
  console.log('💉 Diagnostic script injected!');
  console.log('');
  console.log('INSTRUCTIONS:');
  console.log('1. Browse through different clients to trigger the issue');
  console.log('2. Watch the console for ❌ ERROR messages');
  console.log('3. When you find errors, type `inspectComponentState()` for more info');
  console.log('');
  console.log('Happy debugging!');
})(); 