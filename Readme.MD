# Preamble

+ First, any metrics you put in place to measure software developers will be gamed. 
+ Second: Remember [-2000 lines of code story](https://www.folklore.org/Negative_2000_Lines_Of_Code.html)

# Gitspector 

GitSpector is a Python-based tool that generates detailed contribution reports for GitHub repositories. It analyzes commits and pull requests over a specified time period and exports the data to an Excel spreadsheet.

## Features

- Analyzes multiple repositories simultaneously
- Tracks commits across all branches
- Monitors pull request activity
- Generates detailed Excel reports with:
  - Commit statistics (additions, deletions, files touched)
  - Pull request metrics (wait times, branch information)
  - Author summaries and work patterns
  - Working days analysis

## Prerequisites

- Python 3.6+
- GitHub Personal Access Token
- Required Python packages:
  - click
  - requests
  - pandas
  - xlsxwriter

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install click requests pandas xlsxwriter
```

3. Set up your GitHub token as an environment variable:

```bash
export GITHUB_TOKEN='your-github-token'
```

## Usage

Run the script with the following command:

```bash
python gitspector.py --repos "owner/repo1,owner/repo2" --weeks 4
```

### Parameters

- `--repos`: Comma-separated list of repositories in the format "owner/repo"
- `--weeks`: Number of weeks to analyze (default: 4)

## Output

The script generates an Excel file named `gitspector_report.xlsx` with three sheets:

1. **Commits**: Detailed information about each commit
   - SHA
   - Author
   - Message
   - Additions/Deletions
   - Files touched
   - Branch information
   - Repository
   - URL

2. **Pull Requests**: Information about closed PRs
   - PR number
   - Title
   - Author
   - Branch information
   - Changes statistics
   - Timeline metrics

3. **Summary**: Per-author statistics
   - Total commits
   - Lines added/deleted
   - Files touched
   - Pull requests
   - Working days
   - Work percentage

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Notes

- The tool requires a GitHub Personal Access Token with appropriate repository access permissions
- Rate limiting may apply based on GitHub API restrictions
- Large repositories or long time periods may take longer to analyze
