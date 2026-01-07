import { Paper, Typography, Box, Divider, Alert, Chip } from "@mui/material";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import WarningIcon from "@mui/icons-material/Warning";
import TipsAndUpdatesIcon from "@mui/icons-material/TipsAndUpdates";
import type { DetailedInsights } from "../../utils/insightsGenerator";
import ReactMarkdown from "react-markdown";

interface DetailedInsightsDisplayProps {
  insights: DetailedInsights;
}

export function DetailedInsightsDisplay({
  insights,
}: DetailedInsightsDisplayProps) {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {/* Summary */}
      <Paper sx={{ p: 3, bgcolor: "info.light" }}>
        <Typography variant="h6" gutterBottom>
          📊 Your Historical Performance Analysis
        </Typography>
        <Typography variant="body1">{insights.summary}</Typography>
      </Paper>

      {/* Data Processing & Analysis */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom color="primary">
          ## Data Processing & Analysis
        </Typography>
        <Divider sx={{ my: 2 }} />

        {/* Day of Week Analysis */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            ### 1. **Day of Week Performance**
          </Typography>
          <Typography
            component="div"
            variant="body2"
            sx={{ whiteSpace: "pre-line", pl: 2 }}
          >
            <ReactMarkdown>{insights.dayOfWeekAnalysis}</ReactMarkdown>
          </Typography>
        </Box>

        {/* Time of Day Analysis */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            ### 2. **Time of Day Performance**
          </Typography>
          <Typography
            component="div"
            variant="body2"
            sx={{ whiteSpace: "pre-line", pl: 2 }}
          >
            <ReactMarkdown>{insights.timeOfDayAnalysis}</ReactMarkdown>
          </Typography>
        </Box>

        {/* Top 3 Optimal Send Times */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            ### 3. **Top 3 Optimal Send Times**
          </Typography>
          <Typography
            component="div"
            variant="body2"
            sx={{ whiteSpace: "pre-line", pl: 2 }}
          >
            <ReactMarkdown>{insights.topSendTimes}</ReactMarkdown>
          </Typography>
        </Box>

        {/* Times to AVOID */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            ### 4. **Times to AVOID**
          </Typography>
          <Typography
            component="div"
            variant="body2"
            sx={{ whiteSpace: "pre-line", pl: 2 }}
          >
            <ReactMarkdown>{insights.timesToAvoid}</ReactMarkdown>
          </Typography>
        </Box>

        {/* Notable Patterns & Insights */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            ### 5. **Notable Patterns & Insights**
          </Typography>
          <Typography
            component="div"
            variant="body2"
            sx={{ whiteSpace: "pre-line", pl: 2 }}
          >
            <ReactMarkdown>{insights.notablePatterns}</ReactMarkdown>
          </Typography>

          {insights.seasonalPatterns && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" fontWeight="bold">
                #### Seasonal Patterns:
              </Typography>
              <Typography
                component="div"
                variant="body2"
                sx={{ whiteSpace: "pre-line", pl: 2 }}
              >
                <ReactMarkdown>{insights.seasonalPatterns}</ReactMarkdown>
              </Typography>
            </Box>
          )}

          {insights.performanceMetrics && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" fontWeight="bold">
                #### Performance Metrics Context:
              </Typography>
              <Typography
                component="div"
                variant="body2"
                sx={{ whiteSpace: "pre-line", pl: 2 }}
              >
                <ReactMarkdown>{insights.performanceMetrics}</ReactMarkdown>
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Actionable Recommendations */}
      <Paper sx={{ p: 3, bgcolor: "success.light" }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <TipsAndUpdatesIcon />
          <Typography variant="h6">
            🎯 **Actionable Recommendations**
          </Typography>
        </Box>
        <Divider sx={{ my: 2 }} />
        <Typography
          component="div"
          variant="body2"
          sx={{ whiteSpace: "pre-line" }}
        >
          <ReactMarkdown>{insights.actionableRecommendations}</ReactMarkdown>
        </Typography>

        {insights.expectedImpact && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              ### Expected Impact:
            </Typography>
            <Typography
              component="div"
              variant="body2"
              sx={{ whiteSpace: "pre-line", pl: 2 }}
            >
              <ReactMarkdown>{insights.expectedImpact}</ReactMarkdown>
            </Typography>
          </Box>
        )}

        {insights.specialConsiderations && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              ### Special Considerations:
            </Typography>
            <Typography
              component="div"
              variant="body2"
              sx={{ whiteSpace: "pre-line", pl: 2 }}
            >
              <ReactMarkdown>{insights.specialConsiderations}</ReactMarkdown>
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Bottom Line */}
      <Paper sx={{ p: 3, bgcolor: "warning.light" }}>
        <Typography variant="h6" gutterBottom>
          ---
        </Typography>
        <Typography variant="body1" fontWeight="bold">
          {insights.bottomLine}
        </Typography>
      </Paper>

      {/* Key Insights */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <LightbulbIcon color="primary" />
          <Typography variant="h6">💡 Key Insights</Typography>
        </Box>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {insights.keyInsights.map((insight, index) => (
            <Typography key={index} variant="body2">
              • {insight}
            </Typography>
          ))}
        </Box>
      </Paper>

      {/* Times to Avoid */}
      <Alert severity="warning" icon={<WarningIcon />}>
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
          ⚠️ Times to Avoid:
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}>
          {insights.timesToAvoidList.map((time, index) => (
            <Chip key={index} label={time} size="small" color="warning" />
          ))}
        </Box>
      </Alert>

      {/* Pro Tips */}
      <Paper sx={{ p: 3, bgcolor: "info.light" }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <TipsAndUpdatesIcon />
          <Typography variant="h6">📝 Pro Tips</Typography>
        </Box>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {insights.proTips.map((tip, index) => (
            <Typography key={index} variant="body2">
              • {tip}
            </Typography>
          ))}
        </Box>
      </Paper>
    </Box>
  );
}
