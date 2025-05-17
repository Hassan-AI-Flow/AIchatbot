import os
import asyncio
from dotenv import load_dotenv , find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig, 
    set_tracing_disabled,
    input_guardrail,
    output_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered, 
    RunContextWrapper,
    TResponseInputItem
)

load_dotenv(find_dotenv())
set_tracing_disabled(True)

# Gemini via OpenAI-compatible client
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Use OpenAI-compatible wrapper for Gemini
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash-exp",  # or gemini/gemini-2.0-flash
    openai_client=client,
)

class AgenticAIOutput(BaseModel):
    is_AgenticAI: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you about AgenticAI.",
    output_type=AgenticAIOutput,
    model=model,
)


@input_guardrail
async def Agentic_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        # tripwire_triggered=False #result.final_output.is_math_homework,
        tripwire_triggered=result.final_output.is_AgenticAI,
    )

agent = Agent(
    name="Customer support Assistant",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[Agentic_guardrail],
    model=model
)
async def main():
    history = []
    while True:
        user_input = input("User (type 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("Goodbye! 👋")
            break
        history.append({"role": "user", "content": user_input})
        try:
            result = Runner.run_streamed(agent, history)
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    print(event.data.delta, end="", flush=True)
            print(f"\nAssistant: {result.final_output}")
            history.append({"role": "assistant", "content": result.final_output})
        except InputGuardrailTripwireTriggered:
            print("🚫 Guardrail tripped: input not allowed.")
asyncio.run(main())