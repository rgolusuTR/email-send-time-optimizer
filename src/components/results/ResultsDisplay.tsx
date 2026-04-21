import { useState } from "react";
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Menu,
  MenuItem,
  Chip,
  Divider,
  Tabs,
  Tab,
} from "@mui/material";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import GetAppIcon from "@mui/icons-material/GetApp";
import BarChartIcon from "@mui/icons-material/BarChart";
import ArticleIcon from "@mui/icons-material/Article";
import type {
  AnalysisResult,
  ProcessedEmailData,
  ExportFormat,
} from "../../types";
import { exportResults } from "../../utils/exportUtils";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import {
  getDayDistribution,
  getTimeDistribution,
} from "../../utils/analysisEngine";
import { generateDetailedInsights } from "../../utils/insightsGenerator";
import { DetailedInsightsDisplay } from "./DetailedInsightsDisplay";

interface ResultsDisplayProps {
  results: AnalysisResult;
  data: ProcessedEmailData[];
}

export function ResultsDisplay({ results, data }: ResultsDisplayProps) {
  const [exportAnchor, setExportAnchor] = useState<null | HTMLElement>(null);
  const [activeTab, setActiveTab] = useState(0);

  const handleExport = async (format: ExportFormat) => {
    try {
      await exportResults(results, format);
      setExportAnchor(null);
    } catch (error) {
      console.error("Export failed:", error);
      alert("Failed to export results. Please try again.");
    }
  };

  const dayDistribution = getDayDistribution(data);
  const timeDistribution = getTimeDistribution(data);
  const detailedInsights = generateDetailedInsights(results, data);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {/* Tabs for different views */}
      <Paper sx={{ p: 0 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<EmojiEventsIcon />} label="Summary & Charts" />
          <Tab icon={<ArticleIcon />} label="Detailed Analysis" />
        </Tabs>
      </Paper>

      {activeTab === 1 && (
        <DetailedInsightsDisplay insights={detailedInsights} />
      )}

      {activeTab === 0 && (
        <>
          {/* Header */}
          <Paper sx={{ p: 3 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <EmojiEventsIcon color="primary" fontSize="large" />
                <Typography variant="h5">Analysis Results</Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<GetAppIcon />}
                onClick={(e) => setExportAnchor(e.currentTarget)}
              >
                Export
              </Button>
              <Menu
                anchorEl={exportAnchor}
                open={Boolean(exportAnchor)}
                onClose={() => setExportAnchor(null)}
              >
                <MenuItem onClick={() => handleExport("pdf")}>
                  Export as PDF
                </MenuItem>
                <MenuItem onClick={() => handleExport("excel")}>
                  Export as Excel
                </MenuItem>
                <MenuItem onClick={() => handleExport("csv")}>
                  Export as CSV
                </MenuItem>
                <MenuItem onClick={() => handleExport("json")}>
                  Export as JSON
                </MenuItem>
              </Menu>
            </Box>

            <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
              <Chip
                label={`${results.metadata.totalRecords.toLocaleString()} records analyzed`}
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`${results.metadata.dateRange.start.toLocaleDateString()} - ${results.metadata.dateRange.end.toLocaleDateString()}`}
                variant="outlined"
              />
            </Box>
          </Paper>

          {/* Top 3 Recommendations */}
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
              gap: 3,
            }}
          >
            <Card
              sx={{
                height: "100%",
                bgcolor: "primary.light",
                color: "primary.contrastText",
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    mb: 2,
                  }}
                >
                  <Typography variant="h3">🥇</Typography>
                  <Typography variant="h6">Primary</Typography>
                </Box>
                <Typography variant="h4" gutterBottom>
                  {results.primary.dayOfWeek}
                </Typography>
                <Typography variant="h5" gutterBottom>
                  {results.primary.timeLabel}
                </Typography>
                <Divider
                  sx={{
                    my: 2,
                    bgcolor: "primary.contrastText",
                    opacity: 0.3,
                  }}
                />
                <Typography variant="body2">
                  Open Rate:{" "}
                  <strong>{results.primary.avgOpenRate.toFixed(1)}%</strong>
                </Typography>
                <Typography variant="body2">
                  Click Rate:{" "}
                  <strong>{results.primary.avgClickRate.toFixed(1)}%</strong>
                </Typography>
                {results.primary.sampleSize > 0 && (
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    Based on {results.primary.sampleSize} emails
                  </Typography>
                )}
              </CardContent>
            </Card>
            <Card
              sx={{
                height: "100%",
                bgcolor: "secondary.light",
                color: "secondary.contrastText",
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    mb: 2,
                  }}
                >
                  <Typography variant="h3">🥈</Typography>
                  <Typography variant="h6">Secondary</Typography>
                </Box>
                <Typography variant="h4" gutterBottom>
                  {results.secondary.dayOfWeek}
                </Typography>
                <Typography variant="h5" gutterBottom>
                  {results.secondary.timeLabel}
                </Typography>
                <Divider
                  sx={{
                    my: 2,
                    bgcolor: "secondary.contrastText",
                    opacity: 0.3,
                  }}
                />
                <Typography variant="body2">
                  Open Rate:{" "}
                  <strong>{results.secondary.avgOpenRate.toFixed(1)}%</strong>
                </Typography>
                <Typography variant="body2">
                  Click Rate:{" "}
                  <strong>{results.secondary.avgClickRate.toFixed(1)}%</strong>
                </Typography>
                {results.secondary.sampleSize > 0 && (
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    Based on {results.secondary.sampleSize} emails
                  </Typography>
                )}
              </CardContent>
            </Card>
            <Card
              sx={{
                height: "100%",
                bgcolor: "warning.light",
                color: "warning.contrastText",
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    mb: 2,
                  }}
                >
                  <Typography variant="h3">🥉</Typography>
                  <Typography variant="h6">Tertiary</Typography>
                </Box>
                <Typography variant="h4" gutterBottom>
                  {results.tertiary.dayOfWeek}
                </Typography>
                <Typography variant="h5" gutterBottom>
                  {results.tertiary.timeLabel}
                </Typography>
                <Divider
                  sx={{
                    my: 2,
                    bgcolor: "warning.contrastText",
                    opacity: 0.3,
                  }}
                />
                <Typography variant="body2">
                  Open Rate:{" "}
                  <strong>{results.tertiary.avgOpenRate.toFixed(1)}%</strong>
                </Typography>
                <Typography variant="body2">
                  Click Rate:{" "}
                  <strong>{results.tertiary.avgClickRate.toFixed(1)}%</strong>
                </Typography>
                {results.tertiary.sampleSize > 0 && (
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    Based on {results.tertiary.sampleSize} emails
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Box>

          {/* Charts */}
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
              <BarChartIcon color="primary" />
              <Typography variant="h6">Performance by Day of Week</Typography>
            </Box>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dayDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip />
                <Legend />
                <Bar
                  yAxisId="left"
                  dataKey="count"
                  fill="#8884d8"
                  name="Email Count"
                />
                <Bar
                  yAxisId="right"
                  dataKey="avgOpenRate"
                  fill="#82ca9d"
                  name="Avg Open Rate %"
                />
              </BarChart>
            </ResponsiveContainer>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
              <BarChartIcon color="primary" />
              <Typography variant="h6">Performance by Time of Day</Typography>
            </Box>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timeLabel" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#8884d8"
                  name="Email Count"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </>
      )}
    </Box>
  );
}
