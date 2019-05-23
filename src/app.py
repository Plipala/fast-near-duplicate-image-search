#!/usr/bin/env python
import argparse
import datetime
import os
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from natsort import natsorted
from sklearn.manifold import TSNE
from tqdm import tqdm

from dataset.ImageToHashDataset import ImageToHashDataset
from near_duplicate_image_finder.KDTreeFinder import KDTreeFinder
from near_duplicate_image_finder.cKDTreeFinder import cKDTreeFinder
from utils.CommandLineUtils import CommandLineUtils
from utils.FileSystemUtils import FileSystemUtils
from utils.ImgUtils import ImgUtils
from utils.PlotUtils import PlotUtils

"""
(C) Umberto Griffo, 2019
"""

# List mime types fully supported by Pillow
image_extensions = ['.bmp', '.jp2', 'pcx', '.jpe', '.jpg', '.jpeg', '.tif', '.gif', '.tiff', '.rgb', '.png', 'x-ms-bmp',
                    'x-portable-pixmap', 'x-xbitmap']


def get_images_list(path, natural_order=True):
    """
    Retrieve the images contained in a path.
    :param natural_order: Enable Natural sort.
    :param path: path of directory containing images.
    :return: 
    """
    file_list = os.walk(path)

    images_file_list = [os.path.join(root, file) for root, dirs, files in file_list for file in files if
                        any([file.lower().endswith(extension) for extension in image_extensions])]

    assert len(images_file_list) > 0, "The path doesn't contain images."

    if natural_order:
        images_file_list = natsorted(images_file_list)

    return images_file_list


def copy_images(df_results, output_path_in, column):
    """
    Copy the images into folders.
    :param df_results:
    :param output_path_in:
    :param column:
    :return:
    """
    for index, row in tqdm(df_results.iterrows()):
        full_file_name = row[column]

        dest_path = os.path.join(output_path_in, column)

        FileSystemUtils.mkdir_if_not_exist(dest_path)
        FileSystemUtils.copy_file(full_file_name, dest_path)


def save_results(img_file_list_in, to_keep_in, to_remove_in, hash_size_in, threshold_in, output_path_in,
                 delete_keep_in=False):
    if len(to_keep_in) > 0:
        to_keep_path = os.path.join(output_path_in,
                                    "duplicates_keep_" + str(hash_size_in) + "_dist" + str(threshold_in) + ".csv")

        duplicates_keep_df = pd.DataFrame(to_keep_in)
        duplicates_keep_df.columns = ['keep']
        duplicates_keep_df['hash_size'] = hash_size_in
        duplicates_keep_df['threshold'] = threshold_in
        duplicates_keep_df.to_csv(to_keep_path, index=False)
        copy_images(duplicates_keep_df, output_path_in, 'keep')

    if len(to_remove_in) > 0:
        to_remove_path = os.path.join(output_path_in,
                                      "duplicates_remove_" + str(hash_size_in) + "_dist" + str(threshold_in) + ".csv")
        duplicates_remove_df = pd.DataFrame(to_remove_in)
        duplicates_remove_df.columns = ['remove']
        duplicates_remove_df['hash_size'] = hash_size_in
        duplicates_remove_df['threshold'] = threshold_in
        duplicates_remove_df.to_csv(to_remove_path, index=False)
        copy_images(duplicates_remove_df, output_path_in, 'remove')

    if len(to_remove_in) > 0:
        survived_path = os.path.join(output_path_in,
                                     "survived_df" + str(hash_size_in) + "_dist" + str(threshold_in) + ".csv")
        if delete_keep_in:
            survived = list(set(img_file_list_in).difference(set(to_keep_in + to_remove_in)))
        else:
            survived = list(set(img_file_list_in).difference(set(to_remove_in)))
        print('We have found {0}/{1} not duplicates in folder'.format(len(survived), len(img_file_list_in)))
        survived_df = pd.DataFrame(survived)
        survived_df.columns = ['survived']
        survived_df['hash_size'] = hash_size_in
        survived_df['threshold'] = threshold_in
        survived_df.to_csv(survived_path, index=False)
        copy_images(survived_df, output_path_in, 'survived')


