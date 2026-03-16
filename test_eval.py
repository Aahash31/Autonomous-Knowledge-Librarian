from agent import app  # Imports your LangGraph workflow

# Test cases with different inputs to evaluate model
test_cases = [
    {"question": "When are my taxes due?", "expected_keyword": "april"},
    {"question": "Hello!", "expected_keyword": "hello"}, 
    {"question": "Why should I attend the capstone meeting?", "expected_keyword": "presentation"},
    {"question": "What is the secret recipe for the Librarian's favorite soup?", "expected_keyword": "don't know"}
]

print("Starting Pipeline...\n")
passed_tests = 0

# Run automated test loop
for i, test in enumerate(test_cases):
    print(f"Running Test {i+1}: '{test['question']}'")
    
    # Uses unique thread ID for each test case (starts with a blank memory slate)
    config = {"configurable": {"thread_id": f"eval_session_{i}"}}
    output = app.invoke({"messages": [("user", test["question"])]}, config)
    ai_response = output["messages"][-1].content.lower()
    print(f"AI Response: {ai_response}")
    
    if test["expected_keyword"] in ai_response:
        print("PASS\n")
        passed_tests += 1
    else:
        print(f"FAIL - Expected keyword '{test['expected_keyword']}' not found.\n")

print(f"Final QA Score: {passed_tests}/{len(test_cases)} Passed")