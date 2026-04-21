# Thomson Reuters Email Configuration Guide

## Current Configuration

The system is now configured for Thomson Reuters email infrastructure:

```yaml
email:
  smtp_server: "smtp.office365.com"
  smtp_port: 587
  use_tls: true
  sender_email: "raju.golusu@thomsonreuters.com"
  sender_password: "your-password-here" # REPLACE THIS
```

## Step 1: Configure Your Password

You need to replace `"your-password-here"` in `config/settings.yaml` with one of these options:

### Option A: Use Your Regular Password (if MFA is not enabled)

```yaml
sender_password: "YourActualPassword123"
```

### Option B: Use App Password (if MFA is enabled - RECOMMENDED)

1. **Go to Microsoft Account Security**: https://account.microsoft.com/security
2. **Enable App Passwords** (if not already enabled)
3. **Generate App Password**:
   - Sign in to your Microsoft account
   - Go to Security → Advanced security options
   - Under "App passwords", click "Create a new app password"
   - Name it "Page Analytics System"
   - Copy the generated password (e.g., "abcd-efgh-ijkl-mnop")
4. **Update config/settings.yaml**:
   ```yaml
   sender_password: "abcd-efgh-ijkl-mnop"
   ```

### Option C: Use OAuth (Advanced - Contact IT)

For enterprise security, you may need OAuth authentication. Contact Thomson Reuters IT for:

- OAuth client credentials
- Tenant-specific configuration
- Enterprise app registration

## Step 2: Test Configuration

1. **Start the application**: `python app.py`
2. **Open**: http://localhost:5000
3. **Go to Configuration page**
4. **Click "Test Email Configuration"**
5. **Enter**: `raju.golusu@thomsonreuters.com`
6. **Click "Send Test Email"**

## Step 3: Alternative SMTP Settings

If Office 365 doesn't work, try these Thomson Reuters SMTP alternatives:

### Internal SMTP Server:

```yaml
smtp_server: "mail.thomsonreuters.com" # or "smtp.thomsonreuters.com"
smtp_port: 587
use_tls: true
```

### Exchange Server:

```yaml
smtp_server: "exchange.thomsonreuters.com"
smtp_port: 587
use_tls: true
```

## Troubleshooting

### "Authentication failed"

- **Check password**: Ensure you're using the correct password or app password
- **Check MFA**: If Multi-Factor Authentication is enabled, you MUST use an app password
- **Contact IT**: Thomson Reuters may have specific authentication requirements

### "Connection refused"

- **Network/Firewall**: Thomson Reuters network may block external SMTP
- **VPN Required**: You may need to be on Thomson Reuters VPN
- **Internal SMTP**: Try using internal SMTP servers listed above

### "SMTP not allowed"

- **Policy Restriction**: Thomson Reuters may restrict SMTP access
- **IT Approval**: You may need IT approval to send emails via SMTP
- **Alternative**: Consider using Thomson Reuters approved email services

## Security Considerations

1. **Never share passwords** in code or configuration files
2. **Use environment variables** for sensitive data:
   ```bash
   set TR_EMAIL_PASSWORD=your-password
   ```
3. **Regular password rotation** as per Thomson Reuters policy
4. **Monitor email usage** for security compliance

## Corporate Compliance

- **Data Privacy**: Ensure email content complies with Thomson Reuters data policies
- **Retention**: Configure email retention according to corporate policies
- **Approval**: Get necessary approvals for automated email systems
- **Monitoring**: Be aware that corporate email may be monitored

## Need Help?

1. **Check application logs**: `logs/app.log`
2. **Contact Thomson Reuters IT**: For SMTP server details and permissions
3. **Network team**: For firewall and connectivity issues
4. **Security team**: For authentication and compliance questions

## Example Working Configuration

```yaml
email:
  smtp_server: "smtp.office365.com"
  smtp_port: 587
  use_tls: true
  sender_email: "raju.golusu@thomsonreuters.com"
  sender_password: "abcd-efgh-ijkl-mnop" # Your actual app password
  sender_name: "Page Analytics Notification System"
  default_admin_email: "raju.golusu@thomsonreuters.com"
  reply_to: "noreply@thomsonreuters.com"
```

Once configured correctly, you should be able to send test emails to any @thomsonreuters.com address.
