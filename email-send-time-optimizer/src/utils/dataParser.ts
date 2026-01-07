import Papa from "papaparse";
import type { EmailData, ProcessedEmailData } from "../types";
import {
  parseRate,
  parseDateTime,
  getDayOfWeek,
  getHourOfDay,
} from "./validation";

// Column name aliases - must match validation.ts
const COLUMN_ALIASES: Record<string, string[]> = {
  "Business Unit": [
    "business unit",
    "businessunit",
    "bu",
    "business_unit",
    "business/operating unit",
    "operating unit",
  ],
  "Organization Type": [
    "organization type",
    "organizationtype",
    "org type",
    "orgtype",
    "organization_type",
    "org_type",
    "marketing team gtm",
    "marketing team",
    "team",
  ],
  "Campaign Type": ["campaign type", "campaigntype", "campaign_type"],
  "Send Date": [
    "send date",
    "senddate",
    "date",
    "send_date",
    "date sent",
    "email send date",
  ],
  "Send Time": [
    "send time",
    "sendtime",
    "time",
    "send_time",
    "time sent",
    "email send time",
  ],
  "Open Rate": ["open rate", "openrate", "open_rate", "opens"],
  "Click Rate": [
    "click rate",
    "clickrate",
    "click_rate",
    "clicks",
    "clickthrough rate",
  ],
  "Unsubscribe Rate": [
    "unsubscribe rate",
    "unsubscriberate",
    "unsubscribe_rate",
    "unsub rate",
  ],
  "Bounce Rate": [
    "bounce rate",
    "bouncerate",
    "bounce_rate",
    "bounces",
    "delivered rate",
  ],
};

// Helper function to normalize column names
function normalizeColumnName(name: string): string {
  return name.toLowerCase().trim().replace(/\s+/g, " ");
}

// Helper function to find column value by flexible name matching (including aliases)
function getColumnValue(row: EmailData, columnName: string): any {
  // Try exact match first
  if (row[columnName] !== undefined) {
    return row[columnName];
  }

  // Try case-insensitive match
  const normalizedTarget = normalizeColumnName(columnName);
  const keys = Object.keys(row);

  // Try exact normalized match
  for (const key of keys) {
    const normalizedKey = normalizeColumnName(key);
    if (normalizedKey === normalizedTarget) {
      return row[key];
    }
  }

  // Try aliases
  const aliases = COLUMN_ALIASES[columnName] || [];
  for (const alias of aliases) {
    const normalizedAlias = normalizeColumnName(alias);
    for (const key of keys) {
      const normalizedKey = normalizeColumnName(key);
      if (normalizedKey === normalizedAlias) {
        return row[key];
      }
    }
  }

  return undefined;
}

export async function parseCSVFile(file: File): Promise<EmailData[]> {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: false, // Keep as strings for better control
      complete: (results) => {
        if (results.errors.length > 0) {
          console.warn("CSV parsing warnings:", results.errors);
        }
        resolve(results.data as EmailData[]);
      },
      error: (error) => {
        reject(new Error(`Failed to parse CSV: ${error.message}`));
      },
    });
  });
}

