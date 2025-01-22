import boto3
from datetime import datetime, timedelta

# Initialize the IAM client
iam_client = boto3.client('iam')

# Function to check last login for a user
def get_inactive_users(days=100):
    inactive_users = []
    try:
        # Fetch all IAM users
        users = iam_client.list_users()['Users']
        
        # Define the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for user in users:
            user_name = user['UserName']
            print(f"Checking last login for user: {user_name}...")
            
            # Get the user's last login time
            last_login = user.get('PasswordLastUsed')  # Attribute for last login
            
            if last_login:
                last_login_date = last_login.replace(tzinfo=None)
                if last_login_date < cutoff_date:
                    inactive_users.append((user_name, last_login_date))
            else:
                # User has never logged in
                inactive_users.append((user_name, "Never Logged In"))
    except Exception as e:
        print(f"Error: {e}")
    
    return inactive_users

# Check for inactive users in the last 100 days
days_inactive = 150
inactive_users = get_inactive_users(days_inactive)

# Output the results
if inactive_users:
    print(f"\nUsers who haven't logged in for the last {days_inactive} days:")
    for user, last_login in inactive_users:
        print(f"User: {user}, Last Login: {last_login}")
else:
    print(f"\nNo users found who haven't logged in for the last {days_inactive} days.")
