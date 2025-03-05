/**
 * CLIENT/CONTRACT RELATIONSHIP DIAGNOSTIC SCRIPT
 * 
 * Run this directly in your browser console to diagnose the client/contract issue
 */

// Save original fetch
const originalFetch = window.fetch;

// Track API calls
const apiCalls = [];

// Create a map of valid client->contract relationships from the database
const validRelationships = {};

// Monkey patch fetch to track all API calls
window.fetch = function(...args) {
  const url = args[0].toString();
  
  // Track the API call
  apiCalls.push({
    url,
    timestamp: new Date().toISOString(),
    stack: new Error().stack
  });

  // Analyze client data
  if (url.includes('/clients/') && !url.includes('/clients/by-provider')) {
    const match = url.match(/\/clients\/(\d+)/);
    if (match) {
      const clientId = parseInt(match[1], 10);
      
      // After the fetch, capture the client's contracts
      return originalFetch.apply(this, args)
        .then(response => {
          // Clone the response so we can read the body
          const clone = response.clone();
          clone.json().then(data => {
            if (data && data.contracts && Array.isArray(data.contracts)) {
              validRelationships[clientId] = data.contracts.map(c => c.contract_id);
              console.log(`✅ Client ${clientId} has contracts: ${validRelationships[clientId].join(', ')}`);
            }
          }).catch(err => {
            // Ignore JSON parsing errors
          });
          return response;
        });
    }
  }
  
  // Look for available-periods calls
  if (url.includes('/payments/available-periods/')) {
    const match = url.match(/\/payments\/available-periods\/(\d+)\/(\d+)/);
    if (match) {
      const clientId = parseInt(match[1], 10);
      const contractId = parseInt(match[2], 10);
      
      // Log detailed information about this call
      console.group(`🔍 ${new Date().toLocaleTimeString()} - API Call to ${url}`);
      console.log(`Client ID: ${clientId}, Contract ID: ${contractId}`);
      
      // Validate relationship
      if (validRelationships[clientId]) {
        if (!validRelationships[clientId].includes(contractId)) {
          console.error(`❌ INVALID RELATIONSHIP: Contract ${contractId} does not belong to client ${clientId}`);
          console.log('Valid contracts for this client:', validRelationships[clientId]);
          
          // Show component stack
          console.log('Component call stack:');
          const stack = new Error().stack.split('\n');
          stack.forEach((line, i) => {
            if (i > 0 && i < 10) console.log(`  ${line.trim()}`);
          });
          
          // Show recent API calls for context
          console.log('Recent API calls:');
          apiCalls.slice(-10).forEach((call, i) => {
            console.log(`  ${i+1}. ${call.timestamp.substr(11, 8)} - ${call.url}`);
          });
        } else {
          console.log(`✅ Valid relationship: Contract ${contractId} belongs to client ${clientId}`);
        }
      } else {
        console.warn(`⚠️ Unknown client ${clientId} - can't validate relationship`);
      }
      
      console.groupEnd();
    }
  }
  
  // Call original fetch
  return originalFetch.apply(this, args);
};

// Helper function to print all React component state
function getAllReactInstancesOf(componentName) {
  const roots = [];
  const rootElements = document.querySelectorAll('[data-reactroot]');
  
  if (rootElements.length === 0) {
    console.warn('No React roots found. This may not work in production builds.');
    return [];
  }
  
  rootElements.forEach(root => {
    const key = Object.keys(root).find(key => key.startsWith('__reactInternalInstance$'));
    if (key) {
      roots.push(root[key]);
    }
  });
  
  function findComponents(node, componentList = []) {
    if (!node) return componentList;
    
    // Check if this is a component
    if (
      node.memoizedState &&
      node.type &&
      typeof node.type === 'function' &&
      node.type.name === componentName
    ) {
      componentList.push(node);
    }
    
    // Check children
    if (node.child) {
      findComponents(node.child, componentList);
    }
    
    // Check siblings
    if (node.sibling) {
      findComponents(node.sibling, componentList);
    }
    
    return componentList;
  }
  
  let allComponents = [];
  roots.forEach(root => {
    const components = findComponents(root);
    allComponents = [...allComponents, ...components];
  });
  
  return allComponents;
}

// Expose the diagnostic function
window.diagnoseFuckingClientContractIssue = function() {
  console.log('🔍 Starting client/contract relationship diagnostic...');
  console.log('Watching for API calls. Please switch between clients to trigger the issue.');
  
  // Print instructions
  console.log('');
  console.log('INSTRUCTIONS:');
  console.log('1. Click through different clients in the sidebar');
  console.log('2. Watch the console for error messages');
  console.log('3. When you see an error, check the call stack to identify the source');
  console.log('');
  
  return 'Diagnostic running. Check console for results.';
};

// Run automatically
console.log('💉 Client/Contract diagnostic script injected.');
console.log('Type window.diagnoseFuckingClientContractIssue() to start the diagnostic.'); 