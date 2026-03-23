class HumanReviewAgent:

    def review(self, prompt, response, evaluation):

        print("\n--- HUMAN REVIEW REQUIRED ---")
        print("Prompt:", prompt)
        print("Response:", response[:200])
        print("Evaluation:", evaluation)

        decision = input("Approve or Reject? (a/r): ")

        if decision.lower() == "r":
            return "REJECTED"
        
        return "APPROVED"