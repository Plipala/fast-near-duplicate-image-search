# Fast Near-Duplicate Image Search using pHash and KDTree.
* Author: Umberto Griffo
* Twitter: @UmbertoGriffo

Disclaimer
==========
I take no responsibility for bugs in this script or accidentally deleted pictures. 
Use at your own risk. Make sure you back up your pictures before using.

## pHash definition

Features in the image are used to generate a distinct (but not unique) fingerprint, and these fingerprints are comparable.
**Perceptual hashes** are a different concept compared to cryptographic hash functions like **MD5** and **SHA1**.
With cryptographic hashes, the hash values are random. The data used to generate the hash acts like a random seed, 
so the same data will generate the same result, but different data will create different results.
Comparing two **SHA1** hash values really only tells you two things. 
If the hashes are different, then the data is different. 
And if the hashes are the same, then the data is likely the same. 
(Since there is a possibility of a hash collision, having the same hash values does not guarantee the same data.) 
In contrast, perceptual hashes can be compared giving you a sense of similarity between the two data sets.
Using pHash images can be scaled larger or smaller, have different aspect ratios, and even minor coloring differences 
(contrast, brightness, etc.) and they will still match similar images.

## KDTree definition
A **KDTree** (short for k-dimensional tree) is a space-partitioning data structure for organizing 
points in a k-dimensional space. 
In particular, KDTree helps organize and partition the data points based on specific conditions.
KDTree is a useful for several applications, such as searches involving a multidimensional search key (e.g. range searches and nearest neighbor searches).

### Complexity (Average)

|Scape|Search|Insert|Delete|
|-----|-----|-----|-----|
|O(n)|O(log n)|O(log n)|O(log n)|

where **n** is the number of points.

## Mixing pHash and KDTree in order to detect Near-Duplicate Faster

To find similar images I hash the images using **pHash** from [ImageHash](https://pypi.org/project/ImageHash/) library,
then I build a **KDTree** and perform a **nearest neighbours** search on image hashes.

SW Environment
==============
#### Let’s create an Anaconda environments
```
conda create -n fast_near_duplicate_img_src_py3 python=3.6
```

 To activate this environment, use:
 > source activate fast_near_duplicate_img_src_py3

 To deactivate an active environment, use:
 > source deactivate

#### Install the basic libraries
```
source activate fast_near_duplicate_img_src_py3
conda install pip pandas scikit-learn scipy numpy matplotlib seaborn pillow natsort==5.5.0 tqdm
```
#### OpenCV 4.0.0.21
```
apt install libgtk2.0-dev python3-tk
pip install opencv-contrib-python==4.0.0.21
```
#### Pytest 4.1.1 in order to develop Unit/Mock test
```
pip install -U pytest
```
#### ImageHash 4.0 - Image Hashing library
```
pip install ImageHash
```

To package an Anaconda environment
==================================
#### To export environment file
```
conda env export -n fast_near_duplicate_img_src_py3 > environment.yml
```
#### For other person to use the environment:
```
conda env create -f fast_near_duplicate_img_src_py3.yml
```

Todo
====
- [X] https://www.kaggle.com/colinmorris/visualizing-embeddings-with-t-sne
- [] https://github.com/philipbl/duplicate-images
- [] https://github.com/knjcode/imgdupes
- [] https://github.com/zegami/image-similarity-clustering
- [] Use Locality Sensitive Hashing instead of KDTree.
    - https://towardsdatascience.com/locality-sensitive-hashing-for-music-search-f2f1940ace23
    - https://towardsdatascience.com/fast-near-duplicate-image-search-using-locality-sensitive-hashing-d4c16058efcb

References
==========

* [ImageHash](https://pypi.org/project/ImageHash/)
* [ImageHash - Official Github repository](https://github.com/JohannesBuchner/imagehash)
* [KDTree - Wikipedia](https://en.wikipedia.org/wiki/K-d_tree)
* [Introductory guide to Information Retrieval using kNN and KDTree](https://www.analyticsvidhya.com/blog/2017/11/information-retrieval-using-kdtree/)
* [Perceptual Hash computation](http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.htm)