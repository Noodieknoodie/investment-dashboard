// PASTE THIS DIRECTLY INTO YOUR BROWSER CONSOLE
// This is a minimal diagnostic script to identify client/contract issues

(function() {
  console.clear();
  console.log("=====================================================");
  console.log("🔍 DIAGNOSING CLIENT/CONTRACT BULLSHIT");
  console.log("=====================================================");
  
  // Track valid relationships from API responses
  const validRelationships = {};
  
  // Intercept API calls
  const origFetch = window.fetch;
  window.fetch = function(...args) {
    const url = typeof args[0] === 'string' ? args[0] : args[0].url;
    
    // Extract client data
    if (url.includes('/clients/') && !url.includes('/clients/by-provider') && 
        !url.includes('fee-summary') && !url.includes('compliance')) {
      const match = url.match(/\/clients\/(\d+)/);
      if (match) {
        const clientId = parseInt(match[1], 10);
        
        return origFetch.apply(this, args).then(response => {
          const clone = response.clone();
          clone.json().then(data => {
            if (data?.contracts?.length) {
              const contractIds = data.contracts.map(c => c.contract_id);
              validRelationships[clientId] = contractIds;
              console.log(`✅ Client ${clientId} has contracts: ${contractIds.join(', ')}`);
            }
          }).catch(() => {});
          return response;
        });
      }
    }
    
    // Check periods calls for mismatches
    if (url.includes('/payments/available-periods/')) {
      const match = url.match(/\/payments\/available-periods\/(\d+)\/(\d+)/);
      if (match) {
        const clientId = parseInt(match[1], 10);
        const contractId = parseInt(match[2], 10);
        
        console.group(`🔍 API Call: /payments/available-periods/${clientId}/${contractId}`);
        
        if (validRelationships[clientId]) {
          const isValid = validRelationships[clientId].includes(contractId);
          if (!isValid) {
            console.error(`❌ CONTRACT MISMATCH: Contract ${contractId} doesn't belong to client ${clientId}`);
            console.error(`Valid contracts: ${validRelationships[clientId].join(', ')}`);
            
            // Show stack trace for debugging
            console.error("Stack trace:");
            console.error(new Error().stack.split('\n').slice(1, 6).join('\n'));
          } else {
            console.log(`✅ Valid client/contract relationship`);
          }
        } else {
          console.warn(`⚠️ Unknown client ${clientId}, can't validate`);
        }
        
        console.groupEnd();
      }
    }
    
    return origFetch.apply(this, args);
  };
  
  console.log("Ready! Watching API calls for client/contract mismatches...");
  console.log("Click through clients in the sidebar to trigger the issue");
  console.log("=====================================================");
})(); 