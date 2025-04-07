import matplotlib.pyplot as plt
import numpy as np

def k_means_cluster(k, points):
    # Initialization: choose k centroids (Forgy, Random Partition, etc.)
    centroids = np.random.choice(points, k, replace=False)

    # Initialize clusters list
    clusters = [[] for _ in range(k)]

    # Loop until convergence
    converged = False
    while not converged:
        # Clear previous clusters
        clusters = [[] for _ in range(k)]

        # Assign each point to the "closest" centroid
        for point in points:
            distances_to_each_centroid = [np.abs(point - centroid) for centroid in centroids]
            cluster_assignment = np.min(distances_to_each_centroid)
            clusters[cluster_assignment].append(point)

        # Calculate new centroids
        #   (the standard implementation uses the mean of all points in a
        #     cluster to determine the new centroid)
        new_centroids = [np.mean(cluster) for cluster in clusters]

        converged = (new_centroids == centroids).all()
        centroids = new_centroids

        if converged:
            return clusters

if __name__ == '__main__':
    # create a bunch of players represented by their MMR and their request start time in s
    player_count = 1000
    min_mmr = 1000
    max_mmr = 1200

    players = []
    for i in range(0, player_count):
        players.append(np.random.randint(min_mmr, max_mmr))

    # plot players histogram
    plt.hist(players, bins=50)
    plt.xlabel('MMR')
    plt.ylabel('Number of Players')
    plt.title('Players MMR Distribution')
    plt.show()

    # find numbers of possible matches (4 players per match)
    match_size = 4
    match_count = player_count // match_size

    print(f'Number of matches: {match_count}')

    # k means
    matches = k_means_cluster(match_count, players)

    # print matches with average MMR, average request start time, and players in the match
    for match in matches:
        print(f'Match average MMR: {np.mean(match)}')
        print('Players:')
        for player in match[2]:
            print(player)
        print()