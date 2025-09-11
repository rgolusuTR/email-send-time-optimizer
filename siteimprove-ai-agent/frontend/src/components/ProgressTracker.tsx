import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  IconButton,
  Alert,
  Chip,
} from "@mui/material";
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  PlayArrow as PlayIcon,
} from "@mui/icons-material";

interface ProgressStep {
  id: string;
  step: string;
  message: string;
  status: "in_progress" | "success" | "error";
  timestamp: number;
  progress?: number;
}

interface ProgressTrackerProps {
  isVisible: boolean;
  onClose?: () => void;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  isVisible,
  onClose,
}) => {
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const [isExpanded, setIsExpanded] = useState(true);
  const [currentAction, setCurrentAction] = useState<string>("");
  const [overallProgress, setOverallProgress] = useState<number>(0);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    if (isVisible && !websocket) {
      // Connect to WebSocket - use the same host as the current page but with ws protocol
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsHost = window.location.hostname;
      const wsPort =
        window.location.hostname === "localhost"
          ? "8000"
          : window.location.port;
      const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/ws`;

      console.log("Connecting to WebSocket:", wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setWebsocket(ws);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setWebsocket(null);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    }
  }, [isVisible, websocket]);

  const handleWebSocketMessage = (data: any) => {
    const { type, step, message, status, timestamp, progress } = data;

    if (type === "progress_update") {
      const newStep: ProgressStep = {
        id: `${step}-${timestamp}`,
        step,
        message,
        status: status || "in_progress",
        timestamp,
        progress,
      };

      setSteps((prevSteps) => {
        // Remove any existing step with the same step name to avoid duplicates
        const filteredSteps = prevSteps.filter(
          (s) => !s.step.includes(step.split("_")[1])
        );
        return [...filteredSteps, newStep];
      });

      // Update current action based on step
      if (step.startsWith("login_")) {
        setCurrentAction("Logging in to Siteimprove");
      } else if (step.startsWith("scan_")) {
        setCurrentAction("Scanning for broken links");
      }

      // Update overall progress
      if (progress !== undefined) {
        setOverallProgress(progress);
      }
    } else if (type === "completion") {
      const completionStep: ProgressStep = {
        id: `completion-${timestamp}`,
        step: `${data.action}_complete`,
        message: data.message,
        status: "success",
        timestamp,
      };

      setSteps((prevSteps) => [...prevSteps, completionStep]);
      setOverallProgress(100);

      // Auto-close after completion
      setTimeout(() => {
        if (onClose) {
          onClose();
        }
        resetProgress();
      }, 3000);
    } else if (type === "error") {
      const errorStep: ProgressStep = {
        id: `error-${timestamp}`,
        step: data.step || "error",
        message: data.message,
        status: "error",
        timestamp,
      };

      setSteps((prevSteps) => [...prevSteps, errorStep]);
    }
  };

  const resetProgress = () => {
    setSteps([]);
    setCurrentAction("");
    setOverallProgress(0);
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckIcon color="success" />;
      case "error":
        return <ErrorIcon color="error" />;
      case "in_progress":
      default:
        return <PlayIcon color="primary" />;
    }
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case "success":
        return "success";
      case "error":
        return "error";
      case "in_progress":
      default:
        return "primary";
    }
  };

  if (!isVisible || steps.length === 0) {
    return null;
  }

  return (
    <Paper elevation={3} sx={{ mb: 3, overflow: "hidden" }}>
      <Box
        sx={{
          p: 2,
          backgroundColor: "primary.main",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", flex: 1 }}>
          <InfoIcon sx={{ mr: 1 }} />
          <Typography variant="h6" sx={{ flex: 1 }}>
            {currentAction || "Processing..."}
          </Typography>
          <Chip
            label={`${steps.filter((s) => s.status === "success").length}/${
              steps.length
            } steps`}
            size="small"
            sx={{ backgroundColor: "rgba(255,255,255,0.2)", color: "white" }}
          />
        </Box>
        <IconButton
          onClick={() => setIsExpanded(!isExpanded)}
          sx={{ color: "white" }}
        >
          {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      {overallProgress > 0 && (
        <LinearProgress
          variant="determinate"
          value={overallProgress}
          sx={{ height: 4 }}
        />
      )}

      <Collapse in={isExpanded}>
        <Box sx={{ maxHeight: 300, overflow: "auto" }}>
          <List dense>
            {steps.map((step) => (
              <ListItem key={step.id}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {getStepIcon(step.status)}
                </ListItemIcon>
                <ListItemText
                  primary={step.message}
                  secondary={
                    <Box
                      sx={{ display: "flex", alignItems: "center", mt: 0.5 }}
                    >
                      <Chip
                        label={step.status}
                        size="small"
                        color={getStepColor(step.status) as any}
                        variant="outlined"
                        sx={{ mr: 1, fontSize: "0.7rem", height: 20 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {new Date(step.timestamp * 1000).toLocaleTimeString()}
                      </Typography>
                      {step.progress !== undefined && (
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ ml: 1 }}
                        >
                          ({step.progress}%)
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Collapse>

      {steps.some((s) => s.status === "error") && (
        <Alert severity="error" sx={{ m: 2, mt: 0 }}>
          Some steps failed. Please check the details above and try again.
        </Alert>
      )}
    </Paper>
  );
};
