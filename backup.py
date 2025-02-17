import os
import sys
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.google import Gemini
import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt
from rich.markdown import Markdown
import inspect

class JarvisAssistant:
    def __init__(self):
        # Initialize Rich console for better output
        self.console = Console()
        
        # Setup logging with reduced verbosity
        logging.basicConfig(
            level=logging.WARNING,  # Changed from INFO to WARNING to reduce API logs
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("jarvis")
        
        # Load configuration
        self._load_config()
        
        # Initialize Gemini model
        self._initialize_model()
        
        # Setup agent
        self._setup_agent()

    def _load_config(self) -> None:
        """Load and validate configuration from environment variables."""
        load_dotenv()
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            self.logger.error("GEMINI_API_KEY is missing. Please set it in the .env file.")
            sys.exit(1)
            
        self.nick_name = os.getenv("NickName", "Sir")
        self.assistant_name = os.getenv("AssistantName", "J.A.R.V.I.S.")
        
        # Additional configurable parameters
        self.model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))

    def _initialize_model(self) -> None:
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

    def _setup_agent(self) -> None:
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

    def _format_response(self, response_content: str) -> str:
        """Format and clean the response content."""
        try:
            # Clean the response content and ensure it's a string
            cleaned_content = str(response_content).strip()
            # Return the cleaned content directly without Markdown wrapping
            return cleaned_content
        except Exception as e:
            self.logger.error(f"Error formatting response: {str(e)}")
            return "Sorry, there was an error processing the response."

    def _display_startup_message(self) -> None:
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

    def run(self) -> None:
        """Main interaction loop."""
        self._display_startup_message()
        
        while True:
            try:
                # Get user input with Rich prompt
                user_query = Prompt.ask(
                    f"\n[bold blue]{self.assistant_name}[/bold blue]",
                    default="",
                    show_default=False
                ).strip()

                # Handle exit commands
                if user_query.lower() in ["exit", "quit", "goodbye"]:
                    self.console.print(
                        f"\n{self.assistant_name}: Shutting down systems. Have a wonderful day, {self.nick_name}.",
                        style="bold blue"
                    )
                    break

                # Skip empty input
                if not user_query:
                    continue

                # Process query and get response
                with self.console.status("[bold blue]Processing...", spinner="dots"):
                    response = self.agent.run(user_query)

                # Display formatted response
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

if __name__ == "__main__":
    assistant = JarvisAssistant()
    assistant.run()