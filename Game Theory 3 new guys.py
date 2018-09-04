import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.colors as colors
from collections import Counter
import random

#####################################################
################ CONTROL PANEL ######################
#####################################################

# world dimensions
range_x = 201
range_y = 201

# zeroes -> Defectors
# ones   -> Pavlovs (If he wins, he keeps the strategy)
# twos   -> Tit for Tats (starts good and then eye for an eye)
# threes -> Cooperators
world = np.random.randint(0,4,(range_y,range_x))

# points that defector gets if he wins
b = 1.99

fps = 8
iterations = 100

#####################################################
#####################################################
#####################################################

# setting colors:
# black-defector, red-pavlov, blue-tit for tat, white-cooperator
cmap = colors.ListedColormap(['black', 'red', 'blue', 'white'])
norm = colors.BoundaryNorm([-1, 0.5, 1.5, 2.5, 4], cmap.N)

fig, ax = plt.subplots()
mat = ax.matshow(world, cmap=cmap, norm=norm)


# 1 means good (cooperate), 0 means bad (defect)
# all 4 of the lists below look like this:
# [  [[1, 0, b],   [[1, 0, b],   ...
#     [0, 1, 0],    [0, 1, 0],   ...
#     [b, 1, 1]],   [b, 1, 1]],  ...
#        ...          ...        ... ]
# so every guy in the world has his own 3x3 list of payoff 
# against neighbours and a list of moves against them
# (both from the last iteration and from now)
# 
# initial moves set to 1 for everybody ensures all tit for tats
# will start with cooperating
#
# initial payoff set to 1 (not zero) for everybody means all 
# pavlovs start as if they won in the last round, so they repeat
# what they did last, which is cooperate again
initial_moves = [[ [[1,1,1],[1,1,1],[1,1,1]] for q in range(range_x) ] for i in range(range_y)]
initial_payoff = [[ [[1,1,1],[1,1,1],[1,1,1]] for q in range(range_x) ] for i in range(range_y)]
moves = [[ [[0,0,0],[0,0,0],[0,0,0]] for q in range(range_x) ] for i in range(range_y)]
payoff = [[ [[0,0,0],[0,0,0],[0,0,0]] for q in range(range_x) ] for i in range(range_y)]


#####################################################
#################### STRATEGIES #####################
##################################################### 
def defector_strategy(k, m):
	global moves
	moves[k][m] = [[0,0,0] for q in range(3)]

def pavlov_strategy(k, m):
	# if we won any points that means the opponent cooperated
	# so let's not change what we do,
	# if we got zero let's change the move
	global initial_payoff
	global initial_moves
	global moves
	for y in range(3):
		for x in range(3):
			if initial_payoff[k][m][y][x] != 0:
				moves[k][m][y][x] = initial_moves[k][m][y][x]
			else:
				moves[k][m][y][x] = (initial_moves[k][m][y][x]+1) % 2

def tit_strategy(k, m):
	# we can recognize if someone cheated us just by the payoff
	# we got in the last round: if it's 0 -> he cheated
	global initial_payoff
	global moves
	for y in range(3):
		for x in range(3):
			if initial_payoff[k][m][y][x] == 0:
				moves[k][m][y][x] = 0
			else:
				moves[k][m][y][x] = 1

def cooperator_strategy(k, m):
	global moves
	moves[k][m] = [[1,1,1] for q in range(3)]
#####################################################
#####################################################
#####################################################


#####################################################
################# ANIMATION PART ####################
#####################################################
def init():  # only required for blitting to give a clean slate
	mat.set_data(world)
	return [mat]

def animate(i):
	print(iterations - i, 'iterations left')
	global world
	global initial_moves
	global initial_payoff
	global moves
	global payoff

	# decide the moves based on strategy
	for k in range(range_y):
		for m in range(range_x):
			if world[k, m] == 0:
				defector_strategy(k, m)
			elif world[k, m] == 1:
				pavlov_strategy(k, m)
			elif world[k, m] == 2:
				tit_strategy(k, m)
			elif world[k, m] == 3:
				cooperator_strategy(k, m)

	# calculate payoff based on moves
	for k in range(range_y):
		for m in range(range_x):
			for y in range(3):
				for x in range(3):
					if moves[k][m][y][x] == 0 and moves[(k+y-1) % range_y][(m+x-1) % range_x][2-y][2-x] == 0:
						payoff[k][m][y][x] = 0
					elif moves[k][m][y][x] == 0 and moves[(k+y-1) % range_y][(m+x-1) % range_x][2-y][2-x] == 1:
						payoff[k][m][y][x] = b
					elif moves[k][m][y][x] == 1 and moves[(k+y-1) % range_y][(m+x-1) % range_x][2-y][2-x] == 0:
						payoff[k][m][y][x] = 0
					elif moves[k][m][y][x] == 1 and moves[(k+y-1) % range_y][(m+x-1) % range_x][2-y][2-x] == 1:
						payoff[k][m][y][x] = 1	

	# a proper 2D payoff list with summed up payoff vs neighbours
	payoff_sum = np.array([[np.sum(payoff[k][m]) for m in range(range_x)] for k in range(range_y)])
	world_next = np.zeros((range_y, range_x))
	
	# find the best neighbour and adapt his strategy
	# if few neighbours have equal score, choose the strategy
	# that most of the winners use
	# if still it's a draw between them, choose randomly between
	# them
	for k in range(range_y):
		for m in range(range_x):
			# a 9 element list of scores for all neighbours 
			temp = []
			for y in range(3):
				for x in range(3):
					temp.append([payoff_sum[(k+y-1) % range_y][(m+x-1) % range_x] ])
			best_score = np.amax(temp)
			
			# to these scores append strategies to not forget them
			for y in range(3):
				for x in range(3):
					temp[3*y+x].append(world[(k+y-1) % range_y][(m+x-1) % range_x])
			
			# if the score is the best score, append the strategy
			# to winners list
			winners = []
			for element in temp:
				if element[0] == best_score:
					winners.append(element[1])

			C = Counter(winners).most_common()
			# gives sth like [(3, 2), (2, 2), (0, 1)]
			# so (strategy, how many winners around)
			# C[0][1] is the highest number of winners of 1 strat
			winners_amount = C[0][1]
			# list of strategies that share the highest number 
			# of winners
			temp = []
			for element in C:
				if element[1] == winners_amount:
					temp.append(element[0])
			# adapt random strategy from this list
			world_next[k, m] = random.choice(temp)


	# move new iteration to become the current world
	world = world_next.copy()
	initial_payoff = payoff.copy()
	initial_moves = moves.copy()

	mat.set_data(world)
	return [mat]
#####################################################
#####################################################
#####################################################

filename = 'new guys b' + str(round(b, 2)).replace('.', '_') + ' ' + str(range_x) + '_' + str(range_y) + '.mp4'

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=iterations, interval=1000/fps, blit=True)
anim.save(filename, fps=fps, extra_args=['-vcodec', 'libx264'])

#####################################################
#####################################################
#####################################################


# print % of strategies that remained
x = Counter(world.flatten())
print(filename)
print("Defectors at the end:", end=' ')
print(round(x[0] / (range_y*range_x) * 100, 2), end='')
print('%')

print("Pavlovs at the end:", end=' ')
print(round(x[1] / (range_y*range_x) * 100, 2), end='')
print('%')

print("Tit-for-tats at the end:", end=' ')
print(round(x[2] / (range_y*range_x) * 100, 2), end='')
print('%')

print("Cooperators at the end:", end=' ')
print(round(x[3] / (range_y*range_x) * 100, 2), end='')
print('%')


