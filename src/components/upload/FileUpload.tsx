import { useCallback } from "react";
import {
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Chip,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  isLoading: boolean;
  currentFile: File | null;
}

export function FileUpload({
  onFileUpload,
  isLoading,
  currentFile,
}: FileUploadProps) {
  const handleFileChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file) {
        onFileUpload(file);
      }
    },
    [onFileUpload]
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      const file = event.dataTransfer.files?.[0];
      if (file) {
        onFileUpload(file);
      }
    },
    [onFileUpload]
  );

  const handleDragOver = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
    },
    []
  );

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload Email Data
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Upload a CSV or Excel file containing your email campaign data
      </Typography>

      <Box
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        sx={{
          border: "2px dashed",
          borderColor: "primary.main",
          borderRadius: 2,
          p: 4,
          textAlign: "center",
          bgcolor: "background.default",
          cursor: "pointer",
          transition: "all 0.3s",
          "&:hover": {
            bgcolor: "action.hover",
          },
        }}
      >
        {isLoading ? (
          <Box>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography>Processing file...</Typography>
          </Box>
        ) : (
          <>
            <CloudUploadIcon
              sx={{ fontSize: 48, color: "primary.main", mb: 2 }}
            />
            <Typography variant="h6" gutterBottom>
              Drag & Drop or Click to Upload
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Supports CSV, XLSX, and XLS files (up to 100MB)
            </Typography>
            <Button
              variant="contained"
              component="label"
              startIcon={<CloudUploadIcon />}
            >
              Choose File
              <input
                type="file"
                hidden
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
              />
            </Button>
          </>
        )}
      </Box>

      {currentFile && !isLoading && (
        <Box sx={{ mt: 2, display: "flex", alignItems: "center", gap: 1 }}>
          <InsertDriveFileIcon color="primary" />
          <Typography variant="body2">
            Current file: <strong>{currentFile.name}</strong>
          </Typography>
          <Chip
            label={`${(currentFile.size / 1024 / 1024).toFixed(2)} MB`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
      )}

      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary" display="block">
          Required columns: Business Unit, Organization Type, Campaign Type,
          Send Date, Send Time, Open Rate
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          Optional columns: Click Rate, Unsubscribe Rate, Bounce Rate
        </Typography>
      </Box>
    </Paper>
  );
}
