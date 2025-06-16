# Install dependencies using uv
Write-Host "Installing dependencies..."
uv pip install -r requirements.txt

# Run the benchmarks
Write-Host "Running benchmarks..."
uv run run_benchmarks.py

# Open the results directory
Write-Host "Opening results directory..."
explorer.exe ".\plots" 