import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  InputAdornment,
  IconButton,
} from "@mui/material";
import { Send as SendIcon, Mic as MicIcon } from "@mui/icons-material";

interface PromptInterfaceProps {
  onSubmit: (prompt: string) => void;
  loading?: boolean;
  placeholder?: string;
}

export const PromptInterface: React.FC<PromptInterfaceProps> = ({
  onSubmit,
  loading = false,
  placeholder = "Enter your command...",
}) => {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !loading) {
      onSubmit(prompt.trim());
      setPrompt("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
      <TextField
        fullWidth
        multiline
        maxRows={4}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={loading}
        variant="outlined"
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                type="submit"
                disabled={!prompt.trim() || loading}
                color="primary"
                size="large"
              >
                <SendIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          "& .MuiOutlinedInput-root": {
            paddingRight: "8px",
          },
        }}
      />
    </Box>
  );
};
