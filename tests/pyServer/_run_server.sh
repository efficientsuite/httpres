# if .venv does not exist, create it
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi
source .venv/Scripts/activate
pip3 install -r requirements.txt
python3 main.py