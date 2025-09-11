import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import { IssueData, ExportOptions, ProcessingResults } from "../types";

export class ExportUtils {
  static exportToExcel(
    issueData: IssueData[],
    options: ExportOptions,
    originalFileName: string
  ) {
    const selectedData = issueData.filter((issue) =>
      options.selectedIssues.includes(issue.issueType)
    );

    if (options.format === "multiple") {
      // Create separate files for each issue type
      selectedData.forEach((issue) => {
        const workbook = XLSX.utils.book_new();
        const worksheet = XLSX.utils.json_to_sheet(issue.rows);

        XLSX.utils.book_append_sheet(workbook, worksheet, "Issues");

        const fileName = `${this.sanitizeFileName(
          originalFileName
        )}_${this.sanitizeFileName(issue.issueType)}.xlsx`;
        const excelBuffer = XLSX.write(workbook, {
          bookType: "xlsx",
          type: "array",
        });

        this.saveExcelFile(excelBuffer, fileName);
      });
    } else {
      // Create single file with multiple sheets
      const workbook = XLSX.utils.book_new();

      selectedData.forEach((issue) => {
        const worksheet = XLSX.utils.json_to_sheet(issue.rows);
        const sheetName = this.sanitizeSheetName(issue.issueType);
        XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
      });

      // Add summary sheet if requested
      if (options.includeStats) {
        const summaryData = selectedData.map((issue) => ({
          "Issue Type": issue.issueType,
          Count: issue.count,
          Percentage: `${(
            (issue.count / selectedData.reduce((sum, i) => sum + i.count, 0)) *
            100
          ).toFixed(1)}%`,
        }));

        const summarySheet = XLSX.utils.json_to_sheet(summaryData);
        XLSX.utils.book_append_sheet(workbook, summarySheet, "Summary");
      }

      const fileName = `${this.sanitizeFileName(
        originalFileName
      )}_separated.xlsx`;
      const excelBuffer = XLSX.write(workbook, {
        bookType: "xlsx",
        type: "array",
      });

      this.saveExcelFile(excelBuffer, fileName);
    }
  }

  static exportSummaryReport(results: ProcessingResults) {
    const summaryData = [
      { Property: "File Name", Value: results.fileName },
      {
        Property: "Upload Date",
        Value: new Date(results.uploadDate).toLocaleString(),
      },
      { Property: "Total Rows", Value: results.totalRows },
      { Property: "Unique Issue Types", Value: results.issueTypes.length },
      { Property: "Processing Time", Value: `${results.processingTime}ms` },
      { Property: "", Value: "" }, // Empty row
      { Property: "Issue Type Breakdown", Value: "" },
      ...results.issueTypes.map((issue) => ({
        Property: issue.issueType,
        Value: `${issue.count} (${(
          (issue.count / results.totalRows) *
          100
        ).toFixed(1)}%)`,
      })),
    ];

    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.json_to_sheet(summaryData);

    XLSX.utils.book_append_sheet(workbook, worksheet, "Summary Report");

    const fileName = `${this.sanitizeFileName(
      results.fileName
    )}_summary_report.xlsx`;
    const excelBuffer = XLSX.write(workbook, {
      bookType: "xlsx",
      type: "array",
    });

    this.saveExcelFile(excelBuffer, fileName);
  }

  private static saveExcelFile(buffer: any, fileName: string) {
    const blob = new Blob([buffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    saveAs(blob, fileName);
  }

  private static sanitizeFileName(fileName: string): string {
    // Remove file extension and sanitize for file system
    const nameWithoutExt = fileName.replace(/\.[^/.]+$/, "");
    return nameWithoutExt.replace(/[^a-z0-9]/gi, "_").toLowerCase();
  }

  private static sanitizeSheetName(sheetName: string): string {
    // Excel sheet names have restrictions
    return sheetName
      .replace(/[\\\/\?\*\[\]]/g, "_") // Replace invalid characters
      .substring(0, 31); // Max 31 characters
  }

  static downloadTemplate() {
    const templateData = [
      {
        "Page URL": "https://example.com/page1",
        "Issue Type": "Broken Link",
        Description: "Link to external resource is broken",
        Severity: "High",
        "Date Found": "2024-01-15",
      },
      {
        "Page URL": "https://example.com/page2",
        "Issue Type": "Missing Alt Text",
        Description: "Image missing alt attribute",
        Severity: "Medium",
        "Date Found": "2024-01-16",
      },
      {
        "Page URL": "https://example.com/page3",
        "Issue Type": "Broken Link",
        Description: "Internal link returns 404",
        Severity: "High",
        "Date Found": "2024-01-17",
      },
    ];

    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.json_to_sheet(templateData);

    XLSX.utils.book_append_sheet(workbook, worksheet, "Sample Data");

    const excelBuffer = XLSX.write(workbook, {
      bookType: "xlsx",
      type: "array",
    });
    this.saveExcelFile(excelBuffer, "excel_issue_separator_template.xlsx");
  }
}
