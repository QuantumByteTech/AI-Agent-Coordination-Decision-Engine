from agents.hr_agent import ask_hr_agent

question = input("Enter your HR question: ")

answer = ask_hr_agent(question)

print("\nHR Assistant:")
print(answer)