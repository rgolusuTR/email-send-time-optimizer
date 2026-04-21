import React, { useState } from "react";
import {
  Upload,
  FileSpreadsheet,
  Download,
  BarChart3,
  Settings,
} from "lucide-react";
import { ProcessingResults, ExportOptions } from "./types";
import { ExcelProcessor } from "./lib/excelProcessor";
import { ExportUtils } from "./lib/exportUtils";
import FileUpload from "./components/FileUpload";
import ProcessingStatus from "./components/ProcessingStatus";
import ResultsView from "./components/ResultsView";
import ExportPanel from "./components/ExportPanel";

function App() {
  const [results, setResults] = useState<ProcessingResults | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<"upload" | "results">(
    "upload"
  );

  const handleFileUpload = async (file: File) => {
    setIsProcessing(true);
    setError(null);

    try {
      const validation = ExcelProcessor.validateFile(file);
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      const processingResults = await ExcelProcessor.processFile(file);
      setResults(processingResults);
      setCurrentView("results");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = (options: ExportOptions) => {
    if (!results) return;

    try {
      ExportUtils.exportToExcel(results.issueTypes, options, results.fileName);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    }
  };

  const handleExportSummary = () => {
    if (!results) return;

    try {
      ExportUtils.exportSummaryReport(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Summary export failed");
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    setCurrentView("upload");
  };

  const handleDownloadTemplate = () => {
    try {
      ExportUtils.downloadTemplate();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Template download failed");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <FileSpreadsheet className="h-12 w-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-800">
              Excel Issue Separator
            </h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload your Excel file with issues and automatically separate them
            by type. Perfect for organizing bug reports, feedback, or any
            categorized data.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-md p-1 flex">
            <button
              onClick={() => setCurrentView("upload")}
              className={`px-6 py-2 rounded-md flex items-center space-x-2 transition-colors ${
                currentView === "upload"
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:text-blue-600"
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </button>
            <button
              onClick={() => setCurrentView("results")}
              disabled={!results}
              className={`px-6 py-2 rounded-md flex items-center space-x-2 transition-colors ${
                currentView === "results" && results
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:text-blue-600 disabled:text-gray-400 disabled:cursor-not-allowed"
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              <span>Results</span>
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
                <div className="ml-auto pl-3">
                  <button
                    onClick={() => setError(null)}
                    className="inline-flex text-red-400 hover:text-red-600"
                  >
                    <span className="sr-only">Dismiss</span>
                    <svg
                      className="h-5 w-5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {currentView === "upload" && (
            <div className="space-y-6">
              <FileUpload
                onFileUpload={handleFileUpload}
                isProcessing={isProcessing}
                onDownloadTemplate={handleDownloadTemplate}
              />
              {isProcessing && <ProcessingStatus />}
            </div>
          )}

          {currentView === "results" && results && (
            <div className="space-y-6">
              <ResultsView results={results} onReset={handleReset} />
              <ExportPanel
                results={results}
                onExport={handleExport}
                onExportSummary={handleExportSummary}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t border-gray-200">
          <p className="text-gray-500 text-sm">
            Excel Issue Separator - Organize your data efficiently
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
