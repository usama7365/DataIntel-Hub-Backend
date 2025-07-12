import warnings
warnings.filterwarnings('ignore')

from utils import load_env
load_env()

import os
import yaml
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
    print("coming from nodejs ", file_path)
    return FileReadTool(file_path=file_path)
csv_tool = create_csv_tool('./sheet_dump/1720790400000.csv')

# Creating Agents
suggestion_generation_agent = Agent(
  config=agents_config['suggestion_generation_agent'],
  tools=[csv_tool]
)

reporting_agent = Agent(
  config=agents_config['reporting_agent'],
  tools=[csv_tool]
)

chart_generation_agent = Agent(
  config=agents_config['chart_generation_agent'],
  allow_code_execution=True
)

# Creating Tasks
suggestion_generation = Task(
  config=tasks_config['suggestion_generation'],
  agent=suggestion_generation_agent
)

table_generation = Task(
  config=tasks_config['table_generation'],
  agent=reporting_agent
)

chart_generation = Task(
  config=tasks_config['chart_generation'],
  agent=chart_generation_agent
)

final_report_assembly = Task(
  config=tasks_config['final_report_assembly'],
  agent=reporting_agent,
  context=[suggestion_generation, table_generation, chart_generation]
)

# Creating Crew
report_crew = Crew(
  agents=[
    suggestion_generation_agent,
    reporting_agent,
    chart_generation_agent
  ],
  tasks=[
    suggestion_generation,
    table_generation,
    chart_generation,
    final_report_assembly
  ],
  verbose=True
)

# def test_crew(n_iterations=1, openai_model_name='gpt-4o'):
#     return support_report_crew.test(n_iterations=n_iterations, openai_model_name=openai_model_name)

# def train_crew(n_iterations=1, filename='training.pkl'):
#     return support_report_crew.train(n_iterations=n_iterations, filename=filename)

def kickoff_crew():
    return report_crew.kickoff()
    

if __name__ == "__main__":
    print("Running Crew...")
    result = kickoff_crew()
    print("Crew has been kicked off successfully.")
    # Save the result as a markdown file
    # with open("final_report_3.md", "w", encoding="utf-8") as f:
    #     f.write(result.raw)
    # print("Final report has been saved as 'final_report.md'")


