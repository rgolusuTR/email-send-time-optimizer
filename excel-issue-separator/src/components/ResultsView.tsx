import React, { useState } from "react";
import { ProcessingResults } from "../types";
import { ExcelProcessor } from "../lib/excelProcessor";
import {
  FileSpreadsheet,
  Clock,
  BarChart3,
  ChevronDown,
  ChevronRight,
  RefreshCw,
  Eye,
} from "lucide-react";

interface ResultsViewProps {
  results: ProcessingResults;
  onReset: () => void;
}

const ResultsView: React.FC<ResultsViewProps> = ({ results, onReset }) => {
  const [expandedIssues, setExpandedIssues] = useState<Set<string>>(new Set());
  const [previewIssue, setPreviewIssue] = useState<string | null>(null);

  const stats = ExcelProcessor.getProcessingStats(results);

  const toggleExpanded = (issueType: string) => {
    const newExpanded = new Set(expandedIssues);
    if (newExpanded.has(issueType)) {
      newExpanded.delete(issueType);
    } else {
      newExpanded.add(issueType);
    }
    setExpandedIssues(newExpanded);
  };

  const togglePreview = (issueType: string) => {
    setPreviewIssue(previewIssue === issueType ? null : issueType);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Summary Card */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <FileSpreadsheet className="h-8 w-8 text-green-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-800">
                Processing Complete
              </h2>
              <p className="text-gray-600">File: {results.fileName}</p>
            </div>
          </div>
          <button
            onClick={onReset}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Process New File
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-blue-800">
                  Total Issues
                </p>
                <p className="text-2xl font-bold text-blue-900">
                  {stats.totalIssues}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <FileSpreadsheet className="h-5 w-5 text-green-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-green-800">
                  Issue Types
                </p>
                <p className="text-2xl font-bold text-green-900">
                  {stats.uniqueIssueTypes}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <Clock className="h-5 w-5 text-purple-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-purple-800">
                  Processing Time
                </p>
                <p className="text-2xl font-bold text-purple-900">
                  {results.processingTime}ms
                </p>
              </div>
            </div>
          </div>

          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center">
              <BarChart3 className="h-5 w-5 text-orange-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-orange-800">
                  Most Common
                </p>
                <p className="text-lg font-bold text-orange-900 truncate">
                  {stats.mostCommonIssue}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Info */}
        <div className="text-sm text-gray-500">
          Processed on {new Date(results.uploadDate).toLocaleString()}
        </div>
      </div>

      {/* Issue Types List */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          Issue Types Breakdown
        </h3>

        <div className="space-y-3">
          {results.issueTypes.map((issue, index) => (
            <div
              key={issue.issueType}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              <div className="bg-gray-50 px-4 py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => toggleExpanded(issue.issueType)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    {expandedIssues.has(issue.issueType) ? (
                      <ChevronDown className="h-5 w-5" />
                    ) : (
                      <ChevronRight className="h-5 w-5" />
                    )}
                  </button>
                  <div>
                    <h4 className="font-medium text-gray-800">
                      {issue.issueType}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {issue.count} issues (
                      {((issue.count / results.totalRows) * 100).toFixed(1)}%)
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => togglePreview(issue.issueType)}
                    className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    Preview
                  </button>
                  <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
                    {issue.count}
                  </div>
                </div>
              </div>

              {expandedIssues.has(issue.issueType) && (
                <div className="p-4 bg-white">
                  <div className="mb-3">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${(issue.count / results.totalRows) * 100}%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  {previewIssue === issue.issueType &&
                    issue.rows.length > 0 && (
                      <div className="mt-4">
                        <h5 className="font-medium text-gray-800 mb-2">
                          Sample Data (showing first 3 rows):
                        </h5>
                        <div className="overflow-x-auto">
                          <table className="min-w-full data-table">
                            <thead>
                              <tr>
                                {Object.keys(issue.rows[0]).map((header) => (
                                  <th
                                    key={header}
                                    className="px-3 py-2 text-left"
                                  >
                                    {header}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {issue.rows.slice(0, 3).map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                  {Object.values(row).map(
                                    (value, cellIndex) => (
                                      <td key={cellIndex} className="px-3 py-2">
                                        {String(value).length > 50
                                          ? String(value).substring(0, 50) +
                                            "..."
                                          : String(value)}
                                      </td>
                                    )
                                  )}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        {issue.rows.length > 3 && (
                          <p className="text-sm text-gray-500 mt-2">
                            ... and {issue.rows.length - 3} more rows
                          </p>
                        )}
                      </div>
                    )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsView;
