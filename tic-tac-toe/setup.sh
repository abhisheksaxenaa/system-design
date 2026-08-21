# Create virtual environment
echo "Creating virtual environment"
python -m venv  .venv

# source the virtual environment
echo "Activating virtual environment"
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies from requirements.txt"
.venv/bin/pip install -r requirements.txt

# Create .env file based on .env.example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file based on .env.example"
fi
