// Analysis Types
export type AnalysisType = "best-practices" | "historical" | "combined";

// Email Data Structure
export interface EmailData {
  "Business Unit"?: string;
  "Organization Type"?: string;
  "Campaign Type"?: string;
  "Send Date"?: string;
  "Send Time"?: string;
  "Open Rate"?: number | string;
  "Click Rate"?: number | string;
  "Unsubscribe Rate"?: number | string;
  "Bounce Rate"?: number | string;
  [key: string]: any; // Allow for additional fields
}

// Parsed and Processed Data
export interface ProcessedEmailData {
  businessUnit: string;
  organizationType: string;
  campaignType: string;
  sendDate: Date;
  sendTime: string;
  dayOfWeek: string;
  hourOfDay: number;
  openRate: number;
  clickRate: number;
  unsubscribeRate: number;
  bounceRate: number;
}

// Filter Options
export interface FilterOptions {
  businessUnit: string;
  organizationType: string;
  campaignType: string;
  timezone?: string;
}

// Analysis Results
export interface TimeSlotAnalysis {
  dayOfWeek: string;
  hourOfDay: number;
  timeLabel: string;
  avgOpenRate: number;
  avgClickRate: number;
  sampleSize: number;
  score: number;
}

export interface AnalysisResult {
  primary: TimeSlotAnalysis;
  secondary: TimeSlotAnalysis;
  tertiary: TimeSlotAnalysis;
  allTimeSlots: TimeSlotAnalysis[];
  metadata: {
    totalRecords: number;
    dateRange: {
      start: Date;
      end: Date;
    };
    filters: FilterOptions;
    analysisType: AnalysisType;
    timestamp: Date;
  };
}

// Best Practices Data
export interface BestPractice {
  dayOfWeek: string;
  hourOfDay: number;
  timeLabel: string;
  score: number;
  reasoning: string;
}

// Storage Types
export interface StoredAnalysis {
  id: string;
  fileName: string;
  timestamp: Date;
  filters: FilterOptions;
  results: AnalysisResult;
  analysisType: AnalysisType;
}

export interface RecentFile {
  id: string;
  fileName: string;
  uploadDate: Date;
  rowCount: number;
  filters: FilterOptions;
}

// App State
export interface AppState {
  // Current Analysis
  currentFile: File | null;
  currentData: ProcessedEmailData[];
  currentResults: AnalysisResult | null;
  analysisType: AnalysisType;
  filters: FilterOptions;

  // UI State
  isLoading: boolean;
  error: string | null;
  progress: number;

  // History
  recentFiles: RecentFile[];
  analysisHistory: StoredAnalysis[];

  // Settings
  settings: {
    enableTimezone: boolean;
    selectedTimezone: string;
    autoSaveResults: boolean;
    maxHistoryItems: number;
  };

  // Actions
  setCurrentFile: (file: File | null) => void;
  setCurrentData: (data: ProcessedEmailData[]) => void;
  setCurrentResults: (results: AnalysisResult | null) => void;
  setAnalysisType: (type: AnalysisType) => void;
  setFilters: (filters: FilterOptions) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setProgress: (progress: number) => void;
  addToHistory: (analysis: StoredAnalysis) => void;
  loadFromHistory: (id: string) => void;
  clearHistory: () => void;
  updateSettings: (settings: Partial<AppState["settings"]>) => void;
}

// Export Types
export type ExportFormat = "pdf" | "excel" | "csv" | "json";

export interface ExportOptions {
  format: ExportFormat;
  includeCharts: boolean;
  includeRawData: boolean;
  fileName?: string;
}

// Chart Data Types
export interface ChartDataPoint {
  name: string;
  value: number;
  label?: string;
}

export interface HeatmapDataPoint {
  day: string;
  hour: number;
  value: number;
}

// Validation Types
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  rowCount: number;
  columnCount: number;
  requiredColumns: string[];
  missingColumns: string[];
}

// Worker Message Types
export interface WorkerMessage {
  type: "parse" | "analyze" | "filter";
  payload: any;
}

export interface WorkerResponse {
  type: "success" | "error" | "progress";
  data?: any;
  error?: string;
  progress?: number;
}
