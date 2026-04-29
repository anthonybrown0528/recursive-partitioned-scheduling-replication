from partition import Partition
from partition_tree import PartitionTree

class PartitionForest:
    """Contains a collection of partitions

    :param trees: a list of :class:`PartitionTree` objects
    :type trees: class:`PartitionTree`

    :param m: the number of available processors
    :type m: int
    """

    def __init__(self, m: int):
        """Initialize the :class:`PartitionForest`

        :param m: number of available processors
        :type m: int
        """

        self.trees = []
        self.m  = m

    def create_tree(self, mi: int) -> PartitionTree:
        """Create a new :class:`PartitionTree` and add it to the forest
        
        :param mi: number of processors to allocate to the new tree
        :type mi: int

        :return: a new :class:`PartitionTree` object
        :rtype: PartitionTree
        """

        if mi > self.m:
            raise ValueError("Unable to allocate sufficient processors")
        
        self.m = self.m - mi
        added_tree = PartitionTree(mi)
        self.trees.append(added_tree)

        return added_tree

    def leaves(self):
        """Yields a tuple of :class:`Partition` and :class:`PartitionTree`
        """

        for tree in self.trees:
            for partition in tree.parts:
                yield partition, tree