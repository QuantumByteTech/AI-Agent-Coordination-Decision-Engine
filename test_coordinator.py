from agents.coordinator import ask_coordinator

question = input("Enter your HR question: ")

answer = ask_coordinator(question)

print("\nFinal HR Response:")
print(answer)