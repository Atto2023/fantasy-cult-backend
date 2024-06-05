class UserConstant():
    ERROR_USER_EMAIL = "User with this email id already exist"
    ERROR_EMAIL_OTP_NOT_MATCH = "Email OTP does not match"
    ERROR_MOBILE_OTP_NOT_MATCH = "Mobile OTP does not match"
    ERROR_PASSWORD_VALIDATOR = "Password and confirm password does not match"
    ERROR_PASSWORD_MISMATCH ="Password Mismatch"
    ERROR_USER_REGISTRATION = "Unable to Register the user" 
    ERROR_USER_MOBILE = "User with this mobile already exist"
    ERROR_USER_ALREADY_EXIST = "User is already registered, please login"
    ERROR_TOKEN = "Unauthorized Access! Please Login first!"
    SUCCESS_EMAIL_PHONE_STORE = 'OTP Sent Successfully!'
    USER_NOT_FOUND = 'User Not Found!'
    SUCCESS_USER_LOGGED = 'User Logged in Successfully'
    SUCCESS_UPDATED_PASSWORD = 'Password updated successfully'
    SUCCESS_ADD_SERIES ='Successfully added'
    SUCCESS_ADD_SERIES_ROUND ='Successfully added'
    SUCCESS_ADD_SPORT_MATCHES ='Successfully added'
    ERROR_EMAIL_OTP_NOT_MATCH = "The email OTP you entered doesn't match. Try again"
    ERROR_MOBILE_OTP_ID_NOT_MATCH = "The mobile OTP doesn't match. Please try again."
    SUCCESS_PHONE_RESEND_OTP = "OTP successfully resent to your phone!"
    

    SUCCESS_OTP_SENDED = "Otp Sended to mobile and email"
    SUCCESS_USER_REGISTRATION = "Logged In Successfully!!"
    SUCCESS_FETCH ="Fetch User Profile Success on Home Page"
    OTP_REQUIERED = 'Please provide both Email OTP and Mobile OTP ID'
    
    USER_REGISTER_NOT_FOUND = 'User Not Found, please register'
    USER_FIREBASE_ID = 'Please provide firebase uid for the requested User or Proper Password for the requested User'
    USER_ADDED_FAILED = "Unable to add user"
    USER_Profile_ADDED_SUCCESS = 'UserProfile Added successfully'
    UPDATE_SUCCESS = 'UserProfile Updated Successfully'
    FETCH_ALL_SUCCESS = 'Fetched all the User Data'
    REQUEST_ERROR = 'Please pass correct params'
    PARAM_ERROR = "Please Provide Either mobile or Either email"
    NONE_PROVIDED = 'Please Provide Either Email or Phone Number to Login'
    EMPTY_PASSWORD = 'Please Provide Non-Empty Password'
    INCORRECT_PASSWORD = 'Login Credential Dont Match'
    USER_ERROR = 'Something Bad Happens while creating User Check the Error -> '
    VERIFY_EMAIL_AND_MOBILE_SEND = "Please send email or mobile as verify for"
    USER_NOT_FOUND = 'No User Found'
    SUCCESS_USER_DELETED = 'User Deleted Successfully'
    SUCCESS_VERIFY_ACCOUNT = "Verify Accounts!!"
    
    #PanVerification
    PAN_DATA_SUBMITED = 'We received your Pan Data we will verify in 24 Hours'
    PAN_DATA_GET = 'Pan Card Data of the user'
    PAN_CARD_EXIST = 'Pan Card Data already there try to update'
    PAN_DATA_NOT_EXIST = 'User Pan Data not available try Registering'
    PAN_EMPTY_DATA = 'Please provide at least 1 data'

    
    #BankVerification
    BANK_DATA_SUBMITED = 'We Recieved you bank data we will verify in 24 Hours'
    BANK_DATA_GET = 'Bank Data of the user'
    BANK_DATA_EXIST = 'Bank Data already there try to update'
    BANK_DATA_NOT_EXIST = 'User Bank Data not avaialble try Registering'
    BANK_EMPTY_DATA = 'Please provide at least 1 data'

    #Admin
    HOME_SCREEN_ADDED = "Home Screen Datad Added"
    HOME_SCREEN_ERROR = "Home Screen Data Not Added"
    HOME_SCREEN_LIST = "Home Screen Data List"
    HOME_SCREEN_DETAIL = "Home Screen Data Detail"
    NOT_ADMIN = "User is not admin"
    HOME_SCREE_GET_ERROR = "Home Screen Get Error"
    
    #predefined
    EMAIL_DOES_NOT_EXITS = 'Enter Email Does Not Exits In Respected Firebase ID Database'
    PHONE_DOES_NOT_EXITS = 'Enter Mobile Number Does Not Exits In Respected Firebase ID Database'
    USER_FIREBASE_ID = 'Please provide firebase uid for the requested User or Proper Password for the requested User'
    USER_ADDED_SUCCESS = 'User Added successfully'
    USER_UPDATED = 'User Updated Successfully'
    USER_LOGIN_SUCCESS = 'User Login Successfully'
    REQUEST_ERROR = 'Please pass correct params'
    PARAM_ERROR = "Please Provide Either Number or Either Email"
    FIRESBASE_EXIST = 'Firebase UID is already exists'
    NONE_PROVIDED = 'Please Provide Either Email or Phone Number to Login'
    EMPTY_PASSWORD = 'Please Provide Non-Empty Password'
    INCORRECT_PASSWORD = 'Login Credential Dont Match'
    USER_ERROR = 'Something Bad Happens while creating User Please Recreate User!'
    DATA_ERROR = 'Please Provide Proper Body'
    FETCH_ALL_SUCCESS = 'Fetched all the User Data'
    FETCH_SUCCESS = 'Fetched User Data of given Token'
    ID_ERROR = 'Please Provide Numeric ID'
    FIREBASE_ID_DOES_NOT_EXITS = 'This Firebase ID Does Not Exits in Database'
    USER_DELETED = 'User Deleted'
    
     #Token
    NEW_TOKEN_GENERATED = "New Token Generated"
    INVALID_TOKEN = "Token invalid"
    
    #City
    ALL_CITY_DATA = 'All City Data'
    SUCCESS_CITY_ADD = 'city add Successfully'
    NO_DATA_FOUND = 'No Data Found'
    
    #state
    ALL_STATE_DATA = 'All state Data'
    SUCCESS_STATE_ADD = 'state add Successfully'
    
    #Transactions
    SUCCESS_BALANCE_ADD= 'Balance Added Successfully!'
    FETCH_ALL_AMOUNT = 'Fetch User Amount Successfully'
    ERROR_NO_TRANSACTION_FOUND = 'No Transaction Found For this User'
    FETCH_ALL_TRANSACTION = 'Fetch User Transactions Successfully'
    
    
    #status
    SUCCESS_STATUS_ADD = 'status add Successfully'
    ALL_STATUS_DATA = 'All status Data'
    SUCCESS_BALANCE_TYPE_ADD = 'balance type add Successfully'
    
    
    #UserBalance
    PLEASE_ENTER_VALUE_AMOUNT = "Please Enter Value for Amount for is Deposit Money"
    USER_BALANCE_NOT_FOUND = "User Balance Not Found"
    
    
    
    
