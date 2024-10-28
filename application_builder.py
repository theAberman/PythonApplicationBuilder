"""
Application Builder File Summary

# application_builder.py

This file serves as the core of the Python Application Builder, designed to automate the documentation processes for Python projects. It primarily focuses on two key functionalities:

1. **README Generation**: This feature automatically compiles essential project information such as project name, version, author details, installation instructions, and usage examples into a structured README.md file. This ensures that all necessary information is readily available to users and contributors, enhancing project clarity and usability.

2. **Comment Generation**: This function enhances the readability and maintainability of Python code by adding meaningful comments to source files. It analyzes functions, classes, and complex code blocks, inferring their purposes and inserting comments that provide context, thus facilitating collaboration and easing the onboarding process for new developers.

Overall, the application_builder.py file plays a crucial role in increasing developer productivity and improving code quality by streamlining documentation tasks and ensuring that both documentation and code are clear and up-to-date.

"""

import os
import json
from chatgpt_interface import ChatGPTClient  # Import the ChatGPTClient
from analyze_application import FeatureAnalyzer, save_analysis_to_context  # Ensure these imports are included
from documentation_manager import DocumentationManager
from recursive_executor import RecursiveExecutor

class ApplicationBuilder:
    def __init__(self, app_path):
        self.app_path = app_path
        self.context_file = os.path.join(os.path.dirname(__file__), 'context.json')
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.openai_api_key = self.load_api_key()
        self.context = self.load_context()
        self.chatgpt_client = ChatGPTClient(api_key=self.openai_api_key)  # Initialize ChatGPT client
        self.feature_analyzer = FeatureAnalyzer(self.chatgpt_client)  # Initialize FeatureAnalyzer with the client
        self.documentation_manager = DocumentationManager(self.chatgpt_client)
        self.recursive_executor = RecursiveExecutor(self.chatgpt_client, self.feature_analyzer, self.documentation_manager)  # Initialize RecursiveExecutor
        self.analysis_result = None  # Store the analysis result

    def load_api_key(self):
        """Load the OpenAI API key from the config file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config.get('openai_api_key')
        except FileNotFoundError:
            print("❌ Config file not found.")
            return None
        except json.JSONDecodeError:
            print("❌ Error decoding JSON from config file.")
            return None

    def load_context(self):
        """Load the context from the context file."""
        if os.path.exists(self.context_file):
            with open(self.context_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def analyze_application(self):
        """Analyze the application and save features to the context."""
        print(f"[DEBUG] Analyzing application at path: {self.app_path}")
        analysis_result = self.feature_analyzer.analyze_application(self.app_path)
        self.context = save_analysis_to_context(self.context, analysis_result)  # Save features to context
        print(f"[DEBUG] Features analyzed and saved to context: {analysis_result}")


    def display_menu(self):
        """Display the menu options."""
        print("\n[DEBUG] Options:")
        print("1. Analyze files and show features")
        print("2. Update Comments")
        print("3. Generate README.md")
        print("4. Run Recursive Executor")  # New option
        print("5. Quit")


    def run(self):
        """Run the application builder."""
        print("[DEBUG] Starting the ChatGPT-Python Application Builder...")
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == '1':
                self.analyze_application()
            elif choice == '2':
                if self.analysis_result:
                    self.documentation_manager.maintain_comments(self.analysis_result, self.app_path)
                else:
                    print("[DEBUG] No analysis found. Please analyze the application first.")
            elif choice == '3':
                if self.analysis_result:
                    self.documentation_manager.update_readme(self.analysis_result, self.app_path)
                else:
                    print("[DEBUG] No analysis found. Please analyze the application first.")
            elif choice == '4':
                print("[DEBUG] Running Recursive Executor...")
                self.recursive_executor.execute(self.app_path)  # Execute the Recursive Executor
            elif choice == '5':
                print("[DEBUG] Exiting.")
                break
            else:
                print("[DEBUG] Invalid choice. Please select a valid option.")
                continue

    def run_recursive_executor(self):
        """Launch the RecursiveExecutor with the app path."""
        print("[DEBUG] Launching Recursive Executor...")
        self.recursive_executor.execute(self.app_path)

if __name__ == "__main__":
    app_path = input("Enter the path to your Python application: ")
    builder = ApplicationBuilder(app_path)
    builder.run()