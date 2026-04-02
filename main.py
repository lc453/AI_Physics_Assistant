from kobold_agent import run_agent

if __name__ == "__main__":
    while True:
        query = input("Ask a physics question: ")
        if query.lower() in ["exit", "quit"]:
            break

        result = run_agent(query)
        print("\nFinal Answer:", result, "\n")