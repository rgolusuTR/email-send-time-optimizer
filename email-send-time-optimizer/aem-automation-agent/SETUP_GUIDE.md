# 🚀 AEM Automation Agent - Setup Guide

This guide will help you configure and use the AEM Automation Agent to automate Adobe Experience Manager page authoring tasks.

## 📋 Prerequisites

1. **AEM Access**: You need access to an Adobe Experience Manager instance
2. **AEM Credentials**: Valid username and password for AEM
3. **Python 3.8+**: Make sure Python is installed on your system
4. **Chrome Browser**: Required for browser automation

## ⚙️ Configuration Steps

### Step 1: Configure AEM Credentials

1. **Open the `.env` file** in the `aem-automation-agent` folder
2. **Update the following values** with your actual AEM credentials:

```env
# AEM Configuration
AEM_BASE_URL=https://your-aem-instance.com/sites.html/content
AEM_USERNAME=your_actual_username
AEM_PASSWORD=your_actual_password

# AI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key

# Browser Configuration
HEADLESS_MODE=false
BROWSER_TIMEOUT=30000
```

### Step 2: Update AEM Base URL

**Important**: Replace the `AEM_BASE_URL` with your actual AEM instance URL:

- **Current**: `https://author-ppe-ams.ewp.thomsonreuters.com/sites.html/content`
- **Update to**: Your organization's AEM URL

Common AEM URL patterns:

- `https://author.your-company.com/sites.html/content`
- `https://your-aem-instance.adobeaemcloud.com/sites.html/content`
- `https://localhost:4502/sites.html/content` (for local AEM)

### Step 3: Test Your Configuration

1. **Start the Web UI**:

   ```bash
   cd aem-automation-agent
   python start_web_ui.py
   ```

2. **Open your browser** to: http://localhost:5000

3. **Click "Initialize Agent"** - You should see:
   - ✅ "Agent browser started successfully"
   - ✅ "Attempting to login to AEM..."
   - ✅ "Successfully logged in to AEM"
   - ✅ "Agent ready for commands"

## 🔧 Troubleshooting

### Issue: "Failed to login to AEM"

**Possible Causes & Solutions:**

1. **Incorrect Credentials**

   - Double-check your username and password
   - Try logging into AEM manually with the same credentials

2. **Wrong AEM URL**

   - Verify the `AEM_BASE_URL` is correct
   - Make sure it includes `/sites.html/content` at the end

3. **Network/VPN Issues**

   - Ensure you can access AEM from your current network
   - Connect to VPN if required by your organization

4. **AEM Instance Down**
   - Check if your AEM instance is running
   - Contact your AEM administrator

### Issue: "Empty screen" when initializing

**Solution:**

- Wait a few seconds for the browser to start
- Check the Activity Logs section for detailed status
- Refresh the page if needed

### Issue: Browser automation fails

**Solutions:**

1. **Install Chrome**: Make sure Google Chrome is installed
2. **Update Chrome**: Ensure you have the latest version
3. **Check Permissions**: Make sure the agent can launch browsers

## 🎯 Usage Examples

Once configured, you can use natural language commands like:

### Basic Page Creation

```
Create a page called 'Product Launch'
```

### Page with Components

```
Create a page called 'News Article' and add an Article Paragraph component
```

### Complete Workflow

```
Create a page called 'About Us', add an Article Paragraph component, and fill it with 'Welcome to our company'
```

## 🔐 Security Notes

1. **Credentials Storage**: Your AEM credentials are stored locally in the `.env` file
2. **Network Security**: The agent connects directly to your AEM instance
3. **Browser Automation**: Uses Chrome in non-headless mode for transparency
4. **Local Only**: The web UI runs locally on your machine (localhost:5000)

## 📞 Support

If you encounter issues:

1. **Check the Activity Logs** in the web UI for detailed error messages
2. **Verify your AEM credentials** by logging in manually
3. **Ensure network connectivity** to your AEM instance
4. **Check browser compatibility** (Chrome required)

## 🚀 Next Steps

Once setup is complete:

1. **Test with simple commands** first
2. **Use the "Test Parser" button** to preview actions
3. **Monitor the Activity Logs** for execution details
4. **Take screenshots** to verify results

---

**Ready to automate your AEM page authoring! 🎉**
