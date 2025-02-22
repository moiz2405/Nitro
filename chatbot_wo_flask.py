import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt

class JarvisAssistant:
    def __init__(self):
        self.console = Console()
        self._setup_logging()
        self._load_config()
        self._initialize_model()

    def _setup_logging(self):
        """Configure logging with Rich output."""
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("jarvis")

    def _load_config(self):
        """Load configuration from environment variables."""
        load_dotenv()
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            self.logger.error("GEMINI_API_KEY is missing. Please set it in the .env file.")
            sys.exit(1)
        
        self.nick_name = os.getenv("NICK_NAME", "User")
        self.assistant_name = os.getenv("ASSISTANT_NAME", "J.A.R.V.I.S.")
        
        self.model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")

    def _initialize_model(self):
        """Initialize the Gemini AI model."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_id)
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini model: {str(e)}")
            sys.exit(1)

    def _display_startup_message(self):
        """Display a startup message."""
        startup_message = f"""
        {self.assistant_name} Online
        -------------------------
        Systems: Operational
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        -------------------------
        """
        self.console.print(startup_message, style="bold blue")

    def _generate_response(self, user_input: str) -> str:
        """Generate a response using the Gemini AI model."""
        prompt = f"""
        You are {self.assistant_name}, an intelligent AI assistant.
        Address the user as {self.nick_name} and maintain a professional yet warm demeanor.
        Provide concise, relevant responses first, followed by additional insights when appropriate.
        Use technical language when discussing complex topics, but explain clearly.
        Maintain a slight wit and dry humor characteristic of J.A.R.V.I.S.
        Show initiative by suggesting proactive solutions when relevant.
        Never explicitly mention being an AI; operate as a fully functional butler.
        Use markdown formatting for code blocks and technical information.
        
        User: {user_input}
        {self.assistant_name}:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip() if response and hasattr(response, 'text') else "I'm sorry, I couldn't process that request."
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "An error occurred while processing your request."

    def run(self):
        """Main chat loop."""
        self._display_startup_message()
        
        while True:
            try:
                user_input = Prompt.ask(f"[bold blue]{self.nick_name}[/bold blue]").strip()
                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.console.print(f"\n{self.assistant_name}: Goodbye, {self.nick_name}! Have a great day!", style="bold blue")
                    break
                
                with self.console.status("[bold blue]Processing...", spinner="dots"):
                    response = self._generate_response(user_input)
                
                self.console.print(f"\n{self.assistant_name}: {response}", style="bold white")
            
            except KeyboardInterrupt:
                self.console.print(f"\n{self.assistant_name}: System interrupt detected. Goodbye, {self.nick_name}.", style="bold blue")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}")
                self.console.print("[bold red]An unexpected error occurred. Please try again.[/bold red]")

if __name__ == "__main__":
    assistant = JarvisAssistant()
    assistant.run()