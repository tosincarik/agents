from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from stockpicker_custom.tools.push_tool import PushNotificationTool
from typing import List
from pydantic import BaseModel, Field







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
            config=self.agents_config['emerging_companies_finder'],memory=True,tools=[SerperDevTool(search_type="news")])

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'],tools=[SerperDevTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'],memory=True,tools=[PushNotificationTool()])

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


        short_term_memory = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai"
                    },
                type="short_term",
                path="./memory/"
            )
         )


        long_term_memory = LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path="./memory/long_term_memory_storage.db"
            )
         )
        
        entity_memory = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai"
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
            short_term_memory=short_term_memory,
            long_term_memory=long_term_memory,
            entity_memory=entity_memory,
            manager_agent=manager
            )


       