export async function parseExcelFile(file: File): Promise<EmailData[]> {
  try {
    const XLSX = await import("xlsx");
    const buffer = await file.arrayBuffer();
    const workbook = XLSX.read(buffer, { type: "array" });

    // Get the first sheet
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];

    // Convert to JSON
    const data = XLSX.utils.sheet_to_json(worksheet, {
      raw: false, // Format dates as strings
      defval: "", // Default value for empty cells
    });

    return data as EmailData[];
  } catch (error) {
    throw new Error(
      `Failed to parse Excel file: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}

export async function parseFile(file: File): Promise<EmailData[]> {
  const extension = file.name.split(".").pop()?.toLowerCase();

  switch (extension) {
    case "csv":
      return parseCSVFile(file);
    case "xlsx":
    case "xls":
      return parseExcelFile(file);
    default:
      throw new Error(
        `Unsupported file format: ${extension}. Please upload a CSV or Excel file.`
      );
  }
}

export function processEmailData(rawData: EmailData[]): ProcessedEmailData[] {
  const processed: ProcessedEmailData[] = [];

  console.log(`Processing ${rawData.length} rows...`);

  // Debug: Show available columns from first row
  if (rawData.length > 0) {
    console.log("Available columns:", Object.keys(rawData[0]));
  }

  for (let i = 0; i < rawData.length; i++) {
    const row = rawData[i];
    try {
      // Get values using flexible column matching
      const businessUnit = getColumnValue(row, "Business Unit");
      const organizationType = getColumnValue(row, "Organization Type");
      const campaignType = getColumnValue(row, "Campaign Type");
      const sendDate = getColumnValue(row, "Send Date");
      const sendTime = getColumnValue(row, "Send Time");
      const openRate = getColumnValue(row, "Open Rate");
      const clickRate = getColumnValue(row, "Click Rate");
      const unsubscribeRate = getColumnValue(row, "Unsubscribe Rate");
      const bounceRate = getColumnValue(row, "Bounce Rate");

      // Debug first few rows
      if (i < 3) {
        console.log(`Row ${i} values:`);
        console.log("  Business Unit:", businessUnit);
        console.log("  Organization Type:", organizationType);
        console.log("  Campaign Type:", campaignType);
        console.log("  Send Date:", sendDate);
        console.log("  Send Time:", sendTime);
        console.log("  Open Rate:", openRate);
      }

      // Check for required fields - only sendDate and openRate are truly required
      if (!sendDate) {
        if (i < 5) {
          console.log(`Row ${i} skipped - missing Send Date`);
        }
        continue;
      }

      if (openRate === undefined || openRate === null || openRate === "") {
        if (i < 5) {
          console.log(`Row ${i} skipped - missing Open Rate`);
        }
        continue;
      }

      // Parse date and time
      const dateTime = parseDateTime(
        sendDate.toString(),
        sendTime ? sendTime.toString() : "12:00"
      );

      if (!dateTime) {
        if (i < 5) {
          console.log(`Row ${i} skipped - invalid date/time format`);
        }
        continue;
      }

      // Create processed record with defaults for missing fields
      const processedRow: ProcessedEmailData = {
        businessUnit: businessUnit ? businessUnit.toString().trim() : "Unknown",
        organizationType: organizationType
          ? organizationType.toString().trim()
          : "Unknown",
        campaignType: campaignType ? campaignType.toString().trim() : "Unknown",
        sendDate: dateTime,
        sendTime: sendTime ? sendTime.toString().trim() : "12:00",
        dayOfWeek: getDayOfWeek(dateTime),
        hourOfDay: getHourOfDay(dateTime),
        openRate: parseRate(openRate),
        clickRate: parseRate(clickRate || 0),
        unsubscribeRate: parseRate(unsubscribeRate || 0),
        bounceRate: parseRate(bounceRate || 0),
      };

      processed.push(processedRow);
    } catch (error) {
      // Skip invalid rows
      if (i < 3) {
        console.warn(`Row ${i} error:`, error);
      }
      continue;
    }
  }

  console.log(
    `Successfully processed ${processed.length} rows out of ${rawData.length}`
  );
  return processed;
}

export function getUniqueValues(
  data: ProcessedEmailData[],
  field: keyof ProcessedEmailData
): string[] {
  const values = new Set<string>();

  for (const row of data) {
    const value = row[field];
    if (typeof value === "string" && value.trim() !== "") {
      values.add(value);
    }
  }

  return Array.from(values).sort();
}

export function filterData(
  data: ProcessedEmailData[],
  filters: {
    businessUnit?: string;
    organizationType?: string;
    campaignType?: string;
  }
): ProcessedEmailData[] {
  console.log("Filtering with:", filters);
  console.log("Sample data row:", data[0]);

  const filtered = data.filter((row) => {
    if (filters.businessUnit && filters.businessUnit !== "All") {
      if (row.businessUnit !== filters.businessUnit) {
        return false;
      }
    }

    if (filters.organizationType && filters.organizationType !== "All") {
      if (row.organizationType !== filters.organizationType) {
        return false;
      }
    }

    if (filters.campaignType && filters.campaignType !== "All") {
      if (row.campaignType !== filters.campaignType) {
        return false;
      }
    }

    return true;
  });

  console.log(
    `Filter result: ${filtered.length} out of ${data.length} rows passed`
  );
  return filtered;
}
