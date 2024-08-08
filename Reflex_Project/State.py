# state.py
import reflex as rx
import asyncio
import openai
import os
from openai import AsyncOpenAI
from Reflex_Project.openai_who import API_KEY

class State(rx.State):
    # The current question being asked.
    question: str

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]]

    async def answer(self):
        try:
            # Our chatbot has some brains now!
            client = AsyncOpenAI(api_key=os.environ[API_KEY])
            session = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": self.question}
                ],
                stop=None,
                temperature=0.7,
                stream=True,
            )

            # Add to the answer as the chatbot responds.
            answer = ""
            self.chat_history.append((self.question, answer))

            # Clear the question input.
            self.question = ""
            # Yield here to clear the frontend input before continuing.
            yield

            async for item in session:
                if hasattr(item.choices[0].delta, "content"):
                    if item.choices[0].delta.content is None:
                        # presence of 'None' indicates the end of the response
                        break
                    answer += item.choices[0].delta.content
                    self.chat_history[-1] = (self.chat_history[-1][0], answer)
                    yield
        except KeyError:
            self.chat_history.append((self.question, ""))
            self.question = ""
            yield

            # Simulate streaming with temperature=0.7 and slow latency
            simulated_response = "I'm sorry, I don't have enough tokens to answer your question. but you can work with it if you have enough tokens in yout account. The API key is not inserted in the code. Please insert the API key in the code."
            answer = ""
            for char in simulated_response:
                await asyncio.sleep(0.01)  # Simulate delay
                answer += char
                self.chat_history[-1] = (self.chat_history[-1][0], answer)
                yield