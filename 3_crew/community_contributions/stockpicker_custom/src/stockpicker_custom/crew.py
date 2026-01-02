from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from tools.push_tool import PushNotificationTool
from typing import List
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


class Trendingcompany(BaseModel):
    """A company that is in the news and attracting attention"""
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock tikcer symbol")
    reason: str = Field(description="Reason this company is trending in the news")

class Trendincompanylist(BaseModel):
    """A list of multiple trending companies that are in the news"""
    companies: List[Trendingcompany] = Field(description="List of companies trending in the news")

class TrendingCompanyResearch(BaseModel):
    """A detailed research on a company"""
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")


class TrendingCompanyResearchList(BaseModel):
    """A list of detailed research on all the companies"""
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")


@CrewBase
class StockpickerCustom():
    """StockpickerCustom crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
 

    @agent
    def emerging_companies_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['emerging_companies_finder'],tools=[SerperDevTool(search_type="news")])

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'],tools=[SerperDevTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'],tools=[PushNotificationTool()])

    ##defining task


    @task
    def find_emerging_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_emerging_companies'],
                   output_pydantic=Trendincompanylist)


    @task
    def research_emerging_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_emerging_companies'],
            output_pydantic=TrendingCompanyResearchList)


    @task
    def pick_best_companies(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_companies'])

    @crew
    def crew(self) -> Crew:
        """Creates the StockpickerCustom crew"""
         
        manager = Agent(
            config=self.agents_config['research_manager'],
            allow_delegation=True
         )


        ShortTermMemory = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small"
                    }
                },
                type="short_term",
                path="./memory/"
            )
         )


        LongTermMemory = LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path="./memory/long_term_memory_storage.db"
            )
         )
        
        EntityMemory = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small"
                    }
                },
                type="entity",
                path="./memory/"
            )
         )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            memory=True,
            short_term_memory=ShortTermMemory,
            long_term_memory=LongTermMemory,
            entity_memory=EntityMemory,
            manager_agent=manager
            )


       