# 💬 Customer Support Assistant Chatbot with Input Guardrails 🤖

This project demonstrates a streaming chatbot built using Gemini-2.0 via an OpenAI-compatible API and showcases how to use **input guardrails** 🚧 to restrict specific user queries (such as anything about "AgenticAI").

---

## 🚀 Features

* ✅ **Asynchronous Streaming Response**
* 🔒 **Input Guardrail** using a custom classification agent
* 🧪 **Try/Except Error Handling** for invalid inputs
* 🔐 **.env Integration** to secure API keys
* 🖥️ **Terminal UI with token streaming**

---

## 📁 Project Structure

```
.
├── chat.py              # 🧠 Main chatbot runner script
├── .env.example         # 🔐 Template for storing secrets
├── requirements.txt     # 📦 List of Python dependencies
└── README.md            # 📘 You are here!
```

---

## 🔧 Installation & Setup

```bash
# 1. Clone the repo
$ git clone https://github.com/yourusername/chatbot-guardrail.git
$ cd chatbot-guardrail

# 2. Create a virtual environment
$ python -m venv .venv
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Add your API key
$ cp .env.example .env
$ nano .env  # or open in your editor
```

---

## 🔐 Environment Variables

Create a `.env` file with:

```dotenv
GEMINI_API_KEY=your_google_api_key_here
```

---

## 🧠 Input Guardrail Overview

We create a second **classification agent** that inspects every user input to determine if it refers to "AgenticAI". This agent uses the same model and flags when its custom logic trips a guardrail.

### 🧪 Guardrail Agent Prompt

```
🛑 You are an input filter.
🧠 Your job is to detect whether a user is asking about AgenticAI in any form.
📌 Return a boolean field (is_AgenticAI) and a short reasoning.
```

---

## 📝 Main Loop Logic

```python
while True:
    user_input = input("User (type 'exit' to quit): ")
    if user_input.lower() == "exit":
        break
    history.append({"role": "user", "content": user_input})
    try:
        result = Runner.run_streamed(agent, history)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
        history.append({"role": "assistant", "content": result.final_output})
    except InputGuardrailTripwireTriggered:
        print("🚫 Guardrail tripped: input not allowed.")
        history.pop()
```

---

## 📊 Output Schema for Guardrail Agent

```python
class AgenticAIOutput(BaseModel):
    is_AgenticAI: bool
    reasoning: str
```

---

## 🧩 How It Works

* ⚙️ **Agentic\_guardrail** is a decorated async function that checks input via a special agent.
* ❗ If the user message is flagged, a `InputGuardrailTripwireTriggered` exception is raised.
* 🧯 This is caught in a `try/except` block around `Runner.run_streamed()`.

---

## 🛠 Customize

| Goal                      | How                                         |
| ------------------------- | ------------------------------------------- |
| 🧠 Change model           | Update `model="gemini-2.0-pro"`             |
| 🚫 Block different topics | Update the logic in `guardrail_agent`       |
| 🧱 Add output guardrails  | Use `output_guardrails=[...]` on main agent |
| 🌐 Add web UI             | Use FastAPI, Gradio, or Streamlit frontend  |

---

## 📦 Requirements

```
openai
python-dotenv
pydantic
```

---

## 🧪 Sample Interaction

```bash
User (type 'exit' to quit): Hello
Assistant: Hi! How can I assist you today?

User: What is AgenticAI?
🚫 Guardrail tripped: input not allowed.
```

---

## ✅ Best Practices

* 🧬 Keep `guardrail_agent` lightweight
* 🧾 Use `BaseModel` for consistent output typing
* 🔄 Always `pop()` from history on trip to prevent confusion

---

## 🧠 Future Ideas

* 📝 Logging guardrail trigger reasons to file
* 📈 Analytics on frequency of tripped rules
* 🛡️ Output guardrail to detect dangerous answers

---

## 📜 License

MIT License

---

## 🙏 Acknowledgments

* 🔬 Google AI Studio for Gemini API
* 🛠️ OpenAI-compatible libraries
* 🌟 LangChain for agent inspiration
