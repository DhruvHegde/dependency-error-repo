# F4 Deployment Error Configuration

# GitHub Repository
REPO_OWNER = "solar-gazer"
REPO_NAME = "deployment-errors"

# Workflow Settings
WORKFLOW_NAME = "Deploy"
WORKFLOW_FILE = "deploy.yml"

# Failure Category
FAILURE_TYPE = "F4"
STAGE = "deploy"

# Dataset Target
TOTAL_RUNS = 150

# Output Folders
LOG_FOLDER = "logs/F4"
METADATA_FOLDER = "metadata/F4"

# GitHub Actions Polling
POLL_INTERVAL = 5
MAX_WAIT = 300