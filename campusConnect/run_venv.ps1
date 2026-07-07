# PowerShell wrapper to run a Python script inside the project's virtual environment
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ScriptPath,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ScriptArgs
)

$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-Not (Test-Path $venvActivate)) {
    Write-Error "Virtual environment not found. Run 'setup_env.ps1' first to create it."
    exit 1
}

# Activate the virtual environment
& $venvActivate

# Ensure the script exists
if (-Not (Test-Path $ScriptPath)) {
    Write-Error "Python script '$ScriptPath' not found."
    exit 1
}

# Run the script with any additional arguments
python "$ScriptPath" @ScriptArgs
