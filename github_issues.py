from github import Github, GithubException

# Get GitHub token from user input
GITHUB_TOKEN = input("Enter your GitHub token: ")

# Check if the token is empty or invalid
if not GITHUB_TOKEN.strip():
    print("Error: GitHub token cannot be empty. Please provide a valid token.")
    exit()

# Connect to GitHub using the provided token and verify it
try:
    g = Github(GITHUB_TOKEN)
    # Verify the token by fetching the authenticated user's login
    user = g.get_user()
    print(f"Connected as {user.login}")
except GithubException:
    print("Invalid GitHub token. Please ensure it’s correct and try again.")
    exit()
except Exception as e:
    print(f"Unexpected error during connection: {e}")
    exit()

def get_repo(repo_name):
    """Get a repository object by its name."""
    try:
        repo = g.get_repo(repo_name)
        return repo
    except GithubException as e:
        if e.status == 404:
            print(f"Repository '{repo_name}' does not exist")
        else:
            print(f"Error accessing repository: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def create_issue(repo, title):
    """Create a new issue in the repository."""
    try:
        issue = repo.create_issue(title=title)
        print(f"Issue created successfully: #{issue.number} - {issue.title}")
    except Exception as e:
        print(f"Error creating issue: {e}")

def close_issue(repo, issue_number):
    """Close an existing issue by its number."""
    try:
        issue = repo.get_issue(number=issue_number)
        if issue.state == "closed":
            print(f"Issue #{issue_number} is already closed")
        else:
            issue.edit(state="closed")
            print(f"Issue #{issue_number} closed successfully")
    except GithubException as e:
        if e.status == 404:
            print(f"Issue #{issue_number} does not exist")
        else:
            print(f"Error closing issue: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def list_issues(repo, state="open"):
    """List issues in the repository, filtered by state (open, closed, or all)."""
    try:
        issues = repo.get_issues(state=state)
        if not issues.totalCount:
            print(f"No issues found with state: {state}")
            return
        print(f"\nIssues (state: {state}):")
        for issue in issues:
            print(f"#{issue.number} - {issue.title} ({issue.state})")
    except Exception as e:
        print(f"Error listing issues: {e}")

# Attempt to get a valid repository name from the user (max 2 attempts)
attempts = 0
repo = None
while attempts < 2:
    repo_name = input("Enter the repository name: ")
    repo = get_repo(repo_name)
    if repo:
        break  # Exit the loop if repo is valid
    attempts += 1
    if attempts == 1:
        print("You have one more attempt to enter a valid repository name,e.g example/examplerepo.")
    elif attempts == 2:
        print("You entered an invalid repository name twice. Exiting the program.")
        exit()

# If a valid repository was found, proceed with the menu
if repo:
    print(f"Successfully accessed repository: {repo.full_name}")
    
    # Main menu loop to manage issues
    while True:
        print("\nWhat would you like to do?")
        print("1. Create a new issue")
        print("2. Close an existing issue")
        print("3. List issues")
        print("4. Exit")
        choice = input("Enter your choice (1, 2, 3, or 4): ")
        
        if choice == "1":
            issue_title = input("Enter the title for the new issue: ")
            create_issue(repo, issue_title)
        elif choice == "2":
            try:
                issue_number = int(input("Enter the issue number to close: "))
                if issue_number <= 0:
                    print("Issue number must be a positive integer")
                else:
                    close_issue(repo, issue_number)
            except ValueError:
                print("Please enter a valid number")
        elif choice == "3":
            state = input("Enter state to filter (open/closed/all, default is open): ") or "open"
            if state not in ["open", "closed", "all"]:
                print("Invalid state, using default: open")
                state = "open"
            list_issues(repo, state)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again...")