import json
import os
from chatgpt_interface import ChatGPTClient
from documentation_manager import DocumentationManager
from context_manager import ContextManager
from analyze_application import FeatureAnalyzer
from file_io import read_file, write_file, delete_file

class RecursiveExecutor:
    def __init__(self, chatgpt_client, feature_analyzer, documentation_manager):
        self.chatgpt_client = chatgpt_client
        self.context_manager = ContextManager()
        self.feature_analyzer = feature_analyzer
        self.documentation_manager = documentation_manager
        self.task_queue = []
        self.app_path = None  # Will store the application path during execution

    def execute(self, app_path):
        """
        Start the recursive execution with the provided application path.
        This method adds the analysis task and prompts the user to enter their objective.

        Args:
            app_path (str): The path to the application to be managed.
        """
        self.app_path = app_path
        self.context_manager.set_application_context({"path": app_path})

        # Add the initial analysis step to the task queue
        self.task_queue.append({
            "action": "analyze_project",
            "args": {
                "description": "Analyze the entire project directory to understand its structure and identify key components."
            }
        })

        # Prompt the user to enter their objective
        user_objective = input("[INPUT] Please enter your objective:\n> ").strip()

        # Set the objective in the context
        self.context_manager.set_objective(user_objective)

        # Add the objective as a task to the queue
        self.task_queue.append({
            "action": "generate_plan",
            "args": {
                "objective": user_objective
            }
        })

        # Start the recursive process with the initial analysis task
        self.recursive_call()

    def recursive_call(self):
        """
        Handles recursive execution by processing tasks from the task queue and responses from ChatGPT.
        Continues the recursion based on the queue and dynamically generated follow-ups.
        """
        # Process the next task from the queue if available
        if self.task_queue:
            next_instructions = self.task_queue.pop(0)
            action = next_instructions['action']
            args = next_instructions.get('args', {})

            print(f"[DEBUG] RecursiveCall next action: {action}")
            # Initialize result to None
            result = None

            # Normalize the arguments before executing the action
            normalized_args = self.normalize_args(action, args)
            result = self.process_instructions(next_instructions)

            # Update context with the result if applicable
            if result and 'result_key' in next_instructions:
                self.context_manager.update_context(next_instructions['result_key'], result)

            # Continue recursion with the next task
            self.recursive_call()
        else:
            print("[DEBUG] No more tasks in queue. Execution complete.")

    def process_instructions(self, instructions):
        """
        Execute the specified actions based on instructions and manage follow-up tasks.

        Args:
            instructions (dict): Contains 'action' and 'args' needed for execution.

        Returns:
            Any: The result of the executed action, if applicable.
        """
        action = instructions.get('action')
        args = instructions.get('args', {})
        if args == {}:
            args = instructions.get('arguments', {})

        # Map actions to executor methods
        action_map = {
            'analyze_file': self.analyze_file,
            'analyze_project': self.analyze_project,
            'get_raw_code': self.get_raw_code,
            'modify_file': self.modify_file,
            'identify_gaps': self.identify_gaps,
            'generate_plan': self.generate_plan,
            'generate_new_content': self.generate_new_content,
            'get_user_input': self.get_user_input,
            'evaluate_state': self.evaluate_state
        }

        if action in action_map:
            print(f"[DEBUG] Executing action: {action}")

            # Normalize the arguments before executing the action
            normalized_args = self.normalize_args(action, args)
            self.context_manager.update_context('last_action', action)

            if action == 'evaluate_state':
                # Evaluate state using ChatGPT to determine if objective is complete
                state = self.evaluate_state()
                print(f"[DEBUG] State evaluation result: {state}")
                self.context_manager.update_execution_state({'evaluation_result': state})

                if state == "complete":
                    print("[DEBUG] Objective achieved. No further actions needed.")
                    return "Objective complete"
                else:
                    print("[DEBUG] Replanning required. Adding 'generate_plan' to the queue.")
                    # Add 'generate_plan' directly to the task queue for replanning
                    self.task_queue.append({
                        'action': 'generate_plan',
                        'args': {
                            'objective': (f"Replanning required to achieve objective: {self.context_manager.get_context_value("objective")}.\n"
                                          f"Current state: {state}.\n\n"
                                          "  Thorougly inspect context to review previous actions taken and analysis done to allow further progress."),
                            'description': "Generate the next steps required to achieve the objective."
                        }
                    })
                    return None  # No more actions beyond replanning at this stage

            # Execute the action and store the result
            result = action_map[action](**normalized_args)

            # Update context using action and args as key
            context_key = action + str(args)  # Create a unique key for the context
            self.context_manager.update_context(context_key, result)

            # Add follow-up actions to the task queue, if specified
            follow_up = instructions.get('follow_up')
            if follow_up:
                print("[DEBUG] Adding follow-up task to queue.")
                self.task_queue.append(follow_up)

            return result

        else:
            print(f"[ERROR] Unknown action: {action}. No action executed.")
            return None

    def analyze_project(self):
        """Analyze the entire project directory."""
        print("[DEBUG] Analyzing project directory.")

        if not self.app_path:
            raise FileNotFoundError("[ERROR] Project path not set.")

        try:
            project_files = [f for f in os.listdir(self.app_path) if f.endswith(".py")]
            print(f"[DEBUG] Found project files: {project_files}")

            # Store the result in the execution state for subsequent actions
            self.context_manager.update_execution_state({"analyzed_files": project_files})

            return {"files": project_files}
        except Exception as e:
            print(f"❌ [DEBUG] Error analyzing project: {e}")
            return {"error": str(e)}

    def analyze_file(self, file_name, focus="all"):
        """
        Analyze a file or directory based on the provided file name.
        Args:
            file_name (str): The path to the file or directory.
            focus (str): Not directly used, maintained for compatibility with prompt tasks.
        """
        file_path = os.path.join(self.app_path, file_name)
        print(f"[DEBUG] Analyzing: {file_path}")

        if os.path.isdir(file_path):
            # If it's a directory, analyze as an application
            print(f"[DEBUG] Analyzing directory: {file_path}")
            result = self.feature_analyzer.analyze_application(file_path)
        elif os.path.isfile(file_path):
            # If it's an individual file, read the content
            print(f"[DEBUG] Reading file: {file_path}")
            content = read_file(file_path)
            result = {
                "file_name": file_name,
                "content": content,
                "insights": "Manual review may be required for non-Python files."
            }
        else:
            raise FileNotFoundError(f"File or directory not found: {file_path}")

        # Save result to context for future use
        self.context_manager.update_context("analysis_result", result)

        return {
            "result": result
        }

    def modify_file(self, file_name, content, action_type="modify"):
        """
        Create, modify, or delete a file based on the specified action type.
        This method interacts with the file system to apply the changes.

        Args:
            file_name (str): The name of the file to modify.
            content (str): The new content to write into the file or considerations for modification.
            action_type (str): The type of modification action, either 'modify', 'create', or 'delete'.
        """
        file_path = os.path.join(self.app_path, file_name)

        if action_type == "delete":
            if os.path.exists(file_path):
                delete_file(file_path)
                return {"status": "File deleted"}
            else:
                return {"status": "File not deleted"}

        elif action_type in ("modify", "create"):
            # Ensure content is in the correct format
            if isinstance(content, str):
                content_lines = content.splitlines()  # Split the content into lines for writing
            else:
                print(f"[ERROR] Invalid content format provided for {action_type}: {content}")
                return {"status": "Invalid content format"}

            if action_type == "modify":
                status = write_file(file_path, content_lines)
                return {"status": {status}}

            elif action_type == "create":
                status = write_file(file_path, content_lines)  # Assumes empty original content for creation
                return {"status": {status}}

    def identify_gaps(self, file_name=None, areas_of_interest=None):
        """Identify gaps or improvements in a specific file using ChatGPT."""
        if not file_name:
            print("[ERROR] No file specified for identify_gaps.")
            return None  # Skip this action if no file is specified

        print(f"[DEBUG] Identifying gaps in {file_name}.")

        areas_of_interest = areas_of_interest or ["functionality", "performance", "documentation"]

        # Read the content of the file for analysis
        try:
            file_content = read_file(os.path.join(self.app_path, file_name))
        except FileNotFoundError:
            raise FileNotFoundError(f"[ERROR] File not found: {file_content}")

        prompt = (
            f"File: {file_name}\n\n"
            f"{file_content}\n\n"
            f"Identify gaps or potential improvements related to the following areas: "
            f"{', '.join(areas_of_interest)}."
        )

        # Fetch the response from ChatGPT
        response = self.chatgpt_client.fetch_chatgpt_response(prompt, self.context_manager.get_current_context())

        if response:
            print(f"[DEBUG] Gaps found in {file_name}: {response}")
            # Store the result in the context manager
            self.context_manager.update_context(f"gaps_{file_name}", response)
        else:
            print(f"[ERROR] No response received for {file_name}.")

        return {"status": "Gaps identified", "file": file_name, "response": response}

    def generate_plan(self, objective, dependencies=[]):
        """Generate a plan to achieve the objective using ChatGPT."""
        print(f"[DEBUG] Generating plan for objective: {objective} with dependencies: {dependencies}")

        # Build the prompt as a single string
        prompt = self.generate_plan_prompt(objective, dependencies=[])

        # Fetch the response from ChatGPT
        response = self.chatgpt_client.fetch_chatgpt_response(prompt, self.context_manager.get_current_context())

        if response:
            try:
                cleaned_response = self.extract_json_block(response)
                tasks = self.extract_tasks(cleaned_response)
                if tasks:
                    print("[DEBUG] Adding generated tasks to the queue.")
                    self.task_queue.extend(tasks)
                else:
                    print("[ERROR] No valid tasks found in the response.")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[ERROR] Failed to decode response: {e}")
        else:
            print("[ERROR] Failed to fetch response from ChatGPT.")

    def generate_plan_prompt(self, objective, dependencies=[]):
        prompt = (
            f"The objective is:\n\n{objective}\n\n"
            f"Consider these dependencies: {dependencies}. "
            "Generate a step-by-step plan in JSON format, including only actions for which there is enough information. "
            "Use 'analyze_project' or 'analyze_file' actions to gather any missing information, and after sufficient analysis generate items which you know to be missing or deficient.\n\n"
            "Plans must end with an 'evaluate_state' action to confirm whether the objective has been achieved.  Avoid plans that consist solely of evaluating the state.\n\n"
            "If files or information are missing, or not yet generated, **do not reference filenames or content that haven't been discovered yet**."
            " Also avoid referencing information you expect to gather in the current plan."
            "Instead, for missing content, add another generate-plan action with an objective of completing those actions after you have completed what you know you can do with the current plan.\n\n"
            "If analysis is incomplete, the plan should schedule an 'evaluate_state' action to plan for more steps after further analysis.\n\n"
            "The goal is to ensure incremental planning and prevent assumptions or unnecessary steps in advance.\n\n"
            "Available actions, their descriptions, and required arguments:\n\n"
            "- **analyze_project**: Analyze the entire project directory to understand the structure and identify key components.\n"
            "  Required arguments: { 'description': str }\n\n"
            "- **analyze_file**: Analyze a specific file to understand its contents and identify relevant parts for enhancement.\n"
            "  Required arguments: { 'file_name': str, 'description': str }\n\n"
            "- **get_raw_code**: Retrieve and analyze the raw code of a file to gain insights into its implementation.\n"
            "  Required arguments: { 'file_name': str, 'description': str }\n\n"
            "- **modify_file**: Modify the contents of a file to implement specific feature enhancements. Do not add this action in the same plan the content is being generated.\n"
            "  Required arguments: { 'file_name': str, 'content': str (Content to be directly written to disk)}\n\n"
            "- **generate_new_content**: Generate new code or content based on existing content and a description of requested changes.\n"
            "  Required arguments: { 'existing_content': str(filename to base changes on or string to directly modify), 'change_description': str (detailed description of changes needed) }\n\n"
            "- **identify_gaps**: Identify missing elements or areas for improvement within the provided file or project.\n"
            "  Required arguments: { 'file_name': str, 'areas_of_interest': list[str], 'description': str }\n\n"
            "- **generate_plan**: Generate a high-level development plan to achieve the stated objective.\n"
            "  Required arguments: { 'objective': str }\n\n"
            "- **evaluate_state**: Determine if the current objective has been met or if additional planning is needed.\n"
            "  Required arguments: {}\n\n"
            "- **get_user_input**: Request product-level input or strategic guidance from the user to address high-level decisions.\n"
            "  Required arguments: { 'prompt': str }\n\n"
            "  Send this back as a dictionary called 'steps' containing the actions."
            "  Encode each action as an object with two keys, 'action' and 'args'\n\n"
        )
        return prompt

    def evaluate_state(self):
        """
        Evaluate if the current objective has been achieved by consulting ChatGPT based on completed tasks.
        """
        print("[DEBUG] Evaluating state based on current context.")

        objective = self.context_manager.get_context_value("objective")

        prompt = (
            f"The objective is:\n\n{objective}\n\n"

            "Based on the objective and the bundled context, has the objective been fully achieved? "
            "Please respond with 'yes' if the objective is met, or 'no' along with reasons and any additional actions or planning needed."
        )

        # Query ChatGPT to assess if the objective is complete
        response = self.chatgpt_client.fetch_chatgpt_response(prompt, self.context_manager.get_current_context())

        if response:
            print(f"[DEBUG] ChatGPT response: {response}")

            # Check for explicit 'yes' or 'no' responses
            if "yes" in response.lower():
                print("[DEBUG] Objective achieved.")
                return "complete"
            elif "no" in response.lower():
                print("[DEBUG] Further actions or planning required.")
                return response
            else:
                print("[DEBUG] Unclear response received. Further evaluation needed.")
                return response
        else:
            print("[ERROR] Failed to fetch response from ChatGPT.")
            return "error"


    def get_user_input(self, prompt):
        """
        Handle user input by prompting the user for clarification or preferences.
        Args:
            prompt (str): The question or message to display to the user.
        """
        print(f"[DEBUG] Requesting user input: {prompt}")
        context = self.context_manager.get_current_context()
        # Provide context information to the user
        print(f"[INFO] Current context: {context}")
        user_response = input(f"[USER INPUT] {prompt}\n> ")
        return user_response

    def extract_json_block(self, response):
        """
        Extracts the JSON block from the ChatGPT response.
        This function assumes the JSON block is enclosed within code block delimiters or at least
        properly formatted JSON at the start.
        """
        # Find the start and end of the JSON block
        start = min(response.find("{"), response.find("["))  # Get the earliest valid JSON start
        end = max(response.rfind("}"), response.rfind("]")) + 1  # Get the last valid JSON end

        if start == -1 or end == 0:
            raise ValueError("[ERROR] No valid JSON block found in the response.")

        json_block = response[start:end]
        print(f"[DEBUG] Extracted raw JSON block: {json_block}")

        # Attempt to decode the JSON block
        try:
            return json.loads(json_block)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decoding failed: {e}")
            raise

    def wrap_prompt(self, user_content):
        """
        Wraps the content into the correct structure expected by the ChatGPT API.
        """
        return [
            {"role": "system", "content": "You are assisting in generating a development plan and managing recursive tasks."},
            {"role": "user", "content": user_content}
        ]

    def get_raw_code(self, file_name):
        """Retrieve and display the raw content of a specified file."""
        print(f"[DEBUG] Retrieving raw code for file: {file_name}")

        # Check if the file exists
        file_path = os.path.join(self.app_path, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_name}")

        return read_file(file_path)

    def extract_instructions(self, response):
        """
        Extract instructions from a ChatGPT response, typically JSON formatted,
        to determine the next steps or actions required.
        Args:
            response (str): The JSON-formatted string response from ChatGPT.
        """
        try:
            instructions = json.loads(response)
            print(f"[DEBUG] Instructions extracted successfully.")
            return instructions
        except json.JSONDecodeError:
            print("[ERROR] Failed to decode the response.")
            return {}

    def clean_response(self, response):
        """
        Clean the response by extracting the JSON portion if any extraneous text is present.
        Args:
            response (str): The response string from ChatGPT.
        Returns:
            str: The cleaned JSON string ready for parsing.
        """
        try:
            # Find the JSON block within the response if it exists
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                json_content = response[start:end]
                print(f"[DEBUG] Extracted JSON content: {json_content}")
                return json_content
            else:
                print("[ERROR] No valid JSON found in response.")
                return ""
        except Exception as e:
            print(f"[ERROR] Error while cleaning response: {e}")
            return ""

    def describe_available_actions(self):
        """
        Provide a description of available actions to guide ChatGPT.

        Returns:
            str: A formatted string listing available actions and their descriptions.
        """
        available_actions = self.context_manager.static_context["available_actions"]
        return "\n".join(
            f"- {action['name']}: {action['description']}"
            for action in available_actions
        )

    def generate_new_content(self, existing_content, change_description):
        """
        Generate new content based on existing content and a description of requested changes.

        Args:
            existing_content (str): The current content to be modified, can be a filename or a snippet.
            change_description (str): The description of the changes to be made.

        Returns:
            str: The newly generated content after applying the requested changes.
        """
        original_existing_content = existing_content
        if existing_content:
            if os.path.exists(existing_content):
                existing_content = read_file(existing_content)
            # If existing_content is a snippet (not a path), use it directly.

        elif not existing_content:
            print("[ERROR] Existing content is empty. Cannot generate new content.")
            return ""

        # Check if change_description is provided
        if not change_description:
            print("[ERROR] Change description is missing. Cannot generate new content.")
            return ""

        prompt = (
            f"Here is the existing content:\n\n{existing_content}\n\n"
            f"Based on the following description of changes:\n{change_description}\n\n"
            "Please generate the updated content with the requested modifications."
        )

        # Fetch the response from ChatGPT
        response = self.chatgpt_client.fetch_chatgpt_response(prompt, self.context_manager.get_current_context())

        if response:
            print(f"[DEBUG] Generated new content based on changes: {response}")
            self.context_manager.save_generated_content((f"{existing_content} {change_description}"))
            return response
        else:
            print("[ERROR] Failed to generate new content.")
            return ""

    def normalize_args(self, action, args):
        """
        Normalize the arguments from ChatGPT's response to match internal method signatures.
        Ensure required arguments are present with defaults where needed.

        Args:
            action (str): The action being executed.
            args (dict): The arguments provided by ChatGPT.

        Returns:
            dict: The normalized arguments, cleaned and completed.
        """
        normalization_map = {
            'analyze_file': {'file_path': 'file_name'},
            'analyze_project': {},  # New action
            'get_raw_code': {'file_name': 'file_name'},  # New action
            'modify_file': {'file_name': 'file_name', 'content': 'content'},
            'identify_gaps': {'file_name': 'file_name', 'areas_of_interest': 'areas_of_interest'},
            'generate_plan': {'objective': 'objective'},
            'generate_new_content': {'existing_content': 'existing_content', 'change_description': 'change_description'},  # Add this line
            'evaluate_state': {},
            'get_user_input': {'prompt': 'prompt'}
        }

        # Normalize the arguments and provide defaults where needed
        expected_keys = normalization_map.get(action, {})
        cleaned_args = {
            expected_keys.get(k, k): v for k, v in args.items()
            if k in expected_keys or k in expected_keys.values()
        }

        # Ensure required keys are present with default values if missing
        for expected_key in expected_keys.values():
            if expected_key not in cleaned_args:
                cleaned_args[expected_key] = f"[DEBUG] Missing {expected_key}, setting default."

        print(f"[DEBUG] Normalized arguments for {action}: {cleaned_args} from these args: {args}")
        return cleaned_args

    def extract_tasks(self, cleaned_response):
        """
        Extract tasks from the cleaned JSON response.
        Args:
            cleaned_response (str, dict, or list): The cleaned JSON content or already parsed structure.
        Returns:
            list: A list of tasks.
        """
        # If the response is a string, attempt to load it as JSON
        if isinstance(cleaned_response, str):
            try:
                cleaned_response = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to decode JSON: {e}")
                return []

        # If it's a dictionary, assume tasks are under the "steps" key
        if isinstance(cleaned_response, dict):
            tasks = cleaned_response.get("steps", [])
        elif isinstance(cleaned_response, list):
            tasks = cleaned_response
        else:
            print("[ERROR] JSON content is not a valid task list or object with steps.")
            return []

        # Ensure all tasks have valid "action" entries
        valid_tasks = [step for step in tasks if "action" in step]
        print(f"[DEBUG] Extracted {len(valid_tasks)} valid tasks.")
        return valid_tasks