class SportsConstant():
    DRAFT_CREATE_SUCCESS = "Draft has been created Successfully"
    DRAFT_GET_BY_ID_SUCESS = "Draft for the given contest id"
    DRAFT_GET_SUCCESS = "List of Drafts by the users"
    SERIES_ID_NOT_FOUND = "The Respective Series ID Not Found"
    ROUND_ID_NOT_FOUND = "The Respective Round ID not Found"
    MATCH_ID_NOT_FOUND = "The Respective Match ID not Found"
    PLEASE_SEND = "Please Send Upcoming, Live, Completed in three out of one"
    UPCOMING_MATCH = "Upcoming Match!"
    LIVE_MATCH = "Live Match!!"
    COMPLETED_MATCH = "Completed Match!!"
    SERIES_ALL = "Get All Series"
    MATCH_DATA_NOT_FOUND = "Match Type Data Not Found"
    SUCCESS_TEAM_ADDED = "Team Added SuccessFully!"


class NotificationConstant:
    MONEY_DEPOSITED = "Money Deposited Successfully - INR {}"
    MONEY_WITHDRAW = "Withdrawal Successfully - INR {} in your Bank and INR {} TDS Deducted"
    MONEY_BONUS = "You have Received {} Bonus"
    CONTEST_STARTED = "Your contest has started"
    BONUS_OFFER = "New BONUS OFFER"
    MONEY_WON = "Congratulations! You won INR {} in {} draft"
    MONEY_LOSS = "Uh-Oh! Contest complete but result not in your favour, avenge your loss. Play again and win more"
    DRAFT_CANCELLED = "OOPs! Draft {} is cancelled and amount is refunded"
    DRAFT_STARTED = "Draft about to start in 5 mins"
