import React, { useState, useEffect } from "react";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
} from "@mui/material";
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  BugReport as BugIcon,
  Analytics as AnalyticsIcon,
} from "@mui/icons-material";
import { PromptInterface } from "./components/PromptInterface";
import { DataTable } from "./components/DataTable";
import { StatusCard } from "./components/StatusCard";
import { MockProgressDemo } from "./components/MockProgressDemo";
import { apiService } from "./services/apiService";
import { BrokenLink, SystemStatus } from "./types/types";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
    background: {
      default: "#f5f5f5",
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [brokenLinks, setBrokenLinks] = useState<BrokenLink[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [lastResponse, setLastResponse] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [showProgress, setShowProgress] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const statusData = await apiService.getStatus();
      setStatus(statusData);
    } catch (err) {
      console.error("Failed to fetch status:", err);
    }
  };

  const handlePromptSubmit = async (prompt: string) => {
    setLoading(true);
    setError("");

    // Show progress tracker for login and scan operations
    const lowerPrompt = prompt.toLowerCase();
    if (
      lowerPrompt.includes("login") ||
      lowerPrompt.includes("scan") ||
      lowerPrompt.includes("broken links")
    ) {
      setShowProgress(true);
    }

    try {
      const response = await apiService.processPrompt(prompt);

      if (response.success) {
        setLastResponse(response.message);

        // If the response contains broken links data, update the table
        if (response.data?.broken_links) {
          setBrokenLinks(response.data.broken_links);
        }

        // Refresh status after any action
        await fetchStatus();
      } else {
        setError(response.message);
        setShowProgress(false); // Hide progress on error
      }
    } catch (err) {
      setError("Failed to process command. Please try again.");
      setShowProgress(false); // Hide progress on error
      console.error("Prompt processing error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBrokenLinks = async () => {
    setLoading(true);
    try {
      const response = await apiService.getBrokenLinks();
      setBrokenLinks(response.data);
      setLastResponse(`Retrieved ${response.data.length} broken link entries`);
    } catch (err) {
      setError("Failed to fetch broken links data");
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <BotIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Siteimprove AI Agent
          </Typography>
          <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>
            Natural Language Interface for Broken Links Management
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        {/* Status Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatusCard
              title="System Status"
              value={status?.logged_in ? "Connected" : "Disconnected"}
              icon={<BotIcon />}
              color={status?.logged_in ? "success" : "error"}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatusCard
              title="Cached Entries"
              value={status?.cached_entries || 0}
              icon={<BugIcon />}
              color="info"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatusCard
              title="Last Scan"
              value={
                status?.last_scan
                  ? new Date(status.last_scan).toLocaleString()
                  : "Never"
              }
              icon={<AnalyticsIcon />}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatusCard
              title="Browser Status"
              value={status?.browser_active ? "Active" : "Inactive"}
              icon={<BugIcon />}
              color={status?.browser_active ? "success" : "warning"}
            />
          </Grid>
        </Grid>

        {/* Prompt Interface */}
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography
            variant="h6"
            gutterBottom
            sx={{ display: "flex", alignItems: "center" }}
          >
            <BotIcon sx={{ mr: 1 }} />
            Command Interface
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter natural language commands to control Siteimprove automation
          </Typography>

          <PromptInterface
            onSubmit={handlePromptSubmit}
            loading={loading}
            placeholder="Enter your command (e.g., 'Show me broken links with more than 5 clicks')"
          />

          {/* Quick Action Buttons */}
          <Box sx={{ mt: 2, display: "flex", gap: 1, flexWrap: "wrap" }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => handlePromptSubmit("Login to Siteimprove")}
              disabled={loading}
            >
              Login
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => handlePromptSubmit("Show me broken links")}
              disabled={loading}
            >
              Scan Broken Links
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => handlePromptSubmit("Export to CSV")}
              disabled={loading}
            >
              Export CSV
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => handlePromptSubmit("help")}
              disabled={loading}
            >
              Help
            </Button>
          </Box>
        </Paper>

        {/* Progress Tracker */}
        <MockProgressDemo
          isVisible={showProgress}
          onClose={() => setShowProgress(false)}
        />

        {/* Response Display */}
        {(lastResponse || error) && (
          <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            {error ? (
              <Alert severity="error" onClose={() => setError("")}>
                {error}
              </Alert>
            ) : (
              <Alert severity="success" onClose={() => setLastResponse("")}>
                {lastResponse}
              </Alert>
            )}
          </Paper>
        )}

        {/* Loading Indicator */}
        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
            <CircularProgress />
            <Typography variant="body2" sx={{ ml: 2, alignSelf: "center" }}>
              Processing your request...
            </Typography>
          </Box>
        )}

        {/* Data Table */}
        {brokenLinks.length > 0 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Broken Links Report
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {brokenLinks.length} pages with broken links found
            </Typography>
            <DataTable data={brokenLinks} />
          </Paper>
        )}

        {/* Example Commands */}
        {brokenLinks.length === 0 && !loading && (
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Example Commands
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Try these natural language commands:
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                {[
                  "Login to Siteimprove",
                  "Show me broken links",
                  "Show broken links with more than 10 clicks",
                  "Export to CSV",
                  "Which pages have the most broken links?",
                  "Filter by page level 2",
                  "Help",
                ].map((command) => (
                  <Chip
                    key={command}
                    label={command}
                    variant="outlined"
                    clickable
                    onClick={() => handlePromptSubmit(command)}
                    disabled={loading}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
