#!/usr/bin/env node

/**
 * Mermaid Diagram Validator
 * 
 * This script validates all Mermaid diagrams in markdown files
 * to catch syntax errors before they appear in rendered documentation.
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

// ANSI color codes for output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

/**
 * Extract Mermaid diagrams from markdown content
 */
function extractMermaidDiagrams(content, filename) {
  const mermaidRegex = /```mermaid\n([\s\S]*?)```/g;
  const diagrams = [];
  let match;
  
  while ((match = mermaidRegex.exec(content)) !== null) {
    const lines = content.substring(0, match.index).split('\n');
    diagrams.push({
      content: match[1],
      lineNumber: lines.length + 1,
      filename
    });
  }
  
  return diagrams;
}

/**
 * Validate a single Mermaid diagram
 */
async function validateDiagram(diagram, index) {
  const tempFile = path.join(__dirname, `temp_diagram_${index}.mmd`);
  const outputFile = path.join(__dirname, `temp_diagram_${index}.svg`);
  
  try {
    // Write diagram to temp file
    await fs.writeFile(tempFile, diagram.content);
    
    // Try to render the diagram
    try {
      execSync(`npx mmdc -i "${tempFile}" -o "${outputFile}" --quiet`, {
        stdio: 'pipe'
      });
      
      // Clean up successful render
      await fs.unlink(tempFile).catch(() => {});
      await fs.unlink(outputFile).catch(() => {});
      
      return { success: true, diagram };
    } catch (error) {
      // Clean up failed files
      await fs.unlink(tempFile).catch(() => {});
      await fs.unlink(outputFile).catch(() => {});
      
      return { 
        success: false, 
        diagram,
        error: error.stderr ? error.stderr.toString() : error.message
      };
    }
  } catch (error) {
    return { 
      success: false, 
      diagram,
      error: `Failed to process diagram: ${error.message}`
    };
  }
}

/**
 * Find all markdown files in the project
 */
async function findMarkdownFiles(dir, files = []) {
  const items = await fs.readdir(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = await fs.stat(fullPath);
    
    // Skip node_modules and hidden directories
    if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
      await findMarkdownFiles(fullPath, files);
    } else if (stat.isFile() && item.endsWith('.md')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

/**
 * Main validation function
 */
async function main() {
  console.log(`${colors.blue}🔍 Scanning for Mermaid diagrams...${colors.reset}\n`);
  
  const projectRoot = path.join(__dirname, '..');
  const markdownFiles = await findMarkdownFiles(projectRoot);
  
  let totalDiagrams = 0;
  let failedDiagrams = 0;
  const errors = [];
  
  for (const file of markdownFiles) {
    const content = await fs.readFile(file, 'utf-8');
    const relativePath = path.relative(projectRoot, file);
    const diagrams = extractMermaidDiagrams(content, relativePath);
    
    if (diagrams.length > 0) {
      console.log(`${colors.blue}📄 ${relativePath}${colors.reset} (${diagrams.length} diagram${diagrams.length > 1 ? 's' : ''})`);
      
      for (let i = 0; i < diagrams.length; i++) {
        totalDiagrams++;
        const result = await validateDiagram(diagrams[i], totalDiagrams);
        
        if (result.success) {
          console.log(`  ${colors.green}✓${colors.reset} Diagram at line ${result.diagram.lineNumber}`);
        } else {
          failedDiagrams++;
          console.log(`  ${colors.red}✗${colors.reset} Diagram at line ${result.diagram.lineNumber}`);
          errors.push({
            file: relativePath,
            line: result.diagram.lineNumber,
            error: result.error
          });
        }
      }
    }
  }
  
  console.log(`\n${colors.blue}📊 Summary:${colors.reset}`);
  console.log(`  Total diagrams: ${totalDiagrams}`);
  console.log(`  ${colors.green}✓ Valid: ${totalDiagrams - failedDiagrams}${colors.reset}`);
  console.log(`  ${colors.red}✗ Invalid: ${failedDiagrams}${colors.reset}`);
  
  if (errors.length > 0) {
    console.log(`\n${colors.red}❌ Errors found:${colors.reset}\n`);
    for (const error of errors) {
      console.log(`${colors.yellow}${error.file}:${error.line}${colors.reset}`);
      console.log(`  ${error.error}\n`);
    }
    process.exit(1);
  } else {
    console.log(`\n${colors.green}✅ All Mermaid diagrams are valid!${colors.reset}`);
  }
}

// Run the validator
main().catch(error => {
  console.error(`${colors.red}Fatal error: ${error.message}${colors.reset}`);
  process.exit(1);
});