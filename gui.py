import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import requests
import time

from langchain_community.llms import Ollama
from executor import run_code

# Import updated logic from main
from main import (
    build_prompt,
    handle_command,
    auto_detect_language,
    extract_code,
    detect_language_from_code,
)

# ------------------------
# Start Ollama Automatically
# ------------------------
def start_ollama():
    try:
        requests.get("http://localhost:11434")
        print("✅ Ollama already running")
    except:
        print("🚀 Starting Ollama...")
        subprocess.Popen(["ollama", "serve"])
        time.sleep(3)


# ------------------------
# LLM Setup
# ------------------------
llm = Ollama(model="deepseek-coder")
active_languages = []

# 🔥 NEW: Memory
last_code = None
last_language = None


# ------------------------
# Handle User Input
# ------------------------
def process_input(event=None):
    global last_code, last_language

    user_input = entry.get().strip()
    entry.delete(0, tk.END)

    if not user_input:
        return

    output_box.insert(tk.END, f"\n> {user_input}\n")

    if user_input.lower() == "exit":
        root.quit()
        return

    if handle_command(user_input, active_languages):
        return

    auto_detect_language(user_input, active_languages)

    prompt = build_prompt(user_input, active_languages, last_code, last_language)

    def run_llm():
        global last_code, last_language

        response = llm.invoke(prompt)

        output_box.insert(tk.END, f"\n💡 {response}\n")

        # Extract code
        code = extract_code(response)

        if code:
            from main import clean_code
            code = clean_code(code)

        if code:
            last_code = code
            last_language = detect_language_from_code(response) or (
                active_languages[-1] if active_languages else None
            )

        # Execute code
        if code and active_languages:
            lang = last_language

            output_box.insert(tk.END, "\n⚙️ Running code...\n")

            output, error = run_code(lang, code)

            if output:
                output_box.insert(tk.END, f"✅ Output:\n{output}\n")

            if error:
                output_box.insert(tk.END, f"❌ Error:\n{error}\n")

                explain_prompt = f"""
Explain this {lang} error clearly:

Code:
{code}

Error:
{error}
"""
                explanation = llm.invoke(explain_prompt)

                output_box.insert(tk.END, f"\n🧠 {explanation}\n")

        output_box.see(tk.END)

    threading.Thread(target=run_llm).start()


# ------------------------
# GUI Setup
# ------------------------
root = tk.Tk()
root.title("ProgramAI: Local Coding Agent")

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=28)
output_box.pack(padx=10, pady=10)

entry = tk.Entry(root, width=75)
entry.pack(side=tk.LEFT, padx=10, pady=10)

# 🔥 Enter key support
entry.bind("<Return>", process_input)

send_button = tk.Button(root, text="Send", command=process_input)
send_button.pack(side=tk.RIGHT, padx=10)


# ------------------------
# Start Everything
# ------------------------
start_ollama()

output_box.insert(tk.END, "🚀 Welcome to ProgramAI!\n")
output_box.insert(tk.END, "Commands: use <lang>, remove <lang>, list, exit\n")

root.mainloop()
