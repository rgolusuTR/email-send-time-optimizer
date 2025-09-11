import React, { useCallback, useState } from "react";
import { Upload, FileSpreadsheet, Download, AlertCircle } from "lucide-react";

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  isProcessing: boolean;
  onDownloadTemplate: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  isProcessing,
  onDownloadTemplate,
}) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        onFileUpload(e.dataTransfer.files[0]);
      }
    },
    [onFileUpload]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      e.preventDefault();
      if (e.target.files && e.target.files[0]) {
        onFileUpload(e.target.files[0]);
      }
    },
    [onFileUpload]
  );

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Upload Your Excel File
          </h2>
          <p className="text-gray-600">
            Upload an Excel file (.xlsx, .xls) or CSV file with issue data to
            automatically separate by type
          </p>
        </div>

        {/* File Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
            dragActive
              ? "border-blue-500 bg-blue-50 drag-active"
              : "border-gray-300 hover:border-gray-400"
          } ${isProcessing ? "pointer-events-none opacity-50" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={handleChange}
            disabled={isProcessing}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          <div className="space-y-4">
            <div className="flex justify-center">
              <Upload className="h-12 w-12 text-gray-400" />
            </div>
            <div>
              <p className="text-lg font-medium text-gray-700">
                {dragActive
                  ? "Drop your file here"
                  : "Drag and drop your file here, or click to browse"}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supports .xlsx, .xls, and .csv files (max 50MB)
              </p>
            </div>
          </div>
        </div>

        {/* File Requirements */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-blue-800 mb-2">
                File Requirements:
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>
                  • Your file must contain a column with "Issue", "Problem", or
                  "Type" in the header
                </li>
                <li>• Each row should represent one issue or data point</li>
                <li>• The first row should contain column headers</li>
                <li>• File size should be less than 50MB</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Template Download */}
        <div className="mt-6 text-center">
          <button
            onClick={onDownloadTemplate}
            disabled={isProcessing}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Download Sample Template
          </button>
          <p className="text-xs text-gray-500 mt-2">
            Not sure about the format? Download our sample template to get
            started.
          </p>
        </div>

        {/* Supported Formats */}
        <div className="mt-8 border-t pt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3 text-center">
            Supported File Formats
          </h3>
          <div className="flex justify-center space-x-6">
            <div className="flex items-center text-sm text-gray-600">
              <FileSpreadsheet className="h-4 w-4 mr-2 text-green-600" />
              Excel (.xlsx)
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <FileSpreadsheet className="h-4 w-4 mr-2 text-green-600" />
              Excel (.xls)
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <FileSpreadsheet className="h-4 w-4 mr-2 text-blue-600" />
              CSV (.csv)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
