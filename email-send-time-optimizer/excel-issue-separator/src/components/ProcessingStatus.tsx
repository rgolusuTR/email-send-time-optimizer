import React from "react";
import { Loader2, FileSpreadsheet } from "lucide-react";

const ProcessingStatus: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <FileSpreadsheet className="h-16 w-16 text-blue-600" />
              <Loader2 className="h-6 w-6 text-blue-600 animate-spin absolute -top-1 -right-1" />
            </div>
          </div>

          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Processing Your File
          </h2>

          <p className="text-gray-600 mb-6">
            Please wait while we analyze your data and separate issues by
            type...
          </p>

          <div className="max-w-md mx-auto">
            <div className="bg-gray-200 rounded-full h-2 mb-4">
              <div
                className="bg-blue-600 h-2 rounded-full animate-pulse"
                style={{ width: "60%" }}
              ></div>
            </div>

            <div className="space-y-2 text-sm text-gray-500">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Reading file structure</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span>Analyzing issue types</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                <span>Grouping data</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingStatus;
