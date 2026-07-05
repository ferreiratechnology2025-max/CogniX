#!/usr/bin/env node

/**
 * AEP Conformance Runner v1.0.0
 * 
 * Usage:
 *   node conformance-runner.js --state <path-to-state.md>
 *   node conformance-runner.js --resource <path-to-resource.md>
 *   node conformance-runner.js --all
 */

const fs = require('fs');
const path = require('path');

// Import validators
const { validateState } = require('./validators/state-validator');
const { validateResource } = require('./validators/resource-validator');

// Colors for output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSuccess(message) {
  log(`✅ ${message}`, 'green');
}

function logError(message) {
  log(`❌ ${message}`, 'red');
}

function logWarning(message) {
  log(`⚠️  ${message}`, 'yellow');
}

function logInfo(message) {
  log(`ℹ️  ${message}`, 'cyan');
}

function logHeader(message) {
  log(`\n${'='.repeat(60)}`, 'blue');
  log(`${colors.bold}${message}${colors.reset}`, 'blue');
  log(`${'='.repeat(60)}\n`, 'blue');
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    state: null,
    resource: null,
    all: false,
    help: false,
    verbose: false
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--state':
        options.state = args[++i];
        break;
      case '--resource':
        options.resource = args[++i];
        break;
      case '--all':
        options.all = true;
        break;
      case '--verbose':
        options.verbose = true;
        break;
      case '--help':
      case '-h':
        options.help = true;
        break;
      default:
        logError(`Unknown option: ${args[i]}`);
        printHelp();
        process.exit(1);
    }
  }

  return options;
}

/**
 * Print help message
 */
function printHelp() {
  logHeader('AEP Conformance Runner v1.0.0');
  console.log(`
Usage:
  node conformance-runner.js --state <path>    Validate a state file
  node conformance-runner.js --resource <path> Validate a resource file
  node conformance-runner.js --all             Run all conformance tests
  node conformance-runner.js --help            Show this help

Options:
  --verbose            Show detailed output
  --state <path>       Path to STATE.md file
  --resource <path>    Path to a Resource file
  --all                Run all conformance tests

Examples:
  node conformance-runner.js --state ../KERNEL/STATE.md
  node conformance-runner.js --resource ../RESOURCES/project-cognix.md
  node conformance-runner.js --all
  `);
}

/**
 * Main execution
 */
function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  logHeader('AEP Conformance Runner v1.0.0');

  let passed = 0;
  let failed = 0;
  let total = 0;

  if (options.all) {
    logInfo('Running all conformance tests...');
    // TODO: Implement all tests
    logWarning('All tests not yet implemented');
    process.exit(0);
  }

  if (options.state) {
    logInfo(`Validating state file: ${options.state}`);
    const result = validateState(options.state, options.verbose);
    total++;
    if (result.passed) {
      passed++;
      logSuccess(`State validation passed`);
    } else {
      failed++;
      logError(`State validation failed: ${result.errors.join(', ')}`);
    }
  }

  if (options.resource) {
    logInfo(`Validating resource file: ${options.resource}`);
    const result = validateResource(options.resource, options.verbose);
    total++;
    if (result.passed) {
      passed++;
      logSuccess(`Resource validation passed`);
    } else {
      failed++;
      logError(`Resource validation failed: ${result.errors.join(', ')}`);
    }
  }

  // Summary
  logHeader('Summary');
  logInfo(`Total: ${total}`);
  logSuccess(`Passed: ${passed}`);
  if (failed > 0) {
    logError(`Failed: ${failed}`);
    process.exit(1);
  } else {
    logSuccess('All validations passed');
    process.exit(0);
  }
}

// Run main
if (require.main === module) {
  main();
}

module.exports = {
  log,
  logSuccess,
  logError,
  logWarning,
  logInfo,
  logHeader
};