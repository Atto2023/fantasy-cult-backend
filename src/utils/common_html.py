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

money_bonus_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Money Bonus</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="padding:20px;background:#000;max-width:300px;margin:0 auto;">
            <img src="https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/fantasy+logo+(1).png" alt="Your Logo" style="max-width: 100%; height: auto;">
        </div>
        <h1>Money Bonus</h1>
        <p>You have received a bonus of &#8377; <span id="bonusAmount">{bonus_amount}</span></p>
        <p style="font-size: 16px;">Download our app now!</p>
        <div>
            <a href="{android_link}" style="margin-right: 10px;">Download for Android</a>
            <a href="{ios_link}" style="margin-right: 10px;">Download for Apple</a>
        </div>
        <div style="margin-top: 20px;">
            <p>If you have any questions, feel free to contact us:</p>
            <a href="https://fantasycult.com">Contact us</a>
        </div>
        <div style="text-align:center;margin:20px 0 0 0">
            <p style="font-size:12px;color:#333">This game may be habit-forming or financially risky. Play responsibly.</p>
          </div>
    </div>
</body>
</html>
"""

money_deposited_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Money Deposited</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="padding:20px;background:#000;max-width:300px;margin:0 auto;">
        <img src="https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/fantasy+logo+(1).png" alt="Your Logo" style="max-width: 100%; height: auto;">
        </div>
        <h1>Money Deposited</h1>
        <p>Money Deposited Successfully with amount: &#8377; {amount}</p>
        <p>Thank you for your transaction!</p>
        <p>Please download our mobile app:</p>
        <ul>
            <li><a href="{android_link}">Download on Google Play</a></li>
            <li><a href="{ios_link}">Download on the App Store</a></li>
        </ul>
        <p>If you have any questions, feel free to contact us:</p>
        <p><a href="https://fantasycult.com">Contact us</a></p>
        <div style="text-align:center;margin:20px 0 0 0">
            <p style="font-size:12px;color:#333">This game may be habit-forming or financially risky. Play responsibly.</p>
        </div>
    </div>
</body>
</html>
"""

money_withdraw_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Money Withdrawal</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="padding:20px;background:#000;max-width:300px;margin:0 auto;">
            <img src="https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/fantasy+logo+(1).png" alt="Your Logo" style="max-width: 100%; height: auto;">
        </div>
        <h2>Withdrawal Request</h2>
        <p>We have received request for withdrawal of &#8377; {amount}. </p>
        <p>&#8377; {tds_amount} deducted under TDS.</p>
        <p style="font-size: 16px;">Download our app now!</p>
        <div>
            <a href="{android_link}" style="margin-right: 10px;">Download for Android</a>
            <a href="{ios_link}" style="margin-right: 10px;">Download for Apple</a>
        </div>
        <div style="margin-top: 20px;">
            <p>If you have any questions, feel free to contact us:</p>
            <a href="https://fantasycult.com">Contact us</a>
        </div>
        <div style="text-align:center;margin:20px 0 0 0">
            <p style="font-size:12px;color:#333">This game may be habit-forming or financially risky. Play responsibly.</p>
        </div>
    </div>
</body>
</html>
"""

money_lost_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Money Lost</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="padding:20px;background:#000;max-width:300px;margin:0 auto;">
            <img src="https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/fantasy+logo+(1).png" alt="Your Logo" style="max-width: 100%; height: auto;">
        </div>
        <h1>Uh-Oh!</h1>
        <p style="font-size: 16px;">Contest complete but result not in your favour, avenge your loss. Play again and win more!</p>
        <p style="font-size: 16px;">Download our app now!</p>
        <div>
            <a href="{android_link}" style="margin-right: 10px;">Download for Android</a>
            <a href="{ios_link}" style="margin-right: 10px;">Download for Apple</a>
        </div>
        <div style="margin-top: 20px;">
            <p>If you have any questions, feel free to contact us:</p>
            <a href="https://fantasycult.com">Contact us</a>
        </div>
        <div style="text-align:center;margin:20px 0 0 0">
            <p style="font-size:12px;color:#333">This game may be habit-forming or financially risky. Play responsibly.</p>
        </div>
    </div>
</body>
</html>
"""

money_won_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Money Won</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="padding:20px;background:#000;max-width:300px;margin:0 auto;">
            <img src="https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/fantasy+logo+(1).png" alt="Your Logo" style="max-width: 100%; height: auto;">
        </div>
        <h1>Congratulations!</h1>
        <p>You won &#8377; {amount} in {draft_name}.</p>
        <p style="font-size: 16px;">Download our app now!</p>
        <div>
            <a href="{android_link}" style="margin-right: 10px;">Download for Android</a>
            <a href="{ios_link}" style="margin-right: 10px;">Download for Apple</a>
        </div>
        <div style="margin-top: 20px;">
            <p>If you have any questions, feel free to contact us:</p>
            <a href="https://fantasycult.com">Contact us</a>
        </div>
        <div style="text-align:center;margin:20px 0 0 0">
            <p style="font-size:12px;color:#333">This game may be habit-forming or
            financially risky. Play responsibly.</p>
          </div>
    </div>
</body>
</html>
"""

draft_starting_soon = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draft Starting Soon</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="padding:20px;background:#000;max-width:300px;margin:0 auto;">
            <img src="https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/fantasy+logo+(1).png" alt="Your Logo" style="max-width: 100%; height: auto;">
        </div>
        <h1>Draft Starting Soon</h1>
        <p>Draft about to start in 5 mins.</p>
        <p style="font-size: 16px;">Download our app now!</p>
        <div>
            <a href="{android_link}" style="margin-right: 10px;">Download for Android</a>
            <a href="{ios_link}" style="margin-right: 10px;">Download for Apple</a>
        </div>
        <div style="margin-top: 20px;">
            <p>If you have any questions, feel free to contact us:</p>
            <a href="https://fantasycult.com">Contact us</a>
        </div>
        <div style="text-align:center;margin:20px 0 0 0">
            <p style="font-size:12px;color:#333">This game may be habit-forming or financially risky. Play responsibly.</p>
        </div>
    </div>
</body>
</html>
"""

draft_cancelled_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draft Cancelled</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="padding:20px;background:#000;max-width:300px;margin:0 auto;">
            <img src="https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/fantasy+logo+(1).png" alt="Your Logo" style="max-width: 100%; height: auto;">
        </div>
        <h1>Draft Cancelled</h1>
        <p>Oops! Draft {draft_name} is cancelled and amount is refunded.</p>
        <p style="font-size: 16px;">Download our app now!</p>
        <div>
            <a href="{android_link}" style="margin-right: 10px;">Download for Android</a>
            <a href="{ios_link}" style="margin-right: 10px;">Download for Apple</a>
        </div>
        <div style="margin-top: 20px;">
            <p>If you have any questions, feel free to contact us:</p>
            <a href="https://fantasycult.com">Contact us</a>
        </div>
        <div style="text-align:center;margin:20px 0 0 0">
            <p style="font-size:12px;color:#333">This game may be habit-forming or financially risky. Play responsibly.</p>
        </div>
    </div>
</body>
</html>
"""
