from src.Agents.conversable_agent import MyConversableAgent

class CompetencyExtractionAgent(MyConversableAgent):
    """
    Agent responsible for extracting required competencies from a career description or path.
    It leverages LLM to analyze career metadata and identify essential skills, knowledge areas, and proficiencies.
    """
    def __init__(self, llm_config=None):
        super().__init__(
            name="CompetencyExtractionAgent",
            llm_config=llm_config,
            system_message=self._system_message(),
            description="Extracts key competencies required for a given career path or role."
        )

    def _system_message(self):
        return (
            "You are the CompetencyExtractionAgent. You analyze career descriptions and role expectations to identify "
            "critical competencies and skills. Return a structured list of technical and soft skills, knowledge areas, "
            "and any required proficiencies needed for the target career path. Output should be clear and organized."
        )

    def extract_competencies(self, career_description: str) -> str:
        """
        A helper method to trigger the agent directly with a string of career info.
        """
        self.send(
            message=f"Extract the required competencies from the following description: {career_description}",
            recipient=self
        )
        return self.last_message(agent=self)["content"]
