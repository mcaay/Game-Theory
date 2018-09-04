# Game-Theory 
In a nutshell: 
Imagine 2 robbers were caught by the police. The police knows that at least 1 of them robbed the bank but is not sure who. 
They are now being interviewed independently.
Now if both of them admit they did it (both cooperate) they both get a small sentence because they admitted it. 
If one says it was the other one (cheats) and the other one admits it (cooperates), the first one gets away free (he won) and 
the second one gets a big sentence (he lost). 
If both point to the other guy they both get a big sentence (both lose). 

In the program it looks like this:
1) we both cooperate = 1 point for everyone; 
2) we both cheat = 0 points for everyone; 
3) you cheat and I cooperate = you win (X points) and I lose (0 points); 
4) I cheat and you cooperate = I win (X points) and you lose (0 points). 

Then we have a big 2D grid of guys, and everybody after an interation adapts the best strategy from his neighbors (or could
be his own if he won). 
