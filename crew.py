import warnings
warnings.filterwarnings('ignore')

import os
import yaml
import argparse
import sys
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from IPython.display import display, Markdown
import logging

logging.basicConfig(level=logging.INFO)

# Define file paths for YAML configurations
files = {
    'agents': 'config/agents.yaml',
    'tasks': 'config/tasks.yaml'
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']

# FileReadTool for CSV
def create_csv_tool(file_path):
    print("Processing file:", file_path)
    return FileReadTool(file_path=file_path)

# Creating Agents - will be created dynamically with proper tools
def create_suggestion_generation_agent(file_path):
    csv_tool = create_csv_tool(file_path)
    return Agent(
        config=agents_config['suggestion_generation_agent'],
        tools=[csv_tool]
    )

def create_reporting_agent(file_path):
    csv_tool = create_csv_tool(file_path)
    return Agent(
        config=agents_config['reporting_agent'],
        tools=[csv_tool]
    )

def create_chart_generation_agent():
    return Agent(
        config=agents_config['chart_generation_agent'],
        allow_code_execution=False  # Disable code execution to avoid Docker dependency
    )

# Creating Tasks
def create_tasks(file_path):
    # Create agents with proper tools
    suggestion_generation_agent = create_suggestion_generation_agent(file_path)
    reporting_agent = create_reporting_agent(file_path)
    chart_generation_agent = create_chart_generation_agent()
    
    suggestion_generation = Task(
      config=tasks_config['suggestion_generation'],
      agent=suggestion_generation_agent,
      context=[]
    )

    table_generation = Task(
      config=tasks_config['table_generation'],
      agent=reporting_agent,
      context=[]
    )

    chart_generation = Task(
      config=tasks_config['chart_generation'],
      agent=chart_generation_agent,
      context=[]
    )

    final_report_assembly = Task(
      config=tasks_config['final_report_assembly'],
      agent=reporting_agent,
      context=[suggestion_generation, table_generation, chart_generation]
    )
    
    return [suggestion_generation, table_generation, chart_generation, final_report_assembly]

# Creating Crew
def create_crew(file_path):
    tasks = create_tasks(file_path)
    
    # Create agents with proper tools
    suggestion_generation_agent = create_suggestion_generation_agent(file_path)
    reporting_agent = create_reporting_agent(file_path)
    chart_generation_agent = create_chart_generation_agent()
    
    report_crew = Crew(
      agents=[
        suggestion_generation_agent,
        reporting_agent,
        chart_generation_agent
      ],
      tasks=tasks,
      verbose=True
    )
    
    return report_crew

def kickoff_crew(file_path):
    crew = create_crew(file_path)
    return crew.kickoff()

def main():
    parser = argparse.ArgumentParser(description='Process CSV file with CrewAI')
    parser.add_argument('--file-path', type=str, required=True, help='Path to the CSV file to process')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File {args.file_path} does not exist")
        sys.exit(1)
    
    print("Running Crew...")
    result = kickoff_crew(args.file_path)
    print("Crew has been kicked off successfully.")
    print("Result:", result.raw)
    
    # Save the result as a markdown file
    with open("final_report_3.md", "w", encoding="utf-8") as f:
        f.write(result.raw)
    print("Final report has been saved as 'final_report_3.md'")

if __name__ == "__main__":
    main()