def build_tree(df_dataset, distance_metric_in, leaf_size_in, parallel_in, batch_size_in):
    if args.tree_type == 'cKDTree':
        near_duplicate_image_finder = cKDTreeFinder(df_dataset, distance_metric=distance_metric_in,
                                                    leaf_size=leaf_size_in,
                                                    parallel=parallel_in, batch_size=batch_size_in)
    elif args.tree_type == 'KDTree':
        near_duplicate_image_finder = KDTreeFinder(df_dataset, distance_metric=distance_metric_in,
                                                   leaf_size=leaf_size_in,
                                                   parallel=parallel_in, batch_size=batch_size_in)

    return near_duplicate_image_finder


def show(df_dataset_in, output_path_in):
    """
    Generating a t-SNE (t-distributed Stochastic Neighbor Embedding) of a set of images, using a feature vector for
    each image derived from the pHash function.
    :param df_dataset_in:
    :param output_path_in:
    """
    hash_str_len = len(df_dataset_in.at[0, 'hash_list'])

    # The default of 1,000 iterations gives fine results, but I'm training for longer just to eke
    # out some marginal improvements. NB: This takes almost an hour!
    tsne = TSNE(random_state=1, n_iter=15000, metric="cosine")

    embs = tsne.fit_transform(df_dataset_in[[str(i) for i in range(0, hash_str_len)]])

    # Add to dataframe for convenience
    df_dataset_in['x'] = embs[:, 0]
    df_dataset_in['y'] = embs[:, 1]

    # Save a copy of our t-SNE mapping data for later use
    df_dataset_in.to_csv(os.path.join(output_path_in, 'images_tsne.csv'))

    PlotUtils.plot_images_cluster(df_dataset_in, embs, output_path, width=4000, height=3000, max_dim=100)
    # TODO: image neigbours
    # PlotUtils.plot_region_around(df_dataset_in, '2018-12-11-15-031193.png')
    # plt.show()


