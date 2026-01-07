import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  AppState,
  AnalysisType,
  ProcessedEmailData,
  AnalysisResult,
  FilterOptions,
  StoredAnalysis,
  RecentFile,
} from "../types";

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Current Analysis State
      currentFile: null,
      currentData: [],
      currentResults: null,
      analysisType: "best-practices",
      filters: {
        businessUnit: "All",
        organizationType: "All",
        campaignType: "All",
        timezone: undefined,
      },

      // UI State
      isLoading: false,
      error: null,
      progress: 0,

      // History
      recentFiles: [],
      analysisHistory: [],

      // Settings
      settings: {
        enableTimezone: false,
        selectedTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        autoSaveResults: true,
        maxHistoryItems: 20,
      },

      // Actions
      setCurrentFile: (file) => set({ currentFile: file }),

      setCurrentData: (data) => set({ currentData: data }),

      setCurrentResults: (results) => {
        set({ currentResults: results });

        // Auto-save to history if enabled
        const state = get();
        if (results && state.settings.autoSaveResults && state.currentFile) {
          const analysis: StoredAnalysis = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            fileName: state.currentFile.name,
            timestamp: new Date(),
            filters: state.filters,
            results: results,
            analysisType: state.analysisType,
          };
          state.addToHistory(analysis);
        }
      },

      setAnalysisType: (type) => set({ analysisType: type }),

      setFilters: (filters) => set({ filters }),

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      setProgress: (progress) => set({ progress }),

      addToHistory: (analysis) => {
        const state = get();
        const newHistory = [analysis, ...state.analysisHistory];

        // Limit history size
        const limitedHistory = newHistory.slice(
          0,
          state.settings.maxHistoryItems
        );

        set({ analysisHistory: limitedHistory });

        // Add to recent files if not already there
        const fileExists = state.recentFiles.some(
          (f) => f.fileName === analysis.fileName
        );

        if (!fileExists && state.currentFile) {
          const recentFile: RecentFile = {
            id: analysis.id,
            fileName: analysis.fileName,
            uploadDate: analysis.timestamp,
            rowCount: state.currentData.length,
            filters: analysis.filters,
          };

          const newRecentFiles = [recentFile, ...state.recentFiles].slice(
            0,
            state.settings.maxHistoryItems
          );
          set({ recentFiles: newRecentFiles });
        }
      },

      loadFromHistory: (id) => {
        const state = get();
        const analysis = state.analysisHistory.find((a) => a.id === id);

        if (analysis) {
          set({
            currentResults: analysis.results,
            filters: analysis.filters,
            analysisType: analysis.analysisType,
          });
        }
      },

      clearHistory: () => {
        set({
          analysisHistory: [],
          recentFiles: [],
        });
      },

      updateSettings: (newSettings) => {
        const state = get();
        set({
          settings: {
            ...state.settings,
            ...newSettings,
          },
        });
      },
    }),
    {
      name: "email-optimizer-storage",
      partialize: (state) => ({
        // Only persist these fields
        analysisHistory: state.analysisHistory,
        recentFiles: state.recentFiles,
        settings: state.settings,
        filters: state.filters,
        analysisType: state.analysisType,
      }),
    }
  )
);
