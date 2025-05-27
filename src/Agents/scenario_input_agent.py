from pydantic import BaseModel

class ScenarioInput(BaseModel):
    scenario: str  # e.g., "Increase topic difficulty for student"

class ScenarioOutput(BaseModel):
    parsed_topic: str
    difficulty_level: str
    
def run(input: ScenarioInput) -> ScenarioOutput:
    # Simulate extracting structured info from the scenario string
    if "increase" in input.scenario.lower():
        topic = "mathematics"
        level = "hard"
    else:
        topic = "general"
        level = "medium"

    return ScenarioOutput(parsed_topic=topic, difficulty_level=level)
