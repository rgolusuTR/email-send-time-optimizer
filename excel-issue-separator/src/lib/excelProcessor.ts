import * as XLSX from "xlsx";
import { ProcessingResults, IssueType } from "../types";

export const processExcelFile = async (
  file: File
): Promise<ProcessingResults> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: "array" });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];

        // Convert to JSON with header option to get raw data
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

        if (!jsonData || jsonData.length === 0) {
          throw new Error("No data found in the file");
        }

        // Find the header row by looking for a row that contains "Issue", "Problem", or "Type"
        let headerRowIndex = -1;
        let issueColumnIndex = -1;

        for (let i = 0; i < Math.min(10, jsonData.length); i++) {
          const row = jsonData[i] as any[];
          if (row && Array.isArray(row)) {
            for (let j = 0; j < row.length; j++) {
              const cellValue = String(row[j] || "")
                .toLowerCase()
                .trim();
              if (
                cellValue.includes("issue") ||
                cellValue.includes("problem") ||
                cellValue.includes("type")
              ) {
                headerRowIndex = i;
                issueColumnIndex = j;
                break;
              }
            }
            if (headerRowIndex !== -1) break;
          }
        }

        if (headerRowIndex === -1 || issueColumnIndex === -1) {
          throw new Error(
            "Could not find a column with 'Issue', 'Problem', or 'Type' in the header"
          );
        }

        // Get headers from the found header row
        const headers = jsonData[headerRowIndex] as any[];

        // Process data rows (everything after the header row)
        const dataRows = jsonData.slice(headerRowIndex + 1);
        const validRows = dataRows.filter((row: any) => {
          return (
            Array.isArray(row) &&
            row.length > issueColumnIndex &&
            row[issueColumnIndex]
          );
        });

        if (validRows.length === 0) {
          throw new Error("No valid data rows found");
        }

        // Group by issue type
        const issueGroups: { [key: string]: any[] } = {};

        validRows.forEach((row: any) => {
          const issueType = String(row[issueColumnIndex] || "").trim();
          if (issueType) {
            if (!issueGroups[issueType]) {
              issueGroups[issueType] = [];
            }

            // Convert row array to object using headers
            const rowObject: any = {};
            headers.forEach((header: any, index: number) => {
              if (header) {
                rowObject[String(header)] = row[index] || "";
              }
            });

            issueGroups[issueType].push(rowObject);
          }
        });

        // Create issue types summary
        const issueTypes: IssueType[] = Object.entries(issueGroups).map(
          ([issueType, rows]) => ({
            issueType,
            count: rows.length,
            data: rows,
          })
        );

        // Sort by count (descending)
        issueTypes.sort((a, b) => b.count - a.count);

        const results: ProcessingResults = {
          fileName: file.name,
          totalRows: validRows.length,
          issueTypes,
          headers: headers.map((h) => String(h || "")),
          rawData: validRows,
        };

        resolve(results);
      } catch (error) {
        reject(
          new Error(
            `Failed to process file: ${
              error instanceof Error ? error.message : "Unknown error"
            }`
          )
        );
      }
    };

    reader.onerror = () => {
      reject(new Error("Failed to read file"));
    };

    if (file.name.toLowerCase().endsWith(".csv")) {
      reader.readAsText(file);
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          const lines = text.split("\n").map((line) => line.split(","));

          // Find header row for CSV
          let headerRowIndex = -1;
          let issueColumnIndex = -1;

          for (let i = 0; i < Math.min(10, lines.length); i++) {
            const row = lines[i];
            if (row && Array.isArray(row)) {
              for (let j = 0; j < row.length; j++) {
                const cellValue = String(row[j] || "")
                  .toLowerCase()
                  .trim()
                  .replace(/"/g, "");
                if (
                  cellValue.includes("issue") ||
                  cellValue.includes("problem") ||
                  cellValue.includes("type")
                ) {
                  headerRowIndex = i;
                  issueColumnIndex = j;
                  break;
                }
              }
              if (headerRowIndex !== -1) break;
            }
          }

          if (headerRowIndex === -1 || issueColumnIndex === -1) {
            throw new Error(
              "Could not find a column with 'Issue', 'Problem', or 'Type' in the header"
            );
          }

          const headers = lines[headerRowIndex].map((h) =>
            String(h || "")
              .replace(/"/g, "")
              .trim()
          );
          const dataRows = lines.slice(headerRowIndex + 1);
          const validRows = dataRows.filter((row: any) => {
            return (
              Array.isArray(row) &&
              row.length > issueColumnIndex &&
              String(row[issueColumnIndex] || "")
                .replace(/"/g, "")
                .trim()
            );
          });

          if (validRows.length === 0) {
            throw new Error("No valid data rows found");
          }

          // Group by issue type
          const issueGroups: { [key: string]: any[] } = {};

          validRows.forEach((row: any) => {
            const issueType = String(row[issueColumnIndex] || "")
              .replace(/"/g, "")
              .trim();
            if (issueType) {
              if (!issueGroups[issueType]) {
                issueGroups[issueType] = [];
              }

              // Convert row array to object using headers
              const rowObject: any = {};
              headers.forEach((header: any, index: number) => {
                if (header) {
                  rowObject[header] = String(row[index] || "")
                    .replace(/"/g, "")
                    .trim();
                }
              });

              issueGroups[issueType].push(rowObject);
            }
          });

          // Create issue types summary
          const issueTypes: IssueType[] = Object.entries(issueGroups).map(
            ([issueType, rows]) => ({
              issueType,
              count: rows.length,
              data: rows,
            })
          );

          // Sort by count (descending)
          issueTypes.sort((a, b) => b.count - a.count);

          const results: ProcessingResults = {
            fileName: file.name,
            totalRows: validRows.length,
            issueTypes,
            headers,
            rawData: validRows,
          };

          resolve(results);
        } catch (error) {
          reject(
            new Error(
              `Failed to process CSV file: ${
                error instanceof Error ? error.message : "Unknown error"
              }`
            )
          );
        }
      };
    } else {
      reader.readAsArrayBuffer(file);
    }
  });
};

export const createSampleTemplate = () => {
  const sampleData = [
    ["Page URL", "Issue Type", "Description", "Severity", "Date Found"],
    [
      "https://example.com/page1",
      "Broken Link",
      "Link to external resource is broken",
      "High",
      "2024-01-15",
    ],
    [
      "https://example.com/page2",
      "Missing Alt Text",
      "Image missing alt attribute",
      "Medium",
      "2024-01-16",
    ],
    [
      "https://example.com/page3",
      "Broken Link",
      "Internal link returns 404",
      "High",
      "2024-01-17",
    ],
    [
      "https://example.com/page4",
      "Spelling Error",
      "Typo in main heading",
      "Low",
      "2024-01-18",
    ],
    [
      "https://example.com/page5",
      "Missing Alt Text",
      "Product image missing alt text",
      "Medium",
      "2024-01-19",
    ],
    [
      "https://example.com/page6",
      "Performance Issue",
      "Page load time over 3 seconds",
      "High",
      "2024-01-20",
    ],
    [
      "https://example.com/page7",
      "Spelling Error",
      "Misspelled word in content",
      "Low",
      "2024-01-21",
    ],
    [
      "https://example.com/page8",
      "Accessibility Issue",
      "Missing ARIA labels",
      "Medium",
      "2024-01-22",
    ],
  ];

  const ws = XLSX.utils.aoa_to_sheet(sampleData);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Sample Issues");

  return XLSX.write(wb, { bookType: "xlsx", type: "array" });
};
