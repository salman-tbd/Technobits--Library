"""
Email service using SendinBlue (Brevo) API for sending emails.
"""
import os
import logging
from typing import Optional
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings

logger = logging.getLogger(__name__)


class SendinBlueEmailService:
    """SendinBlue email service for sending transactional emails."""
    
    def __init__(self):
        # Configure API key authorization: api-key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.getenv('SENDINBLUE_API_KEY')
        
        # Create an instance of the API class
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
    
    def send_password_reset_email(
        self, 
        to_email: str, 
        to_name: str, 
        reset_url: str
    ) -> bool:
        """
        Send password reset email using SendinBlue.
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            reset_url: Password reset URL
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create email content
            subject = "Password Reset Request - Secure Authentication"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset Request</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .security-notice {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                        <p>Secure Authentication System</p>
                    </div>
                    <div class="content">
                        <h2>Hello {to_name or 'User'},</h2>
                        <p>We received a request to reset your password for your account. If you made this request, please click the button below to set a new password:</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset My Password</a>
                        </div>
                        
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace;">{reset_url}</p>
                        
                        <div class="security-notice">
                            <strong>⚠️ Security Notice:</strong>
                            <ul>
                                <li>This link will expire in 24 hours for security reasons</li>
                                <li>If you didn't request this password reset, please ignore this email</li>
                                <li>Never share this link with anyone</li>
                            </ul>
                        </div>
                        
                        <p>If you're having trouble with the button above, you can also reset your password by visiting our login page and clicking "Forgot Password" again.</p>
                    </div>
                    <div class="footer">
                        <p>This email was sent by the Secure Authentication System</p>
                        <p>If you have any questions, please contact our support team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Password Reset Request

Hello {to_name or 'User'},

We received a request to reset your password for your account. 

Please visit the following link to set a new password:
{reset_url}

Security Notice:
- This link will expire in 24 hours for security reasons
- If you didn't request this password reset, please ignore this email
- Never share this link with anyone

If you're having trouble, you can visit our login page and click "Forgot Password" again.

Best regards,
The Secure Authentication Team
            """.strip()
            
            # Create SendinBlue email object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name or to_email}],
                sender={"name": "Secure Authentication", "email": "noreply@yourdomain.com"},
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                tags=["password-reset", "authentication"]
            )
            
            # Send the email
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Password reset email sent successfully to {to_email}. Message ID: {api_response.message_id}")
            
            return True
            
        except ApiException as e:
            logger.error(f"SendinBlue API error when sending email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending email to {to_email}: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, to_name: str) -> bool:
        """
        Send welcome email to new users.
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            subject = "Welcome to Secure Authentication! 🎉"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome!</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; padding: 15px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to Secure Authentication!</h1>
                        <p>Your account has been created successfully</p>
                    </div>
                    <div class="content">
                        <h2>Hello {to_name or 'User'},</h2>
                        <p>Welcome to our secure authentication system! Your account has been created successfully and you're all set to get started.</p>
                        
                        <h3>What's Next?</h3>
                        <ul>
                            <li>🔐 Your account is secured with industry-standard encryption</li>
                            <li>🚀 You can sign in using your email and password</li>
                            <li>📱 Google Sign-In is also available for quick access</li>
                            <li>🔑 Use "Forgot Password" anytime to reset your password securely</li>
                        </ul>
                        
                        <div style="text-align: center;">
                            <a href="http://localhost:3007/login" class="button">Sign In Now</a>
                        </div>
                        
                        <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                    </div>
                    <div class="footer">
                        <p>Thank you for choosing our Secure Authentication System!</p>
                        <p>This email was sent because you created an account with us</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Welcome to Secure Authentication!

Hello {to_name or 'User'},

Welcome to our secure authentication system! Your account has been created successfully.

What's Next?
- Your account is secured with industry-standard encryption
- You can sign in using your email and password
- Google Sign-In is also available for quick access
- Use "Forgot Password" anytime to reset your password securely

Sign in at: http://localhost:3007/login

Thank you for choosing our Secure Authentication System!
            """.strip()
            
            # Create SendinBlue email object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name or to_email}],
                sender={"name": "Secure Authentication", "email": "noreply@yourdomain.com"},
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                tags=["welcome", "registration"]
            )
            
            # Send the email
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Welcome email sent successfully to {to_email}. Message ID: {api_response.message_id}")
            
            return True
            
        except ApiException as e:
            logger.error(f"SendinBlue API error when sending welcome email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending welcome email to {to_email}: {e}")
            return False


# Global instance
email_service = SendinBlueEmailService()
