import type {
  ProcessedEmailData,
  TimeSlotAnalysis,
  AnalysisResult,
  AnalysisType,
  FilterOptions,
  BestPractice,
} from "../types";
import { formatTimeLabel } from "./validation";

// Best practices based on industry research
const BEST_PRACTICES: BestPractice[] = [
  {
    dayOfWeek: "Tuesday",
    hourOfDay: 10,
    timeLabel: "10:00 AM",
    score: 95,
    reasoning:
      "Peak engagement time - people are settled into work and checking emails",
  },
  {
    dayOfWeek: "Thursday",
    hourOfDay: 14,
    timeLabel: "2:00 PM",
    score: 90,
    reasoning: "Post-lunch period with high email activity",
  },
  {
    dayOfWeek: "Wednesday",
    hourOfDay: 9,
    timeLabel: "9:00 AM",
    score: 85,
    reasoning: "Mid-week morning when inboxes are being cleared",
  },
  {
    dayOfWeek: "Tuesday",
    hourOfDay: 14,
    timeLabel: "2:00 PM",
    score: 82,
    reasoning: "Strong afternoon engagement on Tuesday",
  },
  {
    dayOfWeek: "Thursday",
    hourOfDay: 10,
    timeLabel: "10:00 AM",
    score: 80,
    reasoning: "Late-week morning with good open rates",
  },
];

export function analyzeBestPractices(): AnalysisResult {
  const allTimeSlots: TimeSlotAnalysis[] = BEST_PRACTICES.map((bp) => ({
    dayOfWeek: bp.dayOfWeek,
    hourOfDay: bp.hourOfDay,
    timeLabel: bp.timeLabel,
    avgOpenRate: bp.score,
    avgClickRate: bp.score * 0.3, // Estimate click rate
    sampleSize: 0,
    score: bp.score,
  }));

  return {
    primary: allTimeSlots[0],
    secondary: allTimeSlots[1],
    tertiary: allTimeSlots[2],
    allTimeSlots,
    metadata: {
      totalRecords: 0,
      dateRange: {
        start: new Date(),
        end: new Date(),
      },
      filters: {
        businessUnit: "All",
        organizationType: "All",
        campaignType: "All",
      },
      analysisType: "best-practices",
      timestamp: new Date(),
    },
  };
}

export function analyzeHistoricalData(
  data: ProcessedEmailData[],
  filters: FilterOptions
): AnalysisResult {
  if (data.length === 0) {
    throw new Error("No data available for analysis");
  }

  // Group data by day of week and hour
  const timeSlotMap = new Map<string, ProcessedEmailData[]>();

  for (const row of data) {
    const key = `${row.dayOfWeek}-${row.hourOfDay}`;
    if (!timeSlotMap.has(key)) {
      timeSlotMap.set(key, []);
    }
    timeSlotMap.get(key)!.push(row);
  }

  // Calculate statistics for each time slot
  const timeSlots: TimeSlotAnalysis[] = [];

  for (const [key, records] of timeSlotMap.entries()) {
    const [dayOfWeek, hourStr] = key.split("-");
    const hourOfDay = parseInt(hourStr);

    const avgOpenRate =
      records.reduce((sum, r) => sum + r.openRate, 0) / records.length;
    const avgClickRate =
      records.reduce((sum, r) => sum + r.clickRate, 0) / records.length;

    // Calculate score based on open rate (70%) and click rate (30%)
    const score = avgOpenRate * 0.7 + avgClickRate * 0.3;

    timeSlots.push({
      dayOfWeek,
      hourOfDay,
      timeLabel: formatTimeLabel(hourOfDay),
      avgOpenRate,
      avgClickRate,
      sampleSize: records.length,
      score,
    });
  }

  // Sort by score descending
  timeSlots.sort((a, b) => b.score - a.score);

  // Get date range
  const dates = data.map((r) => r.sendDate.getTime());
  const minDate = new Date(Math.min(...dates));
  const maxDate = new Date(Math.max(...dates));

  return {
    primary: timeSlots[0] || createEmptyTimeSlot(),
    secondary: timeSlots[1] || createEmptyTimeSlot(),
    tertiary: timeSlots[2] || createEmptyTimeSlot(),
    allTimeSlots: timeSlots,
    metadata: {
      totalRecords: data.length,
      dateRange: {
        start: minDate,
        end: maxDate,
      },
      filters,
      analysisType: "historical",
      timestamp: new Date(),
    },
  };
}

