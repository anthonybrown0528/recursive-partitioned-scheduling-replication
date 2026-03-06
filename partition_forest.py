from partition import Partition
from partition_tree import PartitionTree

class PartitionForest:
    def __init__(self, m: int):
        self.trees = []
        self.m  = m

    def create_tree(self, mi: int) -> PartitionTree:
        if mi > self.m:
            raise ValueError("Unable to allocate sufficient processors")
        
        self.m = self.m - mi
        added_tree = PartitionTree(mi)
        self.trees.append(added_tree)

        return added_tree

    def leaves(self) -> list[Partition]:
        forest_partitions = []
        for tree in self.trees:
            forest_partitions = forest_partitions + list(zip(tree.parts, [tree] * len(tree.parts), list(range(len(tree.parts)))))
        return forest_partitions