import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import * as XLSX from "xlsx";
import type { AnalysisResult, ExportFormat } from "../types";

export async function exportResults(
  results: AnalysisResult,
  format: ExportFormat,
  fileName?: string
): Promise<void> {
  const baseFileName = fileName || `email-optimizer-${Date.now()}`;

  switch (format) {
    case "pdf":
      await exportToPDF(results, baseFileName);
      break;
    case "excel":
      await exportToExcel(results, baseFileName);
      break;
    case "csv":
      await exportToCSV(results, baseFileName);
      break;
    case "json":
      await exportToJSON(results, baseFileName);
      break;
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}

async function exportToPDF(
  results: AnalysisResult,
  fileName: string
): Promise<void> {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  let yPosition = 20;

  // Title
  doc.setFontSize(20);
  doc.setFont("helvetica", "bold");
  doc.text("Email Send Time Optimizer", pageWidth / 2, yPosition, {
    align: "center",
  });
  yPosition += 15;

  // Analysis Type
  doc.setFontSize(12);
  doc.setFont("helvetica", "normal");
  const analysisTypeLabel =
    results.metadata.analysisType === "best-practices"
      ? "Best Practices"
      : results.metadata.analysisType === "historical"
      ? "Historical Data"
      : "Combined Analysis";
  doc.text(`Analysis Type: ${analysisTypeLabel}`, 14, yPosition);
  yPosition += 8;

  // Date Range
  if (results.metadata.totalRecords > 0) {
    const startDate = results.metadata.dateRange.start.toLocaleDateString();
    const endDate = results.metadata.dateRange.end.toLocaleDateString();
    doc.text(`Date Range: ${startDate} - ${endDate}`, 14, yPosition);
    yPosition += 8;
    doc.text(`Total Records: ${results.metadata.totalRecords}`, 14, yPosition);
    yPosition += 8;
  }

  // Filters
  const filters = results.metadata.filters;
  if (filters.businessUnit !== "All") {
    doc.text(`Business Unit: ${filters.businessUnit}`, 14, yPosition);
    yPosition += 6;
  }
  if (filters.organizationType !== "All") {
    doc.text(`Organization Type: ${filters.organizationType}`, 14, yPosition);
    yPosition += 6;
  }
  if (filters.campaignType !== "All") {
    doc.text(`Campaign Type: ${filters.campaignType}`, 14, yPosition);
    yPosition += 6;
  }
  yPosition += 5;

  // Top Recommendations
  doc.setFontSize(16);
  doc.setFont("helvetica", "bold");
  doc.text("Top Recommendations", 14, yPosition);
  yPosition += 10;

  // Primary Recommendation
  doc.setFontSize(12);
  doc.setFont("helvetica", "bold");
  doc.text("🥇 Primary:", 14, yPosition);
  doc.setFont("helvetica", "normal");
  doc.text(
    `${results.primary.dayOfWeek} at ${results.primary.timeLabel}`,
    40,
    yPosition
  );
  yPosition += 6;
  doc.text(
    `Open Rate: ${results.primary.avgOpenRate.toFixed(
      1
    )}% | Click Rate: ${results.primary.avgClickRate.toFixed(1)}%`,
    20,
    yPosition
  );
  if (results.primary.sampleSize > 0) {
    yPosition += 6;
    doc.text(
      `Sample Size: ${results.primary.sampleSize} emails`,
      20,
      yPosition
    );
  }
  yPosition += 10;

  // Secondary Recommendation
  doc.setFont("helvetica", "bold");
  doc.text("🥈 Secondary:", 14, yPosition);
  doc.setFont("helvetica", "normal");
  doc.text(
    `${results.secondary.dayOfWeek} at ${results.secondary.timeLabel}`,
    40,
    yPosition
  );
  yPosition += 6;
  doc.text(
    `Open Rate: ${results.secondary.avgOpenRate.toFixed(
      1
    )}% | Click Rate: ${results.secondary.avgClickRate.toFixed(1)}%`,
    20,
    yPosition
  );
  if (results.secondary.sampleSize > 0) {
    yPosition += 6;
    doc.text(
      `Sample Size: ${results.secondary.sampleSize} emails`,
      20,
      yPosition
    );
  }
  yPosition += 10;

  // Tertiary Recommendation
  doc.setFont("helvetica", "bold");
  doc.text("🥉 Tertiary:", 14, yPosition);
  doc.setFont("helvetica", "normal");
  doc.text(
    `${results.tertiary.dayOfWeek} at ${results.tertiary.timeLabel}`,
    40,
    yPosition
  );
  yPosition += 6;
  doc.text(
    `Open Rate: ${results.tertiary.avgOpenRate.toFixed(
      1
    )}% | Click Rate: ${results.tertiary.avgClickRate.toFixed(1)}%`,
    20,
    yPosition
  );
  if (results.tertiary.sampleSize > 0) {
    yPosition += 6;
    doc.text(
      `Sample Size: ${results.tertiary.sampleSize} emails`,
      20,
      yPosition
    );
  }
  yPosition += 15;

  // Detailed Results Table
  if (yPosition > 200) {
    doc.addPage();
    yPosition = 20;
  }

  doc.setFontSize(14);
  doc.setFont("helvetica", "bold");
  doc.text("Detailed Analysis", 14, yPosition);
  yPosition += 10;

  // Create table data
  const tableData = results.allTimeSlots
    .slice(0, 20)
    .map((slot) => [
      `${slot.dayOfWeek} ${slot.timeLabel}`,
      `${slot.avgOpenRate.toFixed(1)}%`,
      `${slot.avgClickRate.toFixed(1)}%`,
      slot.sampleSize.toString(),
      slot.score.toFixed(1),
    ]);

  autoTable(doc, {
    startY: yPosition,
    head: [["Time Slot", "Open Rate", "Click Rate", "Sample Size", "Score"]],
    body: tableData,
    theme: "striped",
    headStyles: { fillColor: [41, 128, 185] },
    styles: { fontSize: 9 },
  });

  // Footer
  const finalY = (doc as any).lastAutoTable.finalY || yPosition + 50;
  doc.setFontSize(8);
  doc.setFont("helvetica", "italic");
  doc.text(
    `Generated on ${new Date().toLocaleString()}`,
    14,
    doc.internal.pageSize.getHeight() - 10
  );

  // Save
  doc.save(`${fileName}.pdf`);
}

async function exportToExcel(
  results: AnalysisResult,
  fileName: string
): Promise<void> {
  const workbook = XLSX.utils.book_new();

  // Summary Sheet
  const summaryData = [
    ["Email Send Time Optimizer - Analysis Results"],
    [],
    ["Analysis Type", getAnalysisTypeLabel(results.metadata.analysisType)],
    ["Generated", new Date(results.metadata.timestamp).toLocaleString()],
    [],
    ["Filters"],
    ["Business Unit", results.metadata.filters.businessUnit],
    ["Organization Type", results.metadata.filters.organizationType],
    ["Campaign Type", results.metadata.filters.campaignType],
    [],
    ["Top Recommendations"],
    [],
    ["Rank", "Day", "Time", "Open Rate", "Click Rate", "Sample Size", "Score"],
    [
      "🥇 Primary",
      results.primary.dayOfWeek,
      results.primary.timeLabel,
      `${results.primary.avgOpenRate.toFixed(1)}%`,
      `${results.primary.avgClickRate.toFixed(1)}%`,
      results.primary.sampleSize,
      results.primary.score.toFixed(1),
    ],
    [
      "🥈 Secondary",
      results.secondary.dayOfWeek,
      results.secondary.timeLabel,
      `${results.secondary.avgOpenRate.toFixed(1)}%`,
      `${results.secondary.avgClickRate.toFixed(1)}%`,
      results.secondary.sampleSize,
      results.secondary.score.toFixed(1),
    ],
    [
      "🥉 Tertiary",
      results.tertiary.dayOfWeek,
      results.tertiary.timeLabel,
      `${results.tertiary.avgOpenRate.toFixed(1)}%`,
      `${results.tertiary.avgClickRate.toFixed(1)}%`,
      results.tertiary.sampleSize,
      results.tertiary.score.toFixed(1),
    ],
  ];

  const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(workbook, summarySheet, "Summary");

  // Detailed Results Sheet
  const detailedData = [
    ["Day of Week", "Time", "Open Rate", "Click Rate", "Sample Size", "Score"],
    ...results.allTimeSlots.map((slot) => [
      slot.dayOfWeek,
      slot.timeLabel,
      slot.avgOpenRate.toFixed(2),
      slot.avgClickRate.toFixed(2),
      slot.sampleSize,
      slot.score.toFixed(2),
    ]),
  ];

  const detailedSheet = XLSX.utils.aoa_to_sheet(detailedData);
  XLSX.utils.book_append_sheet(workbook, detailedSheet, "Detailed Results");

  // Save
  XLSX.writeFile(workbook, `${fileName}.xlsx`);
}

async function exportToCSV(
  results: AnalysisResult,
  fileName: string
): Promise<void> {
  const headers = [
    "Day of Week",
    "Time",
    "Open Rate",
    "Click Rate",
    "Sample Size",
    "Score",
  ];

  const rows = results.allTimeSlots.map((slot) => [
    slot.dayOfWeek,
    slot.timeLabel,
    slot.avgOpenRate.toFixed(2),
    slot.avgClickRate.toFixed(2),
    slot.sampleSize.toString(),
    slot.score.toFixed(2),
  ]);

  const csvContent = [
    headers.join(","),
    ...rows.map((row) => row.join(",")),
  ].join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", `${fileName}.csv`);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function exportToJSON(
  results: AnalysisResult,
  fileName: string
): Promise<void> {
  const jsonContent = JSON.stringify(results, null, 2);
  const blob = new Blob([jsonContent], { type: "application/json" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", `${fileName}.json`);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function getAnalysisTypeLabel(type: string): string {
  switch (type) {
    case "best-practices":
      return "Best Practices";
    case "historical":
      return "Historical Data";
    case "combined":
      return "Combined Analysis";
    default:
      return type;
  }
}
