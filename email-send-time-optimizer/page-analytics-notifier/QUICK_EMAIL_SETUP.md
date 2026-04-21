# Quick Email Setup Guide

## Step 1: Configure Your Email Credentials

Edit the file `config/settings.yaml` and replace the placeholder values:

```yaml
email:
  sender_email: "your.actual.email@gmail.com" # Replace with your Gmail
  sender_password: "your-actual-app-password" # Replace with Gmail App Password
```

## Step 2: Get Gmail App Password

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Scroll down to "App passwords"
   - Select "Mail" and generate password
   - Copy the 16-digit password (e.g., "abcd efgh ijkl mnop")

## Step 3: Example Configuration

Here's a working example configuration:

```yaml
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  use_tls: true
  sender_email: "myemail@gmail.com" # Your actual Gmail
  sender_password: "abcd efgh ijkl mnop" # Your actual app password
  sender_name: "Page Analytics Notification System"

  # Optional: Add emails to receive copies
  cc_emails: ["manager@company.com"] # CC these emails
  bcc_emails: ["admin@company.com"] # BCC these emails
  reply_to: "noreply@company.com" # Reply-to address
```

## Step 4: Alternative Email Providers

### For Outlook/Hotmail:

```yaml
email:
  smtp_server: "smtp-mail.outlook.com"
  smtp_port: 587
  use_tls: true
  sender_email: "your-email@outlook.com"
  sender_password: "your-password"
```

### For Yahoo:

```yaml
email:
  smtp_server: "smtp.mail.yahoo.com"
  smtp_port: 587
  use_tls: true
  sender_email: "your-email@yahoo.com"
  sender_password: "your-app-password"
```

### For SendGrid (Production):

```yaml
email:
  sendgrid_api_key: "SG.your-sendgrid-api-key"
  sender_email: "noreply@yourdomain.com"
  sender_name: "Page Analytics System"
```

## Step 5: Test Your Configuration

1. Start the application: `python app.py`
2. Open: http://localhost:5000
3. Go to "Configuration" page
4. Click "Test Email Configuration"
5. Enter your email address
6. Check if you receive the test email

## Step 6: Customize Email Templates

Edit these files to customize email content:

- `config/email_templates/expired_page.html`
- `config/email_templates/low_engagement.html`

## Troubleshooting

### "Email credentials contain placeholder values"

- Make sure you replaced `your.email@gmail.com` with your actual email
- Make sure you replaced `your-app-password-here` with your actual app password

### "Authentication failed"

- For Gmail: Use App Password, not regular password
- Check if 2-Factor Authentication is enabled
- Verify the email and password are correct

### "Connection refused"

- Check your internet connection
- Verify SMTP server and port settings
- Try different ports: 587 (TLS) or 465 (SSL)

## Security Tips

1. **Never share your app password**
2. **Use dedicated email account** for notifications
3. **Regularly rotate passwords**
4. **Monitor email usage** for suspicious activity

## Need Help?

Check the application logs in `logs/app.log` for detailed error messages.
