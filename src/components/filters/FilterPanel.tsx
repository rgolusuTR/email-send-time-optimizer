import {
  Paper,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import type { ProcessedEmailData, FilterOptions } from "../../types";
import { getUniqueValues } from "../../utils/dataParser";
import { useAppStore } from "../../store/useAppStore";

interface FilterPanelProps {
  data: ProcessedEmailData[];
  filters: FilterOptions;
  onChange: (filters: FilterOptions) => void;
  onAnalyze?: () => void;
}

export function FilterPanel({
  data,
  filters,
  onChange,
  onAnalyze,
}: FilterPanelProps) {
  const { settings } = useAppStore();

  const businessUnits = ["All", ...getUniqueValues(data, "businessUnit")];
  const organizationTypes = [
    "All",
    ...getUniqueValues(data, "organizationType"),
  ];
  const campaignTypes = ["All", ...getUniqueValues(data, "campaignType")];

  const timezones = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
    "Australia/Sydney",
  ];

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
        <FilterListIcon color="primary" />
        <Typography variant="h6">Filters</Typography>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Refine your analysis by filtering the data
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            md: "repeat(4, 1fr)",
          },
          gap: 2,
        }}
      >
        <Box>
          <FormControl fullWidth>
            <InputLabel>Business Unit</InputLabel>
            <Select
              value={filters.businessUnit}
              label="Business Unit"
              onChange={(e) =>
                onChange({ ...filters, businessUnit: e.target.value })
              }
            >
              {businessUnits.map((unit) => (
                <MenuItem key={unit} value={unit}>
                  {unit}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        <Box>
          <FormControl fullWidth>
            <InputLabel>Organization Type</InputLabel>
            <Select
              value={filters.organizationType}
              label="Organization Type"
              onChange={(e) =>
                onChange({ ...filters, organizationType: e.target.value })
              }
            >
              {organizationTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        <Box>
          <FormControl fullWidth>
            <InputLabel>Campaign Type</InputLabel>
            <Select
              value={filters.campaignType}
              label="Campaign Type"
              onChange={(e) =>
                onChange({ ...filters, campaignType: e.target.value })
              }
            >
              {campaignTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {settings.enableTimezone && (
          <Box>
            <FormControl fullWidth>
              <InputLabel>Timezone (Optional)</InputLabel>
              <Select
                value={filters.timezone || ""}
                label="Timezone (Optional)"
                onChange={(e) =>
                  onChange({
                    ...filters,
                    timezone: e.target.value || undefined,
                  })
                }
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {timezones.map((tz) => (
                  <MenuItem key={tz} value={tz}>
                    {tz}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        )}
      </Box>

      {onAnalyze && (
        <Box sx={{ mt: 3, display: "flex", justifyContent: "center" }}>
          <Button
            variant="contained"
            size="large"
            onClick={onAnalyze}
            sx={{ minWidth: 300 }}
          >
            Get Send Time Recommendations
          </Button>
        </Box>
      )}
    </Paper>
  );
}
