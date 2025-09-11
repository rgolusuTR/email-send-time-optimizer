export interface BrokenLink {
  title: string;
  url: string;
  broken_links: number;
  clicks: number;
  page_level: number;
  page_views: number;
  priority_score?: number;
  last_updated?: string;
}

export interface SystemStatus {
  logged_in: boolean;
  last_scan: string | null;
  cached_entries: number;
  browser_active: boolean;
}

export interface PromptResponse {
  success: boolean;
  message: string;
  data?: any;
  action_taken?: string;
  suggestions?: string[];
}

export interface BrokenLinksResponse {
  data: BrokenLink[];
  total_count: number;
  scan_timestamp: string;
  summary: {
    total_pages: number;
    total_broken_links: number;
    total_clicks: number;
    total_page_views: number;
    avg_broken_links_per_page: number;
  };
}
