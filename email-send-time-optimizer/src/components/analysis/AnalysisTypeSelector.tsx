import {
  Paper,
  ToggleButtonGroup,
  ToggleButton,
  Typography,
  Box,
} from "@mui/material";
import TipsAndUpdatesIcon from "@mui/icons-material/TipsAndUpdates";
import BarChartIcon from "@mui/icons-material/BarChart";
import MergeTypeIcon from "@mui/icons-material/MergeType";
import type { AnalysisType } from "../../types";

interface AnalysisTypeSelectorProps {
  value: AnalysisType;
  onChange: (value: AnalysisType) => void;
}

export function AnalysisTypeSelector({
  value,
  onChange,
}: AnalysisTypeSelectorProps) {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Analysis Type
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Choose how to determine the best send times for your emails
      </Typography>
      <ToggleButtonGroup
        value={value}
        exclusive
        onChange={(_, newValue) => {
          if (newValue !== null) {
            onChange(newValue as AnalysisType);
          }
        }}
        fullWidth
        sx={{ flexWrap: "wrap" }}
      >
        <ToggleButton value="best-practices" sx={{ flex: "1 1 200px" }}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 1,
            }}
          >
            <TipsAndUpdatesIcon />
            <Box>
              <Typography variant="body2" fontWeight="bold">
                Best Practices
              </Typography>
              <Typography variant="caption" display="block">
                Industry standards
              </Typography>
            </Box>
          </Box>
        </ToggleButton>
        <ToggleButton value="historical" sx={{ flex: "1 1 200px" }}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 1,
            }}
          >
            <BarChartIcon />
            <Box>
              <Typography variant="body2" fontWeight="bold">
                Historical Data
              </Typography>
              <Typography variant="caption" display="block">
                Your past performance
              </Typography>
            </Box>
          </Box>
        </ToggleButton>
        <ToggleButton value="combined" sx={{ flex: "1 1 200px" }}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 1,
            }}
          >
            <MergeTypeIcon />
            <Box>
              <Typography variant="body2" fontWeight="bold">
                Combined
              </Typography>
              <Typography variant="caption" display="block">
                Best of both worlds
              </Typography>
            </Box>
          </Box>
        </ToggleButton>
      </ToggleButtonGroup>
    </Paper>
  );
}
