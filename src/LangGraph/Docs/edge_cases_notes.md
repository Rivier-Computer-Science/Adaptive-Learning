# Documented Edge Cases and Fallback Handling

This document outlines known behavioral edge cases across LangGraph-based agents in the Adaptive Learning Platform. It captures the current handling, fallback mechanisms, and potential improvements.

---

## 1. StudentAgent: Empty Code Submission

**Edge Case:**  
User submits the form without entering Python code.

**Current Behavior:**  
- The UI blocks the request and shows a warning:  
  `❗ Please enter valid Python code before submitting.`
- No backend call is triggered.

**Suggested Improvement:**  
Disable the submit button until the code field is non-empty.

---

## 2. StudentAgent: Malformed Python Code

**Edge Case:**  
User enters syntactically invalid or broken Python code.

**Current Behavior:**  
- LangGraph attempts execution.
- Stderr is displayed in the "Code Output" panel.

**Suggested Improvement:**  
Add pre-validation of syntax in the frontend before invoking the backend.

---

## 3. StudentAgent: Runtime Errors in Code Execution

**Edge Case:**  
Code compiles but throws runtime exceptions during execution.

**Current Behavior:**  
- Exception is caught in try-except block.
- Error is shown in the "Error Output" and optionally in the "Fallback Output" panels.

**Suggested Improvement:**  
Add tags or categorization to common runtime errors and show user-friendly tips.

---

## 4. StudentAgent: No Response from Student Agent

**Edge Case:**  
LangGraph returns no valid `student_output`.

**Current Behavior:**  
- Message displayed: `No response from Student`.
- Tracer and mastery panels show fallback.

**Suggested Improvement:**  
Display a more descriptive message indicating student agent failure explicitly.

---

## 5. TracerAgent: Mastery Data Missing

**Edge Case:**  
`tracer_output` is `None` or missing key data.

**Current Behavior:**  
- Mastery panel shows: `❗ No mastery data available (fallback triggered)`.
- No crash; gracefully handled.

**Suggested Improvement:**  
Internally log fallback events; prompt retry if relevant.

---

## 6. General Fallback: LangGraph Invocation Error

**Edge Case:**  
`graph.invoke()` fails due to unhandled exceptions or corrupt inputs.

**Current Behavior:**  
- Error is caught and shown in "LangGraph error" panel.
- Optional fallback panel also shows error.

**Suggested Improvement:**  
Add retry logic or input sanitizer before invocation.

---

## 7. UI Input: Empty Goal Name

**Edge Case:**  
User submits the form without a Goal Name.

**Current Behavior:**  
- No frontend validation.
- Backend processes with an empty goal field.

**Suggested Improvement:**  
Make Goal Name a required field with red highlight on violation.

---

## 8. Mastery Score of Zero

**Edge Case:**  
Code runs successfully, but `mastery_level = 0.0` or `status = "N/A"`.

**Current Behavior:**  
- Results still displayed without explanation.
- Could confuse users.

**Suggested Improvement:**  
Add contextual message like:  
`"Code executed, but mastery evaluation indicates beginner level or mismatch."`

