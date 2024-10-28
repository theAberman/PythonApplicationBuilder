"""
Application Builder File Summary

analyze_application.py serves as a critical component of the Python Application Builder, with the primary purpose of automating project documentation tasks. This file enhances code readability and project documentation by generating README files and adding meaningful comments to Python code. It analyzes existing codebases to identify documentation inefficiencies and areas that require improvement, thereby streamlining the development process.

Key functionalities include:
1. **README Generation**: Automatically creates comprehensive README files that include project title, description, installation instructions, and usage examples.
2. **Comment Automation**: Generates insightful comments in the code to clarify the purpose, parameters, and return values of functions, improving overall code comprehension.
3. **Pre-emptive Analysis**: Evaluates the structure and content of Python files to pinpoint areas needing documentation, aiding developers in making informed improvements.
4. **Continuous Integration Support**: Integrates into CI/CD pipelines to uphold documentation standards by alerting teams to deficiencies in comments or README sections.
5. **Onboarding Aid**: Facilitates smoother onboarding for new contributors by assessing the code's documentation readiness, thereby reducing the learning curve.

Overall, analyze_application.py is essential for maintaining high-quality, well-documented Python projects, allowing developers to focus on writing code while ensuring clarity and collaboration.
"""

import os
import re
import difflib  # Import difflib for creating diffs
from file_io import read_file, write_file

README_FILE = "README.md"
SUMMARY_PREFIX = "Application Builder File Summary"

class FeatureAnalyzer:

    def __init__(self, chatgpt_client):
        """Initialize the FeatureAnalyzer with a ChatGPT client."""
        self.chatgpt_client = chatgpt_client

    def extract_features_from_files(self, directory):
        """Extract functions, classes, and comments from Python files in the given directory."""
        feature_list = []
        python_files = [f for f in os.listdir(directory) if f.endswith(".py")]

        feature_pattern = re.compile(r"(def\s+\w+\(.*?\))|(\bclass\s+\w+)|(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')|(#.*)", re.DOTALL)

        for file in python_files:
            file_path = os.path.join(directory, file)
            print(f"[DEBUG] Analyzing file: {file_path}")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = feature_pattern.findall(content)
                    features = [match[0] or match[1] or match[2] for match in matches if match]
                    feature_list.extend([(file, feature) for feature in features])
                    print(f"[DEBUG] Extracted {len(matches)} features from {file}")

            except Exception as e:
                print(f"❌ [DEBUG] Error reading {file_path}: {e}")

        return feature_list

    def analyze_application(self, path):
        """Analyze the application to extract and generate insights."""
        print(f"[DEBUG] Analyzing application at path: {path}")
        features = self.extract_features_from_files(path)
        application_overview = read_file(os.path.join(path, README_FILE))

        feature_insights = [
            {"file": file, "feature": feature, 
             "insight": self.get_feature_insight(file, feature, application_overview)}
            for file, feature in features
        ]

        file_summaries = self.generate_file_summaries(feature_insights, application_overview)
        overall_insight = self.generate_overall_insight(file_summaries, application_overview)

        return {"file_summaries": file_summaries, "overall_insight": overall_insight}

    def get_feature_insight(self, file, feature, application_overview):
        """Fetch insight for a specific feature using ChatGPT."""
        prompt = (
            f"In the context of the application, which is previously understood to be: '{application_overview}', "
            f"the file '{file}' contains the feature '{feature}'. "
            "Can you provide a detailed analysis of this feature, including its role "
            "how it fits into the overall application, and examples of its use? "
        )
        return self.chatgpt_client.fetch_chatgpt_response(prompt)

    def generate_file_summaries(self, feature_insights, application_overview):
        """Generate summaries for each file based on the insights gathered."""
        file_summaries = []
        for file in set(insight["file"] for insight in feature_insights):
            file_related_insights = [insight for insight in feature_insights if insight["file"] == file]
            features_text = ", ".join(insight["feature"] for insight in file_related_insights)
            insights_text = "\n".join(insight["insight"] for insight in file_related_insights)

            summary_prompt = (
                f"Based on the following features in the file '{file}': {features_text}, "
                f"and considering the insights: {insights_text}, "
                "please summarize the role and functionality of this file, focusing specifically on its purpose "
                "and the key components it contains."
            )
            summary = self.chatgpt_client.fetch_chatgpt_response(summary_prompt)

            file_summaries.append({"file": file, "summary": summary})

        return file_summaries

    def generate_overall_insight(self, file_summaries, application_overview):
        """Generate an overall insight for the application based on file summaries."""
        overall_prompt = (
            f"In the context of the application overview: '{application_overview}', "
            "summarize the following file insights:\n" + "\n".join(f"{file['file']}: {file['summary']}" for file in file_summaries) + "\n"
            "Can you provide a cohesive summary for the overall application? "
            "This will serve as the core of a README, as well as the understanding of application context in the future."
        )
        return self.chatgpt_client.fetch_chatgpt_response(overall_prompt)



def save_analysis_to_context(context, features):
   """Save the analysis results to the context."""
   context['features'] = features
   return context

