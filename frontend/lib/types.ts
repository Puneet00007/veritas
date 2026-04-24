export type Verdict =
  | "TRUE"
  | "MOSTLY_TRUE"
  | "MIXED"
  | "MISLEADING"
  | "FALSE"
  | "UNVERIFIABLE"
  | "SATIRE";

export type Stance = "supports" | "refutes" | "context";

export interface Source {
  id: number;
  url: string;
  title?: string | null;
  publisher?: string | null;
  domain?: string | null;
  credibility: number;
  bias: string;
  kind: string;
  date?: string | null;
}

export interface Evidence {
  source_id: number;
  quote: string;
  stance: Stance;
  agent: string;
}

export interface Claim {
  text: string;
  who?: string | null;
  what?: string | null;
  when?: string | null;
  where?: string | null;
}

export interface RubricBreakdown {
  source_credibility: number;
  source_diversity: number;
  evidence_strength: number;
  fact_checker_consensus: number;
  media_authenticity: number;
  temporal_integrity: number;
  original_source_traceability: number;
}

export interface CheckResult {
  trace_id: string;
  verdict: Verdict;
  legitimacy_score: number;
  confidence: number;
  tl_dr: string;
  claims: Claim[];
  sources: Source[];
  evidence: Evidence[];
  rubric: RubricBreakdown;
  red_flags: string[];
  why_might_i_be_wrong: string;
  critic_notes: string;
  generated_at: string;
  extras: Record<string, unknown>;
}

export interface StreamEvent {
  name: string;
  payload: Record<string, unknown>;
}
