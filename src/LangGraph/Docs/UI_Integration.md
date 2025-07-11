# UI Integration Documentation

## Overview

The adaptive learning system integrates the LangGraph pipeline with a Panel-based web interface. This UI allows students to submit goals and Python code, triggering backend execution through LangGraph. The interface then displays outputs from the StudentAgent, CodeRunnerAgent, and KnowledgeTracerAgent.

## Purpose

- Capture user learning goals and code inputs via UI widgets
- Trigger LangGraph pipeline execution from the Learn tab
- Display agent responses in real-time
- Handle error states and asynchronous feedback gracefully

## LangGraph Role

LangGraph is invoked directly from the Panel UI using the `graph.invoke()` method. The UI supplies a user input dictionary that includes both the student’s learning goal and code. The returned state contains results from multiple agents, which are displayed in their respective output panels.

## UI Components

### Input Fields

- **Goal Name**: TextInput
- **Description**: TextAreaInput
- **Target Date**: DatePicker
- **Code Input**: TextAreaInput
- **Priority**: Dropdown (Low, Medium, High)
- **Category**: Dropdown (Programming, Math, Science)

### Output Panels

- **Student Response Panel**: Displays StudentAgent feedback
- **Code Output Panel**: Displays stdout from CodeRunnerAgent
- **Mastery Output Panel**: Shows status and mastery level from KnowledgeTracerAgent

## Submit Button Logic

On click:

1. Validates that code input is not empty
2. Shows a temporary "Running..." message
3. Constructs the user input dictionary
4. Invokes the LangGraph pipeline:
   ```
   result = graph.invoke(user_input)
   ```
5. Parses and displays:
   - `student_output.message`
   - `code_output.stdout`
   - `tracer_output.status` and `mastery_level`

## Error Handling

If an exception occurs during graph execution:

- Displays error message in `stdout_panel`
- Clears other panels
- Logs the error for debugging

## Code Reference

Located in: `src/UI/panel_gui_tabs_jg.py`

## Commit History

- 06/26/2025 – MMA.4.3: Validated state routing and fallback logic
- 06/29/2025 – MMA.5.1: Triggered LangGraph execution from Learn tab
- 06/29/2025 – MMA.5.2: Displayed multi-agent responses in the UI
- 07/01/2025 – MMA.5.3: Validated UI refresh on repeated input

## Notes

- The UI runs via `panel serve panel_gui_tabs_jg.py`
- Designed for use with `pn.serve()` and embeddable within a notebook or web page
- Supports real-time, user-driven agent execution and monitoring
