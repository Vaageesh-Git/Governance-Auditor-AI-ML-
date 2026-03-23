from agents.red_team import RedTeamAgent
from agents.target import TargetAgent
from agents.judge import JudgeAgent
from agents.policy import PolicyAgent
from agents.human_review import HumanReviewAgent
from core.memory import Memory


class Orchestrator:

    def __init__(self):

        self.red = RedTeamAgent()
        self.target = TargetAgent()
        self.judge = JudgeAgent()
        self.policy = PolicyAgent()
        self.human = HumanReviewAgent()
        self.memory = Memory()

    def run_cycle(self):

        # Step 1: Generate prompt
        prompt = self.red.generate()

        # Step 2: Get model response
        response = self.target.run(prompt)

        # Step 3: Evaluate
        evaluation = self.judge.evaluate(prompt, response)

        # Step 4: Policy decision
        decision = self.policy.decide(evaluation, self.memory.violations)

        # Step 5: Human review
        if decision in ["ESCALATE", "CRITICAL"]:
            decision = self.human.review(prompt, response, evaluation)

        # Step 6: Log
        log = {
            "prompt": prompt,
            "response": response,
            "evaluation": evaluation,
            "decision": decision
        }

        self.memory.update(log)

        # Step 7: Print result
        print("\n===== RESULT =====")
        print("Prompt:", prompt)
        print("Decision:", decision)
        print("Evaluation:", evaluation)