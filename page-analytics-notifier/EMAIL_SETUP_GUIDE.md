# Email Configuration Setup Guide

This guide will help you configure email settings for the Page Analytics Notifier system.

## Quick Setup Options

### Option 1: Gmail with App Password (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Update config/settings.yaml**:
   ```yaml
   email:
     smtp_server: "smtp.gmail.com"
     smtp_port: 587
     use_tls: true
     sender_email: "your-email@gmail.com"
     sender_password: "your-16-digit-app-password"
     sender_name: "Page Analytics System"
   ```

### Option 2: SendGrid (For Production)

1. **Create SendGrid Account** at https://sendgrid.com
2. **Generate API Key** in SendGrid dashboard
3. **Update config/settings.yaml**:
   ```yaml
   email:
     sendgrid_api_key: "your-sendgrid-api-key"
     sender_email: "noreply@yourdomain.com"
     sender_name: "Page Analytics System"
   ```

### Option 3: Other SMTP Providers

For other email providers, update these settings:

```yaml
email:
  smtp_server: "your-smtp-server.com"
  smtp_port: 587 # or 465 for SSL
  use_tls: true # or false for SSL
  sender_email: "your-email@domain.com"
  sender_password: "your-password"
  sender_name: "Page Analytics System"
```

## Common SMTP Settings

| Provider   | SMTP Server           | Port | Security |
| ---------- | --------------------- | ---- | -------- |
| Gmail      | smtp.gmail.com        | 587  | TLS      |
| Outlook    | smtp-mail.outlook.com | 587  | TLS      |
| Yahoo      | smtp.mail.yahoo.com   | 587  | TLS      |
| Office 365 | smtp.office365.com    | 587  | TLS      |

## Testing Email Configuration

1. **Start the application**: `python app.py`
2. **Open the web interface**: http://localhost:5000
3. **Go to Configuration page**
4. **Click "Test Email Configuration"**
5. **Enter your email address** to receive a test email

## Troubleshooting

### "SMTP credentials not configured" Error

- Check that `sender_email` and `sender_password` are not empty
- Verify the credentials are correct

### "Authentication failed" Error

- For Gmail: Use App Password, not regular password
- For other providers: Check username/password
- Verify 2FA settings if enabled

### "Connection refused" Error

- Check SMTP server and port settings
- Verify firewall/network settings
- Try different ports (587, 465, 25)

### "SSL/TLS" Errors

- Try toggling `use_tls` setting
- Check if provider requires SSL instead of TLS

## Security Best Practices

1. **Use App Passwords** instead of regular passwords
2. **Enable 2-Factor Authentication** on email accounts
3. **Use dedicated email accounts** for system notifications
4. **Regularly rotate passwords** and API keys
5. **Monitor email usage** for suspicious activity

## Email Templates

The system uses HTML email templates located in:

- `config/email_templates/expired_page.html`
- `config/email_templates/low_engagement.html`

You can customize these templates to match your organization's branding.

## Support

If you continue to have issues:

1. Check the application logs in `logs/app.log`
2. Verify your email provider's documentation
3. Test with a simple email client first
4. Consider using SendGrid for production environments
