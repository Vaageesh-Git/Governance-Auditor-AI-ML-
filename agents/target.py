from groq import Groq

client = Groq(api_key="YOUR_GROQ_API_KEY")

class TargetAgent:

    def run(self, prompt):

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content