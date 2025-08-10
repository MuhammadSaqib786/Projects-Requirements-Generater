import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

token = os.getenv("GITHUB_TOKEN")
if not token:
    raise SystemExit("GITHUB_TOKEN not set")

client = ChatCompletionsClient(
    endpoint=os.getenv("GITHUB_ENDPOINT", "https://models.github.ai/inference"),
    credential=AzureKeyCredential(token),
)

model = os.getenv("GITHUB_MODEL_ID", "deepseek/DeepSeek-V3-0324")

resp = client.complete(
    messages=[SystemMessage("You are a helpful assistant."),
              UserMessage("Say 'pong'")],
    model=model,
    max_tokens=50,
)

print(resp.choices[0].message.content)
