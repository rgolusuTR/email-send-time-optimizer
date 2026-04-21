import type { EmailData, ValidationResult } from "../types";

const REQUIRED_COLUMNS = [
  "Business Unit",
  "Organization Type",
  "Campaign Type",
  "Send Date",
  "Send Time",
  "Open Rate",
];

// Column name aliases - alternative names that should be accepted
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

const OPTIONAL_COLUMNS = ["Click Rate", "Unsubscribe Rate", "Bounce Rate"];

// Helper function to normalize column names for comparison
function normalizeColumnName(name: string): string {
  return name.toLowerCase().trim().replace(/\s+/g, " ");
}

// Helper function to find a column by normalized name (including aliases)
function findColumn(
  availableColumns: string[],
  targetColumn: string
): string | undefined {
  const normalizedTarget = normalizeColumnName(targetColumn);

  // Try exact normalized match first
  const exactMatch = availableColumns.find(
    (col) => normalizeColumnName(col) === normalizedTarget
  );
  if (exactMatch) return exactMatch;

  // Try aliases
  const aliases = COLUMN_ALIASES[targetColumn] || [];
  for (const alias of aliases) {
    const normalizedAlias = normalizeColumnName(alias);
    const aliasMatch = availableColumns.find(
      (col) => normalizeColumnName(col) === normalizedAlias
    );
    if (aliasMatch) return aliasMatch;
  }

  return undefined;
}

export function validateEmailData(data: EmailData[]): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!data || data.length === 0) {
    errors.push("No data provided");
    return {
      isValid: false,
      errors,
      warnings,
      rowCount: 0,
      columnCount: 0,
      requiredColumns: REQUIRED_COLUMNS,
      missingColumns: REQUIRED_COLUMNS,
    };
  }

  // Check for required columns (case-insensitive)
  const firstRow = data[0];
  const availableColumns = Object.keys(firstRow);

  // Debug: Log available columns
  console.log("Available columns in file:", availableColumns);
  console.log("Required columns:", REQUIRED_COLUMNS);

  const missingColumns = REQUIRED_COLUMNS.filter(
    (col) => !findColumn(availableColumns, col)
  );

  if (missingColumns.length > 0) {
    console.log("Missing columns:", missingColumns);
    console.log("Column matching results:");
    REQUIRED_COLUMNS.forEach((reqCol) => {
      const found = findColumn(availableColumns, reqCol);
      console.log(`  "${reqCol}" -> ${found ? `"${found}" ✓` : "NOT FOUND ✗"}`);
    });
    errors.push(
      `Missing required columns: ${missingColumns.join(
        ", "
      )}. Available columns: ${availableColumns.join(", ")}`
    );
  }

  // Check for optional columns
  const missingOptionalColumns = OPTIONAL_COLUMNS.filter(
    (col) => !availableColumns.includes(col)
  );

  if (missingOptionalColumns.length > 0) {
    warnings.push(
      `Missing optional columns: ${missingOptionalColumns.join(
        ", "
      )}. These will be set to 0.`
    );
  }

  // Validate data types and values
  let invalidRowCount = 0;
  const maxRowsToCheck = Math.min(data.length, 100); // Sample first 100 rows

  for (let i = 0; i < maxRowsToCheck; i++) {
    const row = data[i];
    let hasError = false;

    // Check Business Unit
    if (
      !row["Business Unit"] ||
      row["Business Unit"].toString().trim() === ""
    ) {
      hasError = true;
    }

    // Check Organization Type
    if (
      !row["Organization Type"] ||
      row["Organization Type"].toString().trim() === ""
    ) {
      hasError = true;
    }

    // Check Campaign Type
    if (
      !row["Campaign Type"] ||
      row["Campaign Type"].toString().trim() === ""
    ) {
      hasError = true;
    }

    // Check Send Date
    if (!row["Send Date"] || !isValidDate(row["Send Date"])) {
      hasError = true;
    }

    // Check Send Time
    if (!row["Send Time"] || !isValidTime(row["Send Time"])) {
      hasError = true;
    }

    // Check Open Rate
    if (row["Open Rate"] !== undefined && row["Open Rate"] !== null) {
      const openRate = parseRate(row["Open Rate"]);
      if (isNaN(openRate) || openRate < 0 || openRate > 100) {
        hasError = true;
      }
    }

    if (hasError) {
      invalidRowCount++;
    }
  }

  if (invalidRowCount > 0) {
    const percentage = ((invalidRowCount / maxRowsToCheck) * 100).toFixed(1);
    warnings.push(
      `${invalidRowCount} out of ${maxRowsToCheck} sampled rows have invalid or missing data (${percentage}%). These rows will be skipped during analysis.`
    );
  }

  // Check minimum data requirement
  if (data.length < 10) {
    warnings.push(
      "Dataset is very small (less than 10 rows). Results may not be statistically significant."
    );
  }

  const isValid = errors.length === 0;

  return {
    isValid,
    errors,
    warnings,
    rowCount: data.length,
    columnCount: availableColumns.length,
    requiredColumns: REQUIRED_COLUMNS,
    missingColumns,
  };
}

function isValidDate(dateStr: any): boolean {
  if (!dateStr) return false;

  const str = dateStr.toString().trim();
  if (str === "") return false;

  // Try parsing the date
  const date = new Date(str);
  return !isNaN(date.getTime());
}

function isValidTime(timeStr: any): boolean {
  if (!timeStr) return false;

  const str = timeStr.toString().trim();
  if (str === "") return false;

  // Check for common time formats: HH:MM, HH:MM:SS, H:MM AM/PM, etc.
  const timeRegex =
    /^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?(\s?(AM|PM|am|pm))?$/;
  return timeRegex.test(str);
}

export function parseRate(value: any): number {
  if (typeof value === "number") {
    return value;
  }

  if (typeof value === "string") {
    // Remove percentage sign if present
    const cleaned = value.replace("%", "").trim();
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
  }

  return 0;
}

export function parseDateTime(dateStr: string, timeStr: string): Date | null {
  try {
    // Combine date and time
    const dateTimeStr = `${dateStr} ${timeStr}`;
    const date = new Date(dateTimeStr);

    if (isNaN(date.getTime())) {
      return null;
    }

    return date;
  } catch (error) {
    return null;
  }
}

export function getDayOfWeek(date: Date): string {
  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  return days[date.getDay()];
}

export function getHourOfDay(date: Date): number {
  return date.getHours();
}

export function formatTimeLabel(hour: number): string {
  const period = hour >= 12 ? "PM" : "AM";
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${displayHour}:00 ${period}`;
}
