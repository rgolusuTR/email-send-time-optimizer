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
  Button,
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

interface MockProgressDemoProps {
  isVisible: boolean;
  onClose?: () => void;
}

export const MockProgressDemo: React.FC<MockProgressDemoProps> = ({
  isVisible,
  onClose,
}) => {
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const [isExpanded, setIsExpanded] = useState(true);
  const [currentAction, setCurrentAction] = useState<string>("");
  const [overallProgress, setOverallProgress] = useState<number>(0);
  const [isRunning, setIsRunning] = useState(false);

  const mockLoginSteps = [
    {
      step: "start",
      message: "🚀 Initializing browser and starting login process...",
      delay: 500,
    },
    {
      step: "navigate",
      message: "🌐 Navigating to Siteimprove homepage...",
      delay: 1000,
    },
    {
      step: "page_loaded",
      message: "✅ Homepage loaded successfully",
      delay: 800,
    },
    {
      step: "email_step",
      message: "📧 Entering email credentials...",
      delay: 1200,
    },
    {
      step: "email_entered",
      message: "✅ Email entered successfully",
      delay: 600,
    },
    {
      step: "continue_clicked",
      message: "✅ Continue button clicked, proceeding to password...",
      delay: 800,
    },
    { step: "password_step", message: "🔐 Entering password...", delay: 1000 },
    {
      step: "password_entered",
      message: "✅ Password entered successfully",
      delay: 600,
    },
    {
      step: "login_submit",
      message: "🔄 Submitting login credentials...",
      delay: 1500,
    },
    {
      step: "verifying",
      message: "🔍 Verifying login success and loading dashboard...",
      delay: 2000,
    },
    {
      step: "success",
      message: "🎉 Login successful! Dashboard loaded and ready to use.",
      delay: 500,
    },
  ];

  useEffect(() => {
    if (isVisible && !isRunning) {
      // Small delay to ensure the component is rendered
      setTimeout(() => {
        startMockProgress();
      }, 100);
    }
  }, [isVisible, isRunning]);

  const startMockProgress = async () => {
    setIsRunning(true);
    setCurrentAction("Logging in to Siteimprove");
    setSteps([]);
    setOverallProgress(0);

    for (let i = 0; i < mockLoginSteps.length; i++) {
      const stepData = mockLoginSteps[i];
      const progress = Math.round(((i + 1) / mockLoginSteps.length) * 100);

      await new Promise((resolve) => setTimeout(resolve, stepData.delay));

      const newStep: ProgressStep = {
        id: `${stepData.step}-${Date.now()}`,
        step: stepData.step,
        message: stepData.message,
        status: i === mockLoginSteps.length - 1 ? "success" : "in_progress",
        timestamp: Date.now() / 1000,
        progress: progress,
      };

      setSteps((prevSteps) => [...prevSteps, newStep]);
      setOverallProgress(progress);
    }

    // Auto-close after completion
    setTimeout(() => {
      if (onClose) {
        onClose();
      }
      resetProgress();
    }, 3000);
  };

  const resetProgress = () => {
    setSteps([]);
    setCurrentAction("");
    setOverallProgress(0);
    setIsRunning(false);
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

  if (!isVisible) {
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
          {steps.length === 0 && !isRunning && (
            <Box sx={{ p: 2, textAlign: "center" }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                This is a demo of the visual progress tracker. Click the button
                below to see how it works during login.
              </Typography>
              <Button
                variant="contained"
                onClick={startMockProgress}
                disabled={isRunning}
              >
                Start Demo Login Process
              </Button>
            </Box>
          )}

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
