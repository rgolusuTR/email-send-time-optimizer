import {
  Drawer,
  Typography,
  Box,
  IconButton,
  Switch,
  FormControlLabel,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useAppStore } from "../../store/useAppStore";

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}

export function SettingsPanel({ open, onClose }: SettingsPanelProps) {
  const { settings, updateSettings } = useAppStore();

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 400, p: 3 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h6">Settings</Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.enableTimezone}
                onChange={(e) =>
                  updateSettings({ enableTimezone: e.target.checked })
                }
              />
            }
            label="Enable Timezone Filter"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.autoSaveResults}
                onChange={(e) =>
                  updateSettings({ autoSaveResults: e.target.checked })
                }
              />
            }
            label="Auto-save Analysis Results"
          />
        </Box>
      </Box>
    </Drawer>
  );
}
