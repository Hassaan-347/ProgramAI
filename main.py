import json
import os
import re
from langchain_community.llms import Ollama
from executor import run_code

llm = Ollama(model="deepseek-coder")

LANGUAGE_FOLDER = "languages"


# ------------------------
# Language Loader
# ------------------------
def load_language(language_name):
    path = os.path.join(LANGUAGE_FOLDER, f"{language_name.lower()}.json")

    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return json.load(f)


# ------------------------
# Code Extraction
# ------------------------
def extract_code(text):
    blocks = re.findall(r"```(\w+)?\n(.*?)```", text, re.DOTALL)

    if not blocks:
        return None

    # Sort by size (largest block is most likely real code)
    blocks_sorted = sorted(blocks, key=lambda x: len(x[1]), reverse=True)

    code = blocks_sorted[0][1].strip()

    return code

def clean_code(code):
    lines = code.split("\n")

    cleaned = []
    for line in lines:
        # Remove long explanation-like comments
        if line.strip().startswith("#") and len(line) > 80:
            continue

        # Remove common explanation phrases
        if any(word in line.lower() for word in ["pep8", "guidelines", "this code", "in this case"]):
            continue

        cleaned.append(line)

    return "\n".join(cleaned).strip()

# ------------------------
# Detect Language from Code Block
# ------------------------
def detect_language_from_code(text):
    if "```python" in text:
        return "python"
    if "```cpp" in text or "```c++" in text:
        return "cpp"
    if "```java" in text:
        return "java"
    if "```javascript" in text:
        return "javascript"
    return None


# ------------------------
# Detect Conversion Intent
# ------------------------
def is_conversion_request(user_input):
    keywords = ["same", "convert", "translate", "rewrite"]
    return any(word in user_input.lower() for word in keywords)


# ------------------------
# Detect Target Language
# ------------------------
def detect_target_language(user_input):
    for lang in ["python", "java", "cpp", "javascript", "c", "go", "rust", "bash"]:
        if lang in user_input.lower():
            return lang
    return None


# ------------------------
# Prompt Builder
# ------------------------
def build_prompt(user_input, active_languages, last_code=None, last_language=None):
    context = "You are a strict programming assistant.\n"

    # ------------------------
    # Language Context
    # ------------------------
    if active_languages:
        for lang in active_languages:
            data = load_language(lang)
            if data:
                context += f"\n### {data['name']} Context ###\n"

                context += "Rules:\n"
                for rule in data["rules"]:
                    context += f"- {rule}\n"

                context += "Snippets:\n"
                for snip in data["snippets"]:
                    context += f"- {snip}\n"
    else:
        context += "No language selected. Ask user to choose one.\n"

    # ------------------------
    # 🔥 STRONG Conversion Handling
    # ------------------------
    if last_code and is_conversion_request(user_input):
        target_lang = detect_target_language(user_input)

        context += "\n### TASK: CODE TRANSLATION ###\n"
        context += "You MUST convert the given code into another programming language.\n"
        context += "DO NOT explain. DO NOT describe. ONLY output code.\n"
        context += "Preserve the same functionality.\n"

        context += f"\nOriginal Language: {last_language}\n"
        context += f"Target Language: {target_lang if target_lang else 'infer from user request'}\n"

        context += "\n### SOURCE CODE ###\n"
        context += f"{last_code}\n"

        context += "\n### OUTPUT REQUIREMENTS ###\n"
        context += "- Output ONLY code\n"
        context += "- Wrap code in triple backticks\n"
        context += "- No explanation\n"

        return context  # 🚨 IMPORTANT: EARLY RETURN

    # ------------------------
    # Normal Query
    # ------------------------
    context += "\n### OUTPUT RULES ###\n"
    context += "- Always respond with ONLY code\n"
    context += "- No explanations\n"
    context += "- No comments unless necessary\n"
    context += "- Wrap code in triple backticks\n"

    context += f"\nUser Request:\n{user_input}\n"

    return context


# ------------------------
# Command Handling
# ------------------------
def handle_command(user_input, active_languages):
    cmd = user_input.lower()

    if cmd.startswith("use "):
        lang = cmd.split("use ")[1].strip()

        if lang not in active_languages:
            if load_language(lang):
                active_languages.append(lang)
                print(f"✅ Added language: {lang}")
            else:
                print(f"❌ Language '{lang}' not found.")
        else:
            print(f"⚠️ {lang} already active.")

        return True

    elif cmd.startswith("remove "):
        lang = cmd.split("remove ")[1].strip()

        if lang in active_languages:
            active_languages.remove(lang)
            print(f"🗑️ Removed language: {lang}")
        else:
            print(f"⚠️ {lang} not active.")

        return True

    elif cmd == "list":
        if active_languages:
            print("📚 Active languages:", ", ".join(active_languages))
        else:
            print("📭 No active languages.")

        return True

    return False


# ------------------------
# Auto Language Detection
# ------------------------
def auto_detect_language(user_input, active_languages):
    text = user_input.lower()

    mapping = {
        "python": "python",
        "py": "python",
        "c++": "cpp",
        "cpp": "cpp",
        "javascript": "javascript",
        "js": "javascript",
        "java": "java",
        "c language": "c",
        "golang": "go",
        "go": "go",
        "rust": "rust",
        "bash": "bash",
        "shell": "bash"
    }

    for key, lang in mapping.items():
        if key in text and lang not in active_languages:
            if load_language(lang):
                active_languages.append(lang)
                print(f"🤖 Auto-added {lang}")


# ------------------------
# Main Loop
# ------------------------
def main():
    active_languages = []
    last_code = None
    last_language = None

    print("🚀 Local Coding Agent")
    print("Commands: use <lang>, remove <lang>, list, exit")

    while True:
        user_input = input("\n> ")

        if user_input.lower() == "exit":
            break

        if handle_command(user_input, active_languages):
            continue

        auto_detect_language(user_input, active_languages)

        prompt = build_prompt(user_input, active_languages, last_code, last_language)

        # LLM response
        response = llm.invoke(prompt)
        print("\n💡 Response:\n", response)

        # Extract code
        code = extract_code(response)

        if code:
            code = clean_code(code)

        if code:
            last_code = code
            last_language = detect_language_from_code(response) or (
                active_languages[-1] if active_languages else None
            )

        # Execute code
        if code and active_languages:
            lang = last_language

            print("\n⚙️ Running code...\n")

            output, error = run_code(lang, code)

            if output:
                print("✅ Output:\n", output)

            if error:
                print("❌ Error:\n", error)

                explain_prompt = f"""
Explain this {lang} error clearly:

Code:
{code}

Error:
{error}
"""
                explanation = llm.invoke(explain_prompt)

                print("\n🧠 Explanation:\n", explanation)


if __name__ == "__main__":
    main()
