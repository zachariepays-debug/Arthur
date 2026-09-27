from pathlib import Path
from brain import LocalBrain

print("Initialisation d'Arthur...")

brain = LocalBrain(
    Path("models")
)

print()
print("Arthur est démarré.")
print()

answer = brain.generate(
    "Écris une fonction Python additionner(a, b) et explique très simplement ce qu'elle fait.",
    "Aucune mémoire."
)

print()
print("================================================")
print("              REPONSE D'ARTHUR")
print("================================================")
print()
print(answer)
print()
print("================================================")

brain.close()

input(
    "\nAppuie sur ENTREE pour fermer le test..."
)
