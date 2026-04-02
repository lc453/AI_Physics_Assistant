# AI-Powered Physics Assistant
Designed to work with an LLM hosted locally using KoboldCpp, however a different service can be used by updating the port and adding any credentials if needed.

The Assistant can currently answer simple physics questions, and if it needs to run any calculations to do so, it has access to a calculator tool powered by SymPy.
Since the calculator runs whatever code the Assistant puts in the function, the calculator function implements robust safety measures to ensure only mathematical functions are used.
