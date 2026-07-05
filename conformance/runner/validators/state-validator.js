/**
 * State Validator for AEP v1.0.0
 * Validates R0-R7 registers and state semantics
 */

const fs = require('fs');
const path = require('path');

/**
 * Validate a state file
 * @param {string} filePath - Path to the state file
 * @param {boolean} verbose - Show detailed output
 * @returns {Object} { passed: boolean, errors: string[], warnings: string[] }
 */
function validateState(filePath, verbose = false) {
  const errors = [];
  const warnings = [];

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    errors.push(`File not found: ${filePath}`);
    return { passed: false, errors, warnings };
  }

  // Read file
  let content;
  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch (err) {
    errors.push(`Failed to read file: ${err.message}`);
    return { passed: false, errors, warnings };
  }

  // Extract frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) {
    errors.push('No frontmatter found (missing --- delimiters)');
    return { passed: false, errors, warnings };
  }

  const frontmatter = frontmatterMatch[1];
  
  // Parse YAML-like frontmatter (simplified)
  const parsed = parseYamlLike(frontmatter);

  // Validate required fields
  if (!parsed.type) {
    errors.push('Missing required field: type');
  } else if (parsed.type !== 'state' && parsed.type !== 'status') {
    errors.push(`Invalid type: expected 'state' or 'status', got '${parsed.type}'`);
  }

  if (!parsed.id) {
    errors.push('Missing required field: id');
  }

  if (!parsed.version) {
    errors.push('Missing required field: version');
  } else if (!/^\d+\.\d+\.\d+$/.test(parsed.version)) {
    errors.push(`Invalid version format: ${parsed.version} (expected semver)`);
  }

  if (!parsed.status) {
    errors.push('Missing required field: status');
  } else if (!['draft', 'active', 'deprecated', 'archived'].includes(parsed.status)) {
    errors.push(`Invalid status: ${parsed.status} (expected draft, active, deprecated, archived)`);
  }

  // Validate content (state registers)
  const contentMatch = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
  if (!contentMatch) {
    errors.push('No content found after frontmatter');
    return { passed: false, errors, warnings };
  }

  const stateContent = contentMatch[1];
  const registers = extractRegisters(stateContent);

  // Validate R0-R7
  const requiredRegisters = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'];
  for (const reg of requiredRegisters) {
    if (!registers[reg]) {
      errors.push(`Missing register: ${reg}`);
      continue;
    }

    const value = registers[reg];
    
    // Validate register-specific rules
    switch (reg) {
      case 'R0': // SESSION
        if (!/^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$/.test(value)) {
          errors.push(`R0 [SESSION] invalid format: ${value} (expected YYYY-MM-DD-HH-MM)`);
        }
        break;
      case 'R1': // LAST_ACT
        if (typeof value !== 'string' || value.length < 3) {
          warnings.push(`R1 [LAST_ACT] should be a descriptive string`);
        }
        break;
      case 'R2': // NEXT_ACT
        if (typeof value !== 'string' || value.length < 3) {
          warnings.push(`R2 [NEXT_ACT] should be a descriptive string`);
        }
        break;
      case 'R3': // MODIFIED
        if (typeof value === 'string' && value.includes(',')) {
          warnings.push(`R3 [MODIFIED] contains multiple files (should be delta only)`);
        }
        break;
      case 'R4': // BLOCKERS
        if (typeof value !== 'string' || value === '') {
          warnings.push(`R4 [BLOCKERS] should be 'Nenhum' or describe blockers`);
        }
        break;
      case 'R5': // ACTIVE_SK
        if (!/^skill-/.test(value) && value !== 'Nenhum') {
          warnings.push(`R5 [ACTIVE_SK] should start with 'skill-' or be 'Nenhum'`);
        }
        break;
      case 'R6': // HEALTH
        if (!['OK', 'FAIL'].includes(value)) {
          errors.push(`R6 [HEALTH] invalid: ${value} (expected OK or FAIL)`);
        }
        break;
      case 'R7': // TIMESTAMP
        if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value)) {
          warnings.push(`R7 [TIMESTAMP] invalid format: ${value} (expected ISO 8601 UTC)`);
        }
        break;
    }
  }

  // R3 strict rule: should be delta only (no history)
  if (registers.R3 && typeof registers.R3 === 'string') {
    const files = registers.R3.split(',').map(f => f.trim());
    if (files.length > 3) {
      warnings.push(`R3 [MODIFIED] has ${files.length} files (suspected history accumulation)`);
    }
  }

  const passed = errors.length === 0;

  if (verbose) {
    console.log('\n📋 State Validation Details:');
    console.log(`  File: ${filePath}`);
    console.log(`  Type: ${parsed.type || 'missing'}`);
    console.log(`  ID: ${parsed.id || 'missing'}`);
    console.log(`  Version: ${parsed.version || 'missing'}`);
    console.log(`  Status: ${parsed.status || 'missing'}`);
    console.log('\n  Registers:');
    for (const reg of requiredRegisters) {
      const status = registers[reg] ? '✅' : '❌';
      console.log(`    ${status} ${reg}: ${registers[reg] || 'missing'}`);
    }
    if (warnings.length > 0) {
      console.log('\n  ⚠️  Warnings:');
      for (const warning of warnings) {
        console.log(`    - ${warning}`);
      }
    }
    if (errors.length > 0) {
      console.log('\n  ❌ Errors:');
      for (const error of errors) {
        console.log(`    - ${error}`);
      }
    }
  }

  return { passed, errors, warnings };
}

/**
 * Parse YAML-like frontmatter (simplified)
 */
function parseYamlLike(text) {
  const result = {};
  const lines = text.split('\n');
  for (const line of lines) {
    const match = line.match(/^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/);
    if (match) {
      const key = match[1];
      let value = match[2].trim();
      // Handle arrays
      if (value.startsWith('[') && value.endsWith(']')) {
        value = value.slice(1, -1).split(',').map(v => v.trim());
      }
      // Handle null
      if (value === 'null') {
        value = null;
      }
      result[key] = value;
    }
  }
  return result;
}

/**
 * Extract registers from content
 */
function extractRegisters(content) {
  const registers = {};
  const lines = content.split('\n');
  for (const line of lines) {
    const match = line.match(/^R([0-7])\s*\[([^\]]*)\]\s*=\s*(.*)$/);
    if (match) {
      const num = match[1];
      const name = match[2].trim();
      let value = match[3].trim();
      // Remove quotes if present
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
      }
      registers[`R${num}`] = value;
    }
  }
  return registers;
}

module.exports = {
  validateState,
  extractRegisters,
  parseYamlLike
};