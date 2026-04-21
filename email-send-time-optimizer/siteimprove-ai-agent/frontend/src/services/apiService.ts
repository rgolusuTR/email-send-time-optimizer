import axios from "axios";
import {
  BrokenLinksResponse,
  PromptResponse,
  SystemStatus,
} from "../types/types";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiService = {
  // Process natural language prompts
  async processPrompt(prompt: string): Promise<PromptResponse> {
    const response = await api.post("/api/prompt", { prompt });
    return response.data;
  },

  // Get broken links data
  async getBrokenLinks(
    forceRefresh: boolean = false
  ): Promise<BrokenLinksResponse> {
    const response = await api.get("/api/broken-links", {
      params: { force_refresh: forceRefresh },
    });
    return response.data;
  },

  // Get system status
  async getStatus(): Promise<SystemStatus> {
    const response = await api.get("/api/status");
    return response.data;
  },

  // Trigger a scan
  async triggerScan(
    forceRefresh: boolean = false
  ): Promise<{ message: string; status: string }> {
    const response = await api.post("/api/scan", {
      force_refresh: forceRefresh,
    });
    return response.data;
  },

  // Filter broken links
  async filterBrokenLinks(
    filters: any
  ): Promise<{ data: any[]; total_count: number }> {
    const response = await api.post("/api/filter", filters);
    return response.data;
  },

  // Export data
  async exportData(
    format: string = "csv",
    filters?: any
  ): Promise<{ filename: string; download_url: string }> {
    const response = await api.post("/api/export", {
      format,
      filters,
      include_priority: true,
    });
    return response.data;
  },

  // Download file
  getDownloadUrl(filename: string): string {
    return `${API_BASE_URL}/api/download/${filename}`;
  },
};
