import os
import sys
import pyttsx3
import speech_recognition as sr
from datetime import datetime
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.google import Gemini
import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt

class JarvisAssistant:
    def __init__(self):
        self.console = Console()
        self._setup_logging()
        self._load_config()
        self._initialize_model()
        self._setup_agent()
        self._initialize_tts()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("jarvis")

    def _load_config(self):
        load_dotenv()
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            self.logger.error("GEMINI_API_KEY is missing. Please set it in the .env file.")
            sys.exit(1)

        self.nick_name = os.getenv("NickName", "Sir")
        self.assistant_name = os.getenv("AssistantName", "J.A.R.V.I.S.")
        self.model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))

    def _initialize_model(self):
        try:
            self.model = Gemini(
                id=self.model_id,
                name="Gemini",
                provider="Google",
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini model: {str(e)}")
            sys.exit(1)

    def _setup_agent(self):
        self.agent = Agent(
            model=self.model,
            description=f"{self.assistant_name} is your advanced AI assistant, modeled after J.A.R.V.I.S.",
            instructions=[
                f"You are {self.assistant_name}, an intelligent AI assistant.",
                f"Address the user as {self.nick_name} and maintain a professional yet warm demeanor.",
                "Provide concise, relevant responses first, followed by additional insights when appropriate.",
                "Use markdown formatting for code blocks and technical information.",
            ],
            expected_output="{Precise response}. {Additional insights if relevant.}",
            markdown=True,
            show_tool_calls=False,
            add_datetime_to_instructions=True,
            add_history_to_messages=True
        )

    def _initialize_tts(self):
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 1)  # Volume level

    def _speak(self, text):
        """Convert text to speech and play it."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def _listen(self):
        """Listen for voice input and return transcribed text."""
        with self.microphone as source:
            self.console.print("Listening...", style="bold yellow")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                return self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                self.console.print("[bold red]Speech recognition service unavailable.[/bold red]")
                return ""

    def _display_startup_message(self):
        startup_message = f"""
        {self.assistant_name} Online
        -------------------------
        Systems: Operational
        User: {self.nick_name}
        Model: {self.model_id}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        -------------------------
        """
        self.console.print(startup_message, style="bold blue")

    def chat(self):
        self._display_startup_message()

        while True:
            try:
                choice = Prompt.ask("Enter input mode", choices=["text", "voice"], default="text")
                
                if choice == "voice":
                    user_query = self._listen()
                    if not user_query:
                        self.console.print("[bold red]Couldn't understand. Try again.[/bold red]")
                        continue
                else:
                    user_query = Prompt.ask(f"\n[bold blue]{self.assistant_name}[/bold blue]").strip()

                if user_query.lower() in ["exit", "quit", "goodbye"]:
                    self.console.print(f"\n{self.assistant_name}: Goodbye, {self.nick_name}.", style="bold blue")
                    self._speak(f"Goodbye, {self.nick_name}.")
                    break

                with self.console.status("[bold blue]Processing...", spinner="dots"):
                    response = self.agent.run(user_query)

                if response and hasattr(response, 'content'):
                    formatted_response = response.content.strip()
                    self.console.print(f"\n{self.assistant_name}: {formatted_response}", style="bold white")
                    self._speak(formatted_response)
                else:
                    self.console.print(f"\n{self.assistant_name}: Sorry, I couldn't process that request.", style="bold red")

            except KeyboardInterrupt:
                self.console.print(f"\n{self.assistant_name}: System interrupt detected. Goodbye, {self.nick_name}.", style="bold blue")
                self._speak("System interrupt detected. Goodbye.")
                break
            except Exception as e:
                self.logger.error(f"Error during execution: {str(e)}")
                self.console.print("[bold red]An error occurred. Please try again.[/bold red]")
