/**
 * Resource Validator for AEP v1.0.0
 * Validates Resource structure (type, id, version, depends, status)
 */

const fs = require('fs');
const { parseYamlLike } = require('./state-validator');

const VALID_TYPES = ['project', 'status', 'skill', 'adr', 'incident', 'rule', 'template'];
const VALID_STATUS = ['draft', 'review', 'active', 'deprecated', 'archived'];

/**
 * Validate a resource file
 * @param {string} filePath - Path to the resource file
 * @param {boolean} verbose - Show detailed output
 * @returns {Object} { passed: boolean, errors: string[], warnings: string[] }
 */
function validateResource(filePath, verbose = false) {
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

  // Extract frontmatter (supports both LF and CRLF)
  const frontmatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!frontmatterMatch) {
    errors.push('No frontmatter found (missing --- delimiters)');
    return { passed: false, errors, warnings };
  }

  const frontmatter = frontmatterMatch[1];
  const parsed = parseYamlLike(frontmatter);

  // Validate required fields
  if (!parsed.type) {
    errors.push('Missing required field: type');
  } else if (!VALID_TYPES.includes(parsed.type)) {
    errors.push(`Invalid type: ${parsed.type} (expected one of: ${VALID_TYPES.join(', ')})`);
  }

  if (!parsed.id) {
    errors.push('Missing required field: id');
  } else if (!/^[a-z][a-z0-9-]*$/.test(parsed.id)) {
    errors.push(`Invalid id format: ${parsed.id} (expected kebab-case)`);
  }

  if (!parsed.version) {
    errors.push('Missing required field: version');
  } else if (!/^\d+\.\d+\.\d+$/.test(parsed.version)) {
    errors.push(`Invalid version format: ${parsed.version} (expected semver)`);
  }

  if (parsed.depends !== undefined) {
    if (!Array.isArray(parsed.depends)) {
      errors.push('depends must be an array');
    } else {
      for (const dep of parsed.depends) {
        if (typeof dep !== 'string') {
          errors.push(`Invalid dependency: ${dep} (must be string)`);
        }
      }
    }
  }

  if (!parsed.status) {
    errors.push('Missing required field: status');
  } else if (!VALID_STATUS.includes(parsed.status)) {
    errors.push(`Invalid status: ${parsed.status} (expected one of: ${VALID_STATUS.join(', ')})`);
  }

  // Check content exists (supports CRLF)
  const contentMatch = content.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n([\s\S]*)$/);
  if (!contentMatch || contentMatch[1].trim() === '') {
    warnings.push('Resource content is empty');
  }

  const passed = errors.length === 0;

  if (verbose) {
    console.log('\n📋 Resource Validation Details:');
    console.log(`  File: ${filePath}`);
    console.log(`  Type: ${parsed.type || 'missing'}`);
    console.log(`  ID: ${parsed.id || 'missing'}`);
    console.log(`  Version: ${parsed.version || 'missing'}`);
    console.log(`  Depends: ${parsed.depends ? parsed.depends.join(', ') : 'none'}`);
    console.log(`  Status: ${parsed.status || 'missing'}`);
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

module.exports = {
  validateResource,
  VALID_TYPES,
  VALID_STATUS
};