/**
 * AEP Type Definitions
 */

export type ResourceType = 'project' | 'status' | 'skill' | 'adr' | 'incident' | 'rule' | 'template';

export type ResourceStatus = 'draft' | 'review' | 'active' | 'deprecated' | 'archived';

export interface Resource {
  id: string;
  type: ResourceType;
  version: string;
  status: ResourceStatus;
  depends?: string[];
  content?: string;
  [key: string]: any;
}

export interface State {
  r0_session?: string;
  r1_last_act?: string;
  r2_next_act?: string;
  r3_modified?: string;
  r4_blockers?: string;
  r5_active_sk?: string;
  r6_health?: string;
  r7_timestamp?: string;
}

export interface AEPResult {
  status: 'OK' | 'FAIL';
  error?: string;
  [key: string]: any;
}