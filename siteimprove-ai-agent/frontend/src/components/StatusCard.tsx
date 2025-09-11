import React from "react";
import { Card, CardContent, Typography, Box, Avatar } from "@mui/material";

interface StatusCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: "primary" | "secondary" | "error" | "warning" | "info" | "success";
}

export const StatusCard: React.FC<StatusCardProps> = ({
  title,
  value,
  icon,
  color,
}) => {
  const getColorHex = (color: string) => {
    const colors = {
      primary: "#1976d2",
      secondary: "#dc004e",
      error: "#d32f2f",
      warning: "#ed6c02",
      info: "#0288d1",
      success: "#2e7d32",
    };
    return colors[color as keyof typeof colors] || colors.primary;
  };

  return (
    <Card elevation={2} sx={{ height: "100%" }}>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
          <Avatar
            sx={{
              bgcolor: getColorHex(color),
              width: 40,
              height: 40,
              mr: 2,
            }}
          >
            {icon}
          </Avatar>
          <Box>
            <Typography variant="h6" component="div">
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};
