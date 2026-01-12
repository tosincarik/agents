import warnings

from datetime import datetime

from latest_market_research.crew import LatestMarketResearch

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    inputs = {
        'Sector': 'Technology'
    }

    #Create and run the crew

    result = LatestMarketResearch.crew().kickoff(inputs=inputs)


    #Print the result
    print("\n\n===Final Decision ===\n\n")
    print(result.raw)


if __name__=="__main__":
    run()