import React, { useState } from "react";
import { ProcessingResults, ExportOptions } from "../types";
import {
  Download,
  FileSpreadsheet,
  Settings,
  CheckSquare,
  Square,
  FileText,
} from "lucide-react";

interface ExportPanelProps {
  results: ProcessingResults;
  onExport: (options: ExportOptions) => void;
  onExportSummary: () => void;
}

const ExportPanel: React.FC<ExportPanelProps> = ({
  results,
  onExport,
  onExportSummary,
}) => {
  const [exportFormat, setExportFormat] = useState<"multiple" | "single">(
    "single"
  );
  const [selectedIssues, setSelectedIssues] = useState<string[]>(
    results.issueTypes.map((issue) => issue.issueType)
  );
  const [includeStats, setIncludeStats] = useState(true);

  const toggleIssueSelection = (issueType: string) => {
    setSelectedIssues((prev) =>
      prev.includes(issueType)
        ? prev.filter((type) => type !== issueType)
        : [...prev, issueType]
    );
  };

  const selectAll = () => {
    setSelectedIssues(results.issueTypes.map((issue) => issue.issueType));
  };

  const selectNone = () => {
    setSelectedIssues([]);
  };

  const handleExport = () => {
    if (selectedIssues.length === 0) {
      alert("Please select at least one issue type to export.");
      return;
    }

    const options: ExportOptions = {
      format: exportFormat,
      selectedIssues,
      includeStats,
    };

    onExport(options);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Download className="h-6 w-6 text-blue-600" />
            <h3 className="text-xl font-bold text-gray-800">Export Options</h3>
          </div>
          <button
            onClick={onExportSummary}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <FileText className="h-4 w-4 mr-2" />
            Export Summary Report
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Export Format */}
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-gray-800">Export Format</h4>

            <div className="space-y-3">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="exportFormat"
                  value="single"
                  checked={exportFormat === "single"}
                  onChange={(e) => setExportFormat(e.target.value as "single")}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div>
                  <div className="font-medium text-gray-800">Single File</div>
                  <div className="text-sm text-gray-600">
                    One Excel file with separate sheets for each issue type
                  </div>
                </div>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="exportFormat"
                  value="multiple"
                  checked={exportFormat === "multiple"}
                  onChange={(e) =>
                    setExportFormat(e.target.value as "multiple")
                  }
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div>
                  <div className="font-medium text-gray-800">
                    Multiple Files
                  </div>
                  <div className="text-sm text-gray-600">
                    Separate Excel file for each issue type
                  </div>
                </div>
              </label>
            </div>

            {/* Additional Options */}
            <div className="pt-4 border-t">
              <h5 className="font-medium text-gray-800 mb-3">
                Additional Options
              </h5>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeStats}
                  onChange={(e) => setIncludeStats(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div>
                  <div className="font-medium text-gray-800">
                    Include Statistics
                  </div>
                  <div className="text-sm text-gray-600">
                    Add a summary sheet with issue type statistics
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Issue Selection */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-medium text-gray-800">
                Select Issue Types
              </h4>
              <div className="space-x-2">
                <button
                  onClick={selectAll}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  Select All
                </button>
                <span className="text-gray-300">|</span>
                <button
                  onClick={selectNone}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  Select None
                </button>
              </div>
            </div>

            <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-3 space-y-2">
              {results.issueTypes.map((issue) => (
                <label
                  key={issue.issueType}
                  className="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <div className="flex items-center space-x-3">
                    <button
                      type="button"
                      onClick={() => toggleIssueSelection(issue.issueType)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      {selectedIssues.includes(issue.issueType) ? (
                        <CheckSquare className="h-5 w-5" />
                      ) : (
                        <Square className="h-5 w-5" />
                      )}
                    </button>
                    <div>
                      <div className="font-medium text-gray-800">
                        {issue.issueType}
                      </div>
                      <div className="text-sm text-gray-600">
                        {issue.count} issues
                      </div>
                    </div>
                  </div>
                  <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                    {((issue.count / results.totalRows) * 100).toFixed(1)}%
                  </div>
                </label>
              ))}
            </div>

            <div className="text-sm text-gray-600">
              {selectedIssues.length} of {results.issueTypes.length} issue types
              selected
            </div>
          </div>
        </div>

        {/* Export Button */}
        <div className="mt-8 pt-6 border-t">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {exportFormat === "single" ? (
                <>
                  <FileSpreadsheet className="inline h-4 w-4 mr-1" />
                  Will create 1 Excel file with {selectedIssues.length} sheets
                  {includeStats && " + summary sheet"}
                </>
              ) : (
                <>
                  <FileSpreadsheet className="inline h-4 w-4 mr-1" />
                  Will create {selectedIssues.length} separate Excel files
                </>
              )}
            </div>
            <button
              onClick={handleExport}
              disabled={selectedIssues.length === 0}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors btn-primary"
            >
              <Download className="h-5 w-5 mr-2" />
              Export Selected Issues
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportPanel;
