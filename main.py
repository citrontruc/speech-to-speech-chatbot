import asyncio
import base64
from dotenv import load_dotenv
import io
from openai import AsyncAzureOpenAI
import os
import simpleaudio as sa # You need C++ VC14 to play sound

load_dotenv(override=True)


async def main() -> None:
    """
    When prompted for user input, type a message and hit enter to send it to the model.
    Enter "q" to quit the conversation.
    """

    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-10-01-preview",
    )
    async with client.beta.realtime.connect(
        model="gpt-4o-mini-realtime-preview",  # deployment name of your model
    ) as connection:
        await connection.session.update(session={"modalities": ["text", "audio"], "instructions" : "You are a nerd. Answer with short answers."},)  
        while True:
            user_input = input("Enter a message: ")
            if user_input == "q":
                break

            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_input}],
                }
            )
            await connection.response.create()
            async for event in connection:
                if event.type == "response.text.delta":
                    print(event.delta, flush=True, end="")
                elif event.type == "response.audio.delta":
                    audio_data = base64.b64decode(event.delta)
                    #audio_buffer = io.BytesIO(audio_data)
                    play_obj = sa.play_buffer(audio_data, 1, 2, 22050)
                    play_obj.wait_done()
                    print(f"Received {len(audio_data)} bytes of audio data.")
                elif event.type == "response.audio_transcript.delta":
                    print(f"Received text delta: {event.delta}")
                elif event.type == "response.text.done":
                    print()
                elif event.type == "response.done":
                    break


if __name__ == "__main__":
    asyncio.run(main())
