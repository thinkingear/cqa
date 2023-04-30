import numpy as np
from cqa.settings import MIN_PARTITION_SIZE
import math


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


"""
将完整的 dataframe 分割成若干个 partition，以便 MapReduce
"""
def partition_df(df, num_partitions):
    partition_size = max(math.ceil(len(df) / num_partitions), MIN_PARTITION_SIZE)
    partitions = []
    for i in range(0, len(df), partition_size):
        partitions.append(df[i:i + partition_size])

    return partitions
