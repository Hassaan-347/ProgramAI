# ProgramAI - Local Coding Assistant

## Linux Setup

```bash
python3 -m venv llm-agent-env
source llm-agent-env/bin/activate
pip install -r requirements.txt
```

Install Ollama from https://ollama.com

Then:
```
ollama run deepseek-coder
./run.sh
```

### DO NOT UPLOAD:
- llm-agent-env
- __pycache__
### MUST UPLOAD:
- requirements.txt
- run.sh
- source code

## Windows Setup
```
git clone https://github.com/your-username/ProgramAI.git
cd ProgramAI
python -m venv llm-agent-env
llm-agent-env\Scripts\activate
pip install -r requirements.txt
```
Install Ollama from https://ollama.com
Then run once:
```
ollama run deepseek-coder
```
Run the app using using run.bat because run.sh is for Linux systems only!
