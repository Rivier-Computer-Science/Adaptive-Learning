# --- Payload definition ---
test_payload_1 = {
    "student_input": {
        "goal_name": "Learn Loops",
        "description": "Understand for-loops in Python",
        "target_date": "2025-07-31",
        "priority": "High",
        "category": "Programming"
    },
    "code_input": "for i in range(5): print(i)"
}

# --- Pipeline test function with logging ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from LangGraph.workflow.langgraph_main import graph

def test_pipeline_run_with_logging():
    try:
        result = graph.invoke(test_payload_1)

        print("\n Final Result:")
        print(result)

        if "code_output" in result:
            print("\n Code Output:")
            print("stdout:", getattr(result["code_output"], 'stdout', ''))
            print("stderr:", getattr(result["code_output"], 'stderr', ''))

        if "student_output" in result:
            print("\n Student Agent:")
            print("message:", getattr(result["student_output"], 'message', ''))

        if "tracer_output" in result:
            print("\n Tracer Output:")
            print("status:", result["tracer_output"].status)
            print("mastery_level:", result["tracer_output"].mastery_level)

        if "error" in result:
            print("\n Error:")
            print(result["error"])

    except Exception as e:
        print(f"\n Exception occurred during pipeline execution: {e}")
if __name__ == "__main__":
    test_pipeline_run_with_logging()