export function analyzeCombined(
  data: ProcessedEmailData[],
  filters: FilterOptions
): AnalysisResult {
  if (data.length === 0) {
    // If no historical data, return best practices
    return analyzeBestPractices();
  }

  // Get historical analysis
  const historical = analyzeHistoricalData(data, filters);

  // Get best practices
  const bestPractices = analyzeBestPractices();

  // Combine scores: 60% historical, 40% best practices
  const combinedMap = new Map<string, TimeSlotAnalysis>();

  // Add historical data
  for (const slot of historical.allTimeSlots) {
    const key = `${slot.dayOfWeek}-${slot.hourOfDay}`;
    combinedMap.set(key, {
      ...slot,
      score: slot.score * 0.6,
    });
  }

  // Add or merge best practices
  for (const slot of bestPractices.allTimeSlots) {
    const key = `${slot.dayOfWeek}-${slot.hourOfDay}`;
    const existing = combinedMap.get(key);

    if (existing) {
      // Merge: 60% historical + 40% best practice
      existing.score = existing.score + slot.score * 0.4;
      existing.avgOpenRate =
        existing.avgOpenRate * 0.6 + slot.avgOpenRate * 0.4;
      existing.avgClickRate =
        existing.avgClickRate * 0.6 + slot.avgClickRate * 0.4;
    } else {
      // Add best practice with 40% weight
      combinedMap.set(key, {
        ...slot,
        score: slot.score * 0.4,
        sampleSize: 0,
      });
    }
  }

  // Convert to array and sort
  const allTimeSlots = Array.from(combinedMap.values()).sort(
    (a, b) => b.score - a.score
  );

  return {
    primary: allTimeSlots[0] || createEmptyTimeSlot(),
    secondary: allTimeSlots[1] || createEmptyTimeSlot(),
    tertiary: allTimeSlots[2] || createEmptyTimeSlot(),
    allTimeSlots,
    metadata: {
      totalRecords: data.length,
      dateRange: historical.metadata.dateRange,
      filters,
      analysisType: "combined",
      timestamp: new Date(),
    },
  };
}

export function performAnalysis(
  data: ProcessedEmailData[],
  analysisType: AnalysisType,
  filters: FilterOptions
): AnalysisResult {
  switch (analysisType) {
    case "best-practices":
      return analyzeBestPractices();
    case "historical":
      return analyzeHistoricalData(data, filters);
    case "combined":
      return analyzeCombined(data, filters);
    default:
      throw new Error(`Unknown analysis type: ${analysisType}`);
  }
}

function createEmptyTimeSlot(): TimeSlotAnalysis {
  return {
    dayOfWeek: "N/A",
    hourOfDay: 0,
    timeLabel: "N/A",
    avgOpenRate: 0,
    avgClickRate: 0,
    sampleSize: 0,
    score: 0,
  };
}

// Helper function to get day-hour heatmap data
export function getHeatmapData(data: ProcessedEmailData[]) {
  const days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  const heatmapData = [];

  for (const day of days) {
    for (const hour of hours) {
      const records = data.filter(
        (r) => r.dayOfWeek === day && r.hourOfDay === hour
      );

      if (records.length > 0) {
        const avgOpenRate =
          records.reduce((sum, r) => sum + r.openRate, 0) / records.length;

        heatmapData.push({
          day,
          hour,
          value: avgOpenRate,
          count: records.length,
        });
      }
    }
  }

  return heatmapData;
}

// Helper function to get time distribution data
export function getTimeDistribution(data: ProcessedEmailData[]) {
  const hourCounts = new Map<number, number>();

  for (const row of data) {
    const count = hourCounts.get(row.hourOfDay) || 0;
    hourCounts.set(row.hourOfDay, count + 1);
  }

  return Array.from(hourCounts.entries())
    .map(([hour, count]) => ({
      hour,
      timeLabel: formatTimeLabel(hour),
      count,
    }))
    .sort((a, b) => a.hour - b.hour);
}

// Helper function to get day of week distribution
export function getDayDistribution(data: ProcessedEmailData[]) {
  const dayCounts = new Map<string, { count: number; avgOpenRate: number }>();

  for (const row of data) {
    const existing = dayCounts.get(row.dayOfWeek) || {
      count: 0,
      avgOpenRate: 0,
    };
    existing.count++;
    existing.avgOpenRate += row.openRate;
    dayCounts.set(row.dayOfWeek, existing);
  }

  const days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  return days
    .filter((day) => dayCounts.has(day))
    .map((day) => {
      const data = dayCounts.get(day)!;
      return {
        day,
        count: data.count,
        avgOpenRate: data.avgOpenRate / data.count,
      };
    });
}
