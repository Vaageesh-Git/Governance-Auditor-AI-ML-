from core.orchestrator import Orchestrator

if __name__ == "__main__":

    system = Orchestrator()

    for i in range(3):
        print(f"\n--- Cycle {i+1} ---")
        system.run_cycle()