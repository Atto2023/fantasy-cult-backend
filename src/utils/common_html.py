verify_email_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Email Verification Confirmation</title>
    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            text-align: center;
        }
        h1 {
            color: #007bff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
        }
        p {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Your Email Has Been Verified</h1>
        <p>Thank you for verifying your email address. You can now access your account.</p>
        <p>If you have any questions or need further assistance, please contact our support team.</p>
    </div>
</body>
</html>
"""

send_email_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification</title>
</head>
<body>
    <div style="text-align: center;">
        <h1>Email Verification</h1>
        <p>To verify your email address, please click the "Verify Email" button below:</p>
        
        <!-- Replace 'verification_link' with the actual link to your verification script on the server -->
        <a href={link} style="text-decoration: none;">
            <button style="padding: 10px 20px; background-color: #007BFF; color: #fff; border: none; cursor: pointer;">
                Verify Email
            </button>
        </a>
        
        <p>If you didn't request this email, you can safely ignore it.</p>
    </div>
</body>
</html>
"""
