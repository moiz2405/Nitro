import os
import sys
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

    def _setup_logging(self):
        """Setup logging with reduced verbosity."""
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("jarvis")

    def _load_config(self):
        """Load and validate configuration from environment variables."""
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
        """Initialize the Gemini model with configuration."""
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
        """Configure the AI agent with personality and instructions."""
        self.agent = Agent(
            model=self.model,
            description=f"{self.assistant_name} is your advanced AI assistant, modeled after J.A.R.V.I.S.",
            instructions=[
                f"You are {self.assistant_name}, an intelligent AI assistant.",
                f"Address the user as {self.nick_name} and maintain a professional yet warm demeanor.",
                "Provide concise, relevant responses first, followed by additional insights when appropriate.",
                "Use technical language when discussing complex topics, but explain clearly.",
                "Maintain a slight wit and dry humor characteristic of J.A.R.V.I.S.",
                "Show initiative by suggesting proactive solutions when relevant.",
                "Never explicitly mention being an AI; operate as a fully functional butler.",
                "Use markdown formatting for code blocks and technical information.",
            ],
            expected_output="{Precise response}. {Additional insights or recommendations if relevant.}",
            markdown=True,
            show_tool_calls=False,
            add_datetime_to_instructions=True,
            add_history_to_messages=True
        )

    def _format_response(self, response_content):
        """Format and clean the response content."""
        try:
            return str(response_content).strip()
        except Exception as e:
            self.logger.error(f"Error formatting response: {str(e)}")
            return "Sorry, there was an error processing the response."

    def _display_startup_message(self):
        """Display an engaging startup message."""
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
        """Main interaction loop."""
        self._display_startup_message()

        while True:
            try:
                user_query = Prompt.ask(
                    f"\n[bold blue]{self.assistant_name}[/bold blue]",
                    default="",
                    show_default=False
                ).strip()

                if user_query.lower() in ["exit", "quit", "goodbye"]:
                    self.console.print(
                        f"\n{self.assistant_name}: Shutting down systems. Have a wonderful day, {self.nick_name}.",
                        style="bold blue"
                    )
                    break

                if not user_query:
                    continue

                with self.console.status("[bold blue]Processing...", spinner="dots"):
                    response = self.agent.run(user_query)

                if response and hasattr(response, 'content'):
                    formatted_response = self._format_response(response.content)
                    self.console.print(f"\n{self.assistant_name}: {formatted_response}", style="bold white")
                else:
                    self.console.print(f"\n{self.assistant_name}: I apologize, but I couldn't process that request properly.", style="bold red")

            except KeyboardInterrupt:
                self.console.print(
                    f"\n{self.assistant_name}: System interrupt detected. Goodbye, {self.nick_name}.",
                    style="bold blue"
                )
                break
            except Exception as e:
                self.logger.error(f"Error during execution: {str(e)}")
                self.console.print(
                    f"[bold red]An error occurred. Please try again or check the logs.[/bold red]"
                )
