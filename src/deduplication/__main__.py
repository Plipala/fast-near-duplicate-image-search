import argparse
import datetime
import os

from deduplication.commands.delete import delete
from deduplication.commands.search import search
from deduplication.commands.show import show
from deduplication.dataset.ImageToHash import ImageToHash
from deduplication.utils.CommandLine import CommandLine
from deduplication.utils.FileSystem import FileSystem

"""
(C) Umberto Griffo, 2019
"""


def main(args=None):

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Fast Near-Duplicate Image Search and Delete')
    parser.add_argument("command",
                        metavar="<command>",
                        type=str,
                        choices=['delete', 'show', 'search'],
                        help='delete or show or search.')
    parser.add_argument('--images-path',
                        required=True,
                        metavar="/path/to/images/",
                        type=str,
                        help='The Directory containing images.')
    parser.add_argument('--output-path',
                        required=True,
                        metavar="/path/to/output/",
                        type=str,
                        help='The Directory containing results.')
    parser.add_argument("-q",
                        "--query",
                        required=False,
                        metavar="/path/to/image/",
                        type=str,
                        help="Path to the query image")
    parser.add_argument('--tree-type',
                        required=False,
                        type=str,
                        choices=['KDTree', 'cKDTree'],
                        default='KDTree')
    parser.add_argument("--leaf-size",
                        type=int,
                        default=40,
                        help="Leaf size of the tree.")
    parser.add_argument("--hash-algorithm",
                        type=str,
                        default='phash',
                        choices=['average_hash', 'dhash', 'phash', 'whash'],
                        help="Hash algorithm to use.")
    parser.add_argument("--hash-size",
                        type=int,
                        default=8,
                        help="Hash size to use.")
    parser.add_argument("-d",
                        "--distance-metric",
                        required=False,
                        default="manhattan",
                        choices=[
                            'euclidean',
                            'l2',
                            'minkowski',
                            'p',
                            'manhattan',
                            'cityblock',
                            'l1',
                            'chebyshev',
                            'infinity',
                        ],
                        help="Distance metric to use")
    parser.add_argument("--nearest-neighbors",
                        type=int,
                        default=5,
                        help="# of nearest neighbors.")
    parser.add_argument("--threshold",
                        type=int,
                        default=25,
                        help="Threshold.")
    parser.add_argument('--parallel',
                        required=False,
                        metavar="parallel",
                        type=CommandLine.str2bool,
                        nargs='?',
                        const=True,
                        default='false',
                        help="Whether to parallelize the computation.")
    parser.add_argument("--batch-size",
                        type=int,
                        default=32,
                        help="The batch size is used when parallel is set to true.")
    parser.add_argument("--backup-keep",
                        type=CommandLine.str2bool,
                        nargs='?',
                        const=True,
                        default='true',
                        help="Whether to save the image to keep into a folder.")
    parser.add_argument("--backup-duplicate",
                        type=CommandLine.str2bool,
                        nargs='?',
                        const=True,
                        default='true',
                        help="Whether to save the duplicates into a folder.")
    parser.add_argument("--safe-deletion",
                        type=CommandLine.str2bool,
                        nargs='?',
                        const=True,
                        default='false',
                        help="Whether to execute the deletion without really deleting nothing.")
    parser.add_argument("--image-w",
                        type=int,
                        default=128,
                        help="The source image is resized down to or up to the specified size.")
    parser.add_argument("--image-h",
                        type=int,
                        default=128,
                        help="The source image is resized down to or up to the specified size.")

    if args is None:
        args = parser.parse_args()

    from deduplication._version import get_versions
    __version__ = get_versions()['version']

    dt = str(datetime.datetime.today().strftime('%Y-%m-%d-%H-%M'))

    output_path = os.path.join(args.output_path, dt)
    FileSystem.mkdir_if_not_exist(output_path)

    if args.command == "delete":
        # Config
        images_path = args.images_path
        hash_algo = args.hash_algorithm
        hash_size = args.hash_size
        tree_type = args.tree_type
        distance_metric = args.distance_metric
        nearest_neighbors = args.nearest_neighbors
        leaf_size = args.leaf_size
        parallel = args.parallel
        batch_size = args.batch_size
        threshold = args.threshold
        backup_keep = args.backup_keep
        backup_duplicate = args.backup_duplicate
        safe_deletion = args.safe_deletion
        image_w = args.image_w
        image_h = args.image_h

        df_dataset, img_file_list = ImageToHash(images_path, hash_size=hash_size, hash_algo=hash_algo) \
            .build_dataset(parallel=parallel, batch_size=batch_size)

        delete(df_dataset, img_file_list, output_path, hash_size, tree_type, distance_metric, nearest_neighbors,
               leaf_size, parallel, batch_size, threshold, backup_keep, backup_duplicate, safe_deletion, image_w,
               image_h)

    if args.command == "show":
        # Config
        images_path = args.images_path
        hash_algo = args.hash_algorithm
        hash_size = args.hash_size
        parallel = args.parallel
        batch_size = args.batch_size

        df_dataset, _ = ImageToHash(images_path, hash_size=hash_size, hash_algo=hash_algo) \
            .build_dataset(parallel=parallel, batch_size=batch_size)

        show(df_dataset, output_path)

    if args.command == "search":
        # Config
        images_path = args.images_path
        hash_algo = args.hash_algorithm
        hash_size = args.hash_size
        tree_type = args.tree_type
        distance_metric = args.distance_metric
        nearest_neighbors = args.nearest_neighbors
        leaf_size = args.leaf_size
        parallel = args.parallel
        batch_size = args.batch_size
        threshold = args.threshold
        image_w = args.image_w
        image_h = args.image_h
        query = args.query

        df_dataset, _ = ImageToHash(images_path, hash_size=hash_size, hash_algo=hash_algo) \
            .build_dataset(parallel=parallel, batch_size=batch_size)

        search(df_dataset, output_path, tree_type, distance_metric, nearest_neighbors, leaf_size, parallel, batch_size,
               threshold, image_w, image_h, query)


if __name__ == '__main__':
    main()