if __name__ == '__main__':

    dt = str(datetime.datetime.today().strftime('%Y-%m-%d-%H-%M'))

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Fast Near-Duplicate Image Search and Delete')
    parser.add_argument("command",
                        metavar="<command>",
                        type=str,
                        choices=['delete', 'show', 'search'])
    parser.add_argument('--images-path',
                        required=True,
                        metavar="/path/to/images/",
                        type=str,
                        help='Directory containing images.')
    parser.add_argument('--output-path',
                        required=True,
                        metavar="/path/to/output/",
                        type=str,
                        help='Directory containing results.')
    parser.add_argument("-q",
                        "--query",
                        required=False,
                        metavar="/path/to/image/",
                        type=str,
                        help="path to the query image")
    parser.add_argument('--tree-type',
                        required=False,
                        metavar="KDTree or cKDTree",
                        type=str,
                        choices=['KDTree', 'cKDTree'],
                        default='KDTree')
    parser.add_argument('--parallel',
                        required=False,
                        metavar="parallel",
                        type=CommandLineUtils.str2bool,
                        nargs='?',
                        const=True,
                        default='false',
                        help="Whether to parallelize the computation.")
    parser.add_argument("--delete-keep",
                        type=CommandLineUtils.str2bool,
                        nargs='?',
                        const=True,
                        default='false',
                        help="Whether to delete the origin of duplication.")
    parser.add_argument("--hash-algorithm",
                        type=str,
                        default='phash',
                        choices=['average_hash', 'dhash', 'phash', 'whash'],
                        help="hash algorithm")
    parser.add_argument("--hash-size",
                        type=int,
                        default=8,
                        help="hash size")
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
                        help="distance metric")
    parser.add_argument("--nearest-neighbors",
                        type=int,
                        default=5,
                        help="# of nearest neighbors")
    parser.add_argument("--leaf-size",
                        type=int,
                        default=40,
                        help="leaf size")
    parser.add_argument("--batch-size",
                        type=int,
                        default=32,
                        help="batch size")
    parser.add_argument("--threshold",
                        type=int,
                        default=25,
                        help="threshold")
    parser.add_argument("--image-w",
                        type=int,
                        default=128,
                        help="image width")
    parser.add_argument("--image-h",
                        type=int,
                        default=128,
                        help="image height")
    args = parser.parse_args()

    # Validate arguments
    if args.command == "delete":
        assert args.tree_type, "Argument --tree-type is required for deleting"

    output_path = os.path.join(args.output_path, dt)
    FileSystemUtils.mkdir_if_not_exist(output_path)

    if args.command == "delete":
        # Config
        images_path = args.images_path
        hash_algo = args.hash_algorithm
        hash_size = args.hash_size
        distance_metric = args.distance_metric
        nearest_neighbors = args.nearest_neighbors
        leaf_size = args.leaf_size
        parallel = args.parallel
        batch_size = args.batch_size
        threshold = args.threshold
        delete_keep = args.delete_keep
        image_w = args.image_w
        image_h = args.image_h

        # Retrieve the images contained in output_path.
        img_file_list = get_images_list(images_path, natural_order=True)
        # Build the dataset
        df_dataset = ImageToHashDataset(img_file_list, hash_size=hash_size, hash_algo=hash_algo).build_dataset(
            parallel=parallel,
            batch_size=batch_size)
        # Build the tree
        near_duplicate_image_finder = build_tree(df_dataset, distance_metric, leaf_size, parallel, batch_size)
        # Find duplicates
        to_keep, to_remove, dict_image_to_duplicates = near_duplicate_image_finder.find_all_near_duplicates(
            nearest_neighbors,
            threshold)
        total_report = to_keep + to_remove
        print('We have found {0}/{1} duplicates in folder'.format(len(to_remove), len(img_file_list)))
        # Save results
        save_results(img_file_list, to_keep, to_remove, hash_size, threshold, output_path, delete_keep_in=delete_keep)
        # Show a duplicate
        if len(dict_image_to_duplicates) > 0:
            random_img = random.choice(list(dict_image_to_duplicates.keys()))
            near_duplicate_image_finder.show_an_image_duplicates(dict_image_to_duplicates, random_img, output_path,
                                                                 image_w=image_w,
                                                                 image_h=image_h)

    if args.command == "show":
        # Config
        images_path = args.images_path
        hash_algo = args.hash_algorithm
        hash_size = args.hash_size
        parallel = args.parallel
        batch_size = args.batch_size

        # Retrieve the images contained in images_path.
        img_file_list = get_images_list(images_path, natural_order=True)
        # Build the dataset
        df_dataset = ImageToHashDataset(img_file_list, hash_size=hash_size, hash_algo=hash_algo).build_dataset(
            parallel=parallel,
            batch_size=batch_size)
        show(df_dataset, output_path)

    if args.command == "search":
        # Config
        images_path = args.images_path
        hash_algo = args.hash_algorithm
        hash_size = args.hash_size
        distance_metric = args.distance_metric
        nearest_neighbors = args.nearest_neighbors
        leaf_size = args.leaf_size
        parallel = args.parallel
        batch_size = args.batch_size
        threshold = args.threshold
        delete_keep = args.delete_keep
        image_w = args.image_w
        image_h = args.image_h
        query = args.query

        # Retrieve the images contained in images_path.
        img_file_list = get_images_list(images_path, natural_order=True)
        # Build the dataset
        df_dataset = ImageToHashDataset(img_file_list, hash_size=hash_size, hash_algo=hash_algo).build_dataset(
            parallel=parallel,
            batch_size=batch_size)
        # Build the tree
        near_duplicate_image_finder = build_tree(df_dataset, distance_metric, leaf_size, parallel, batch_size)
        # Get the image's id
        image_id = df_dataset[df_dataset['file'] == query].index.values.astype(int)[0]
        # Find the images's near duplicates
        distances, indices = near_duplicate_image_finder.find_near_duplicates(image_id, nearest_neighbors, threshold)
        # Show the near duplicates
        if len(distances) > 0 and len(indices) > 0:

            for distance, idx in zip(distances, indices):
                print("{0} distance:{1}".format(df_dataset.iloc[idx]['file'], distance))

            image_path = df_dataset.iloc[image_id]['file']
            files_to_show = []
            files_to_show.append(ImgUtils.scale(ImgUtils.read_image_numpy(image_path, image_w, image_h)))

            duplicates_path = [f for f in list(df_dataset.iloc[indices]['file'])]
            duplicates_arr = [ImgUtils.scale(ImgUtils.read_image_numpy(f, image_w, image_h)) for f in duplicates_path]
            files_to_show.extend(duplicates_arr)
            fig_acc = plt.figure(figsize=(10, len(files_to_show) * 5))
            plt.imshow(ImgUtils.mosaic_images(np.asarray(files_to_show), len(files_to_show)))
            fig_acc.savefig(os.path.join(output_path, image_path.split(os.path.sep)[-1]))
            plt.show()
            plt.cla()
            plt.close()
        else:
            print("The image doesn't have near duplicates.")
