import os
from file_io import read_file

class ContextManager:
    def __init__(self):
        self.static_context = self.load_static_context()
        self.semi_static_context = {}
        self.dynamic_context = {}
        self.execution_state = {}

    def load_static_context(self):
        return {
            "description": "Handles complex task execution including planning and recursion.",
            "available_actions": [
                {
                    "name": "analyze_file",
                    "description": "Analyze the content of a file.",
                },
                {
                    "name": "modify_file",
                    "description": "Modify the contents of a file.",
                },
                {
                    "name": "identify_gaps",
                    "description": "Identify missing elements or gaps.",
                },
                {"name": "generate_plan",
                    "description": "Generate development plans."},
                {
                    "name": "evaluate_state",
                    "description": "Determine if the current objective has been met.",
                },
                {
                    "name": "get_user_input",
                    "description": "Request input or clarification from the user.",
                },
            ],
        }

    def load_application_context(self):
        application_files = {}

        directory = self.semi_static_context.get("path")
        python_files = [f for f in os.listdir(directory) if f.endswith(".py")]

        #for file in python_files:
        #    file_path = os.path.join(directory, file)
        #    application_files[file] = read_file(file_path)

        self.semi_static_context["application_files"] = python_files

    def set_application_context(self, app_structure):
        self.semi_static_context = app_structure
        self.load_application_context()

    def save_generated_content(self, key, content):
        if "generated_content" not in self.dynamic_context:
            self.dynamic_context["generated_content"] = {}  # Initialize if it doesn't exist
        self.dynamic_context["generated_content"][key] = content  # Use assignment to store key-value pair


    def set_objective(self, user_objective):
        self.dynamic_context = {"objective": user_objective}

    def update_execution_state(self, state_info):
        self.execution_state.update(state_info)

    def create_plan(self, objective, dependencies):
        return {"objective": objective, "dependencies": dependencies}

    def get_current_context(self):
        return {
            "static": self.static_context,
            "semi_static": self.semi_static_context,
            "dynamic": self.dynamic_context,
            "execution_state": self.execution_state,
        }

    def update_context(self, key, value):
        self.dynamic_context[key] = value

    def get_context_value(self, key):
        return self.dynamic_context.get(key)

    def clear_context(self):
        """Reset the dynamic context for a fresh start."""
        self.dynamic_context = {}

    def reset_execution_state(self):
        """Reset the execution state to prepare for new tasks."""
        self.execution_state = {}

    def display_context(self):
        """Print current context values for debugging purposes."""
        print(f"Static Context: {self.static_context}")
        print(f"Semi-static Context: {self.semi_static_context}")
        print(f"Dynamic Context: {self.dynamic_context}")
        print(f"Execution State: {self.execution_state}")
