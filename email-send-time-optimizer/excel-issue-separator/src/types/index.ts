export interface ExcelRow {
  [key: string]: any;
}

export interface IssueData {
  issueType: string;
  rows: ExcelRow[];
  count: number;
}

export interface ProcessingResults {
  fileName: string;
  totalRows: number;
  issueTypes: IssueData[];
  processingTime: number;
  uploadDate: string;
}

export interface ProcessingStats {
  totalIssues: number;
  uniqueIssueTypes: number;
  mostCommonIssue: string;
  leastCommonIssue: string;
}

export interface ExportOptions {
  format: "multiple" | "single";
  selectedIssues: string[];
  includeStats: boolean;
}
