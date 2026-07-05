/**
 * AEP Client - High-level API for AEP operations
 */

import * as fs from 'fs';
import * as path from 'path';
import { Resource, State, AEPResult, ResourceType, ResourceStatus } from './types';

export class AEPClient {
  private basePath: string;
  private resourcesPath: string;
  private loadedResources: Map<string, Resource> = new Map();
  private state: State = {};

  constructor(basePath: string = '.') {
    this.basePath = basePath;
    this.resourcesPath = path.join(basePath, 'RESOURCES');
  }

  boot(): AEPResult {
    this.state = {};
    return { status: 'OK', message: 'System initialized' };
  }

  load(resourceId: string): AEPResult {
    const filePath = path.join(this.resourcesPath, `${resourceId}.md`);
    
    if (!fs.existsSync(filePath)) {
      return { status: 'FAIL', error: `Resource '${resourceId}' not found` };
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const resource = this.parseResource(resourceId, content);
    
    if (resource) {
      this.loadedResources.set(resourceId, resource);
      return { status: 'OK', resource: resourceId };
    }
    
    return { status: 'FAIL', error: `Failed to parse resource '${resourceId}'` };
  }

  validate(resourceId: string): AEPResult {
    if (!this.loadedResources.has(resourceId)) {
      const result = this.load(resourceId);
      if (result.status === 'FAIL') return result;
    }

    const resource = this.loadedResources.get(resourceId)!;
    const errors: string[] = [];

    if (!resource.type) errors.push('Missing type');
    if (!resource.id) errors.push('Missing id');
    if (!resource.version) errors.push('Missing version');

    return {
      status: errors.length === 0 ? 'OK' : 'FAIL',
      resource: resourceId,
      valid: errors.length === 0,
      errors
    };
  }

  listResources(): string[] {
    if (!fs.existsSync(this.resourcesPath)) return [];
    return fs.readdirSync(this.resourcesPath)
      .filter(f => f.endsWith('.md'))
      .map(f => path.basename(f, '.md'));
  }

  getState(): State {
    return { ...this.state };
  }

  private parseResource(resourceId: string, content: string): Resource | null {
    const lines = content.split('\n');
    const metadata: Record<string, string> = {};
    const contentLines: string[] = [];
    let inFrontmatter = false;

    for (const line of lines) {
      if (line.trim() === '---') {
        inFrontmatter = !inFrontmatter;
        continue;
      }
      if (inFrontmatter) {
        const colonIndex = line.indexOf(': ');
        if (colonIndex > 0) {
          const key = line.substring(0, colonIndex).trim();
          const value = line.substring(colonIndex + 2).trim();
          metadata[key] = value;
        }
      } else {
        contentLines.push(line);
      }
    }

    try {
      return {
        id: metadata.id || resourceId,
        type: (metadata.type || 'project') as ResourceType,
        version: metadata.version || '0.0.0',
        status: (metadata.status || 'draft') as ResourceStatus,
        depends: this.parseDepends(metadata.depends || ''),
        content: contentLines.join('\n')
      };
    } catch {
      return null;
    }
  }

  private parseDepends(dependsStr: string): string[] {
    if (dependsStr.startsWith('[') && dependsStr.endsWith(']')) {
      return dependsStr.slice(1, -1).split(',').map(d => d.trim()).filter(Boolean);
    }
    return [];
  }
}