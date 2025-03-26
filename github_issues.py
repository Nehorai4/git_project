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

def show_repo_stats(repo):
    """Display basic statistics about the repository."""
    try:
        # Count issues
        open_issues = repo.get_issues(state="open").totalCount
        closed_issues = repo.get_issues(state="closed").totalCount
        
        # Count pull requests
        open_pulls = repo.get_pulls(state="open").totalCount
        closed_pulls = repo.get_pulls(state="closed").totalCount
        
        # Count commits
        commits = repo.get_commits().totalCount
        
        # Get last contributor
        last_commit = repo.get_commits()[0]
        last_contributor = last_commit.author.login if last_commit.author else "Unknown"

        # Display statistics
        print("\nRepository Statistics:")
        print(f"Open Issues: {open_issues}")
        print(f"Closed Issues: {closed_issues}")
        print(f"Open Pull Requests: {open_pulls}")
        print(f"Closed Pull Requests: {closed_pulls}")
        print(f"Total Commits: {commits}")
        print(f"Last Contributor: {last_contributor}")
    except Exception as e:
        print(f"Error fetching repository stats: {e}")

def create_branch(repo, branch_name):
    """Create a new branch in the repository based on main."""
    try:
        # Get the main branch reference
        source_branch = repo.get_branch("main")
        # Create a new branch from the latest commit of main
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source_branch.commit.sha)
        print(f"Branch '{branch_name}' created successfully.")
    except GithubException as e:
        print(f"Error creating branch: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def delete_branch(repo, branch_name):
    """Delete an existing branch from the repository."""
    try:
        # Prevent deletion of the main branch
        if branch_name == "main":
            print("Cannot delete the main branch.")
            return
        # Get the branch reference
        ref = repo.get_git_ref(f"heads/{branch_name}")
        # Delete the branch
        ref.delete()
        print(f"Branch '{branch_name}' deleted successfully.")
    except GithubException as e:
        if e.status == 404:
            print(f"Branch '{branch_name}' does not exist.")
        else:
            print(f"Error deleting branch: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def list_branches(repo):
    """List all branches in the repository."""
    try:
        branches = repo.get_branches()
        if not branches:
            print("No branches found in the repository.")
            return
        print("\nBranches:")
        for branch in branches:
            print(f"- {branch.name}")
    except Exception as e:
        print(f"Error listing branches: {e}")

# Attempt to get a valid repository name from the user (max 2 attempts)
attempts = 0
repo = None
while attempts < 2:
    repo_name = input("Enter the repository name: ")
    repo = get_repo(repo_name)
    if repo:
        break
    attempts += 1
    if attempts == 1:
        print("You have one more attempt to enter a valid repository name, e.g., example/examplerepo.")
    elif attempts == 2:
        print("You entered an invalid repository name twice. Exiting the program.")
        exit()

# If a valid repository was found, proceed with the menu
if repo:
    print(f"Successfully accessed repository: {repo.full_name}")
    
    # Main menu loop to manage issues, stats, and branches
    while True:
        print("\nWhat would you like to do?")
        print("1. Create a new issue")
        print("2. Close an existing issue")
        print("3. List issues")
        print("4. Show repository statistics")
        print("5. Create a new branch")
        print("6. Delete a branch")
        print("7. List branches")
        print("8. Exit")
        choice = input("Enter your choice (1-8): ")
        
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
            show_repo_stats(repo)
        elif choice == "5":
            branch_name = input("Enter the name for the new branch: ")
            create_branch(repo, branch_name)
        elif choice == "6":
            branch_name = input("Enter the name of the branch to delete: ")
            delete_branch(repo, branch_name)
        elif choice == "7":
            list_branches(repo)
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again...")