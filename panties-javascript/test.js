// Node.js test script for Panties JavaScript client
// Run with: node test.js

const { PantiesClient } = require('./dist/index.js');

console.log('=== Panties JavaScript Test Suite (Node.js) ===\n');

// Initialize client
console.log('🩲 Initializing Panties client...');
const client = new PantiesClient({
  apiToken: '3be174777f5fb929c316084267c2f851e94a11b826768aa5ac25df3b95ea611a',
  endpoint: 'http://localhost:5000/api/events',
  environment: 'dev',
  serviceName: 'javascript-node-test',
  installGlobalHandlers: false
});
console.log('✓ Client initialized!\n');

// Test 1: Manual exception
console.log('Test 1: Manual exception capture...');
try {
  throw new Error('This is a test exception from Node.js');
} catch (error) {
  client.captureException(error, {
    context: 'manual test',
    platform: 'node.js',
    nodeVersion: process.version
  }, {
    test_type: 'manual',
    severity: 'high'
  });
  console.log('✓ Exception captured!\n');
}

// Test 2: Message capture
console.log('Test 2: Message capture...');
client.captureMessage(
  'This is an info message from Node.js',
  'info',
  { platform: process.platform },
  { test: 'message_capture' }
);
console.log('✓ Info message sent!');

client.captureMessage(
  'This is a warning message',
  'warning',
  { memory: process.memoryUsage() },
  { test: 'warning' }
);
console.log('✓ Warning message sent!\n');

// Test 3: Different error types
console.log('Test 3: Different error types...');

try {
  JSON.parse('invalid json');
} catch (error) {
  client.captureException(error, {}, { error_type: 'SyntaxError' });
  console.log('✓ SyntaxError captured!');
}

try {
  const obj = null;
  obj.property = 'value';
} catch (error) {
  client.captureException(error, {}, { error_type: 'TypeError' });
  console.log('✓ TypeError captured!');
}

try {
  throw new RangeError('Value out of range');
} catch (error) {
  client.captureException(error, {}, { error_type: 'RangeError' });
  console.log('✓ RangeError captured!\n');
}

// Test 4: Async operations
console.log('Test 4: Async error handling...');
(async () => {
  try {
    await Promise.reject(new Error('Async operation failed'));
  } catch (error) {
    client.captureException(error, { async: true }, { test_type: 'async' });
    console.log('✓ Async error captured!\n');
  }

  console.log('=== All tests completed ===\n');
  console.log('⏳ Waiting for events to be sent...');

  // Flush and wait
  await client.flush();
  setTimeout(() => {
    console.log('✓ Done! Check your Panties dashboard at http://localhost:5000\n');
    console.log('🩲 Panties JavaScript - Error tracking made simple!');
    client.dispose();
    process.exit(0);
  }, 2000);
})();
