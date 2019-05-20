import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import ca_requirement
import ctypes
# setting up the values for the grid
Crack = 1
No_Crack = 0
vals = [Crack, No_Crack]

# , p=[0.1, .9]
def randomGrid(N):

    """returns a grid of NxN random values"""
    return np.random.choice(vals, N*N, p=[0.1,0.9]).reshape(N, N)


def update(frameNum, img, grid, N):

    # copy grid since we require 8 neighbors
    # for calculation and we go line by line
    newGrid = grid.copy()
    count =0
    a= []

    for i in range(N):
        iteration = 0
        threshold = np.random.randint(28000,40000)
        for j in range(N):

            # compute 8-neghbor sum
            # using toroidal boundary conditions - x and y wrap around
            # so that the simulaton takes place on a toroidal surface.
            total = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] +
                         grid[(i-1)%N, j] + grid[(i+1)%N, j] +
                         grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
                         grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N])/1)


            if grid[i, j]  == Crack:
                count += 1
                a.append(count)
            elif grid[i,j] == No_Crack:
                if (total)> 3:
                    newGrid[i, j] = Crack
                    count += 1
                    a.append(count)
                elif (grid[i, (j-1)%N]+ grid[i, (j+1)%N] == 2):
                    newGrid[i, j] = Crack
                    count += 1
                    a.append(count)
                elif (grid[(i-1)%N, j]+ grid[(i-1)%N, (j-1)%N]) + grid[(i+1)%N, (j-1)%N]  == 3:
                    newGrid[i, j] = Crack
                    count += 1
                    a.append(count)
            # if grid[i,j] == No_Crack:
            #     if (total)> 3:
            #         newGrid[i, j] = Crack
            #         count += 1


    # update data
    # print(total)
    # print(count)


    img.set_data(newGrid)
    grid[:] = newGrid[:]
    # print(count)
    b = len(a)
    failure_probability = b/threshold

    if count > 9800:

        # print ('total iteration :', len(a))
        print ('failure probability :', failure_probability)
        if failure_probability >= 0.3:
            ctypes.windll.user32.MessageBoxW(0, "Need Maintenance", "Warning", 0)
        # ctypes.windll.user32.MessageBoxW(0, "Need Maintenance", "Notification", 0)
        grid[:]= randomGrid(N)
    return img,
# main() function
def main():

    # Command line args are in sys.argv[1], sys.argv[2] ..
    # sys.argv[0] is the script name itself and can be ignored
    # parse arguments
    parser = argparse.ArgumentParser(description="Runs Simulation for crack propogation.")

    # add arguments
    parser.add_argument('--grid-size', dest='N', required=False)
    parser.add_argument('--mov-file', dest='movfile', required=False)
    parser.add_argument('--interval', dest='interval', required=False)
    parser.add_argument('--glider', action='store_true', required=False)
    parser.add_argument('--gosper', action='store_true', required=False)
    args = parser.parse_args()

    # set grid size
    N = 100
    if args.N and int(args.N) > 8:
        N = int(args.N)

    # set animation update interval
    updateInterval = 1000
    if args.interval:
        updateInterval = int(args.interval)

    # declare grid
    grid = np.array([])

    # check if "glider" demo flag is specified
    if args.glider:
        grid = np.zeros(N*N).reshape(N, N)
        ca_requirement.addGlider(1, 1, grid)
    elif args.gosper:
        grid = np.zeros(N*N).reshape(N, N)
        ca_requirement.addGosperGliderGun(10, 10, grid)

    else:   # populate grid with random on/off -
            # more off than on
        grid = randomGrid(N)

    # set up animation
    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N, ),
                                  frames = 10,
                                  interval=updateInterval,
                                  save_count=50)

    # # of frames?
    # set output file
    if args.movfile:
        ani.save(args.movfile, fps=30, extra_args=['-vcodec', 'libx264'])

    plt.show()

# call main
if __name__ == '__main__':
    main()
