// Charts functionality for Siteimprove Dashboard
class DashboardCharts {
  constructor() {
    this.charts = {};
    this.initializeCharts();
  }

  initializeCharts() {
    // Initialize trend chart
    this.initTrendChart();

    // Initialize top words chart
    this.initTopWordsChart();

    // Initialize language distribution chart
    this.initLanguageChart();
  }

  initTrendChart() {
    const ctx = document.getElementById("trendChart");
    if (!ctx) return;

    this.charts.trend = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Misspellings",
            data: [],
            borderColor: "#6f42c1",
            backgroundColor: "rgba(111, 66, 193, 0.1)",
            tension: 0.4,
          },
          {
            label: "Words to Review",
            data: [],
            borderColor: "#20c997",
            backgroundColor: "rgba(32, 201, 151, 0.1)",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
          title: {
            display: true,
            text: "Trends Over Time",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  initTopWordsChart() {
    const ctx = document.getElementById("topWordsChart");
    if (!ctx) return;

    this.charts.topWords = new Chart(ctx, {
      type: "bar",
      data: {
        labels: [],
        datasets: [
          {
            label: "Occurrences",
            data: [],
            backgroundColor: [
              "#6f42c1",
              "#20c997",
              "#fd7e14",
              "#e83e8c",
              "#6610f2",
              "#6f42c1",
              "#20c997",
              "#fd7e14",
              "#e83e8c",
              "#6610f2",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          title: {
            display: true,
            text: "Top Misspelled Words",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  initLanguageChart() {
    const ctx = document.getElementById("languageChart");
    if (!ctx) return;

    this.charts.language = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: [],
        datasets: [
          {
            data: [],
            backgroundColor: [
              "#6f42c1",
              "#20c997",
              "#fd7e14",
              "#e83e8c",
              "#6610f2",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
          },
          title: {
            display: true,
            text: "Language Distribution",
          },
        },
      },
    });
  }

  updateTrendChart(data) {
    if (!this.charts.trend) return;

    const chart = this.charts.trend;
    chart.data.labels = data.labels || [];
    chart.data.datasets[0].data = data.misspellings || [];
    chart.data.datasets[1].data = data.words_to_review || [];
    chart.update();
  }

  updateTopWordsChart(data) {
    if (!this.charts.topWords) return;

    const chart = this.charts.topWords;
    chart.data.labels = data.map((item) => item.word || "");
    chart.data.datasets[0].data = data.map((item) => item.count || 0);
    chart.update();
  }

  updateLanguageChart(data) {
    if (!this.charts.language) return;

    const chart = this.charts.language;
    chart.data.labels = data.map((item) => item.language || "");
    chart.data.datasets[0].data = data.map((item) => item.count || 0);
    chart.update();
  }

  updateAllCharts(dashboardData) {
    if (dashboardData.trend_data) {
      this.updateTrendChart(dashboardData.trend_data);
    }

    if (dashboardData.top_words) {
      this.updateTopWordsChart(dashboardData.top_words);
    }

    if (dashboardData.language_distribution) {
      this.updateLanguageChart(dashboardData.language_distribution);
    }
  }
}

// Initialize charts when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  window.dashboardCharts = new DashboardCharts();
});
