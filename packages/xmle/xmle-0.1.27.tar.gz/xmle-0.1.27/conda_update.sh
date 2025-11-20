#!/bin/bash

export CONDA_RECIPE_DIR="conda-recipe"
export CONDA_BUILD_DIR="conda-build"
export CONDA_PKG_NAME="xmle"
export CONDA_PKG_VERSION="0.1.24"

conda build $CONDA_RECIPE_DIR --output-folder $CONDA_BUILD_DIR -c jpn --python 3.6
conda build $CONDA_RECIPE_DIR --output-folder $CONDA_BUILD_DIR -c jpn --python 3.7

# anaconda upload $CONDA_BUILD_DIR/osx-64/$CONDA_PKG_NAME-$CONDA_PKG_VERSION-*.tar.bz2

# conda convert --platform win-64 $CONDA_BUILD_DIR/osx-64/$CONDA_PKG_NAME-$CONDA_PKG_VERSION-*.tar.bz2 -o $CONDA_BUILD_DIR
# anaconda upload $CONDA_BUILD_DIR/win-64/$CONDA_PKG_NAME-$CONDA_PKG_VERSION-*.tar.bz2

# conda convert --platform linux-64 $CONDA_BUILD_DIR/osx-64/$CONDA_PKG_NAME-$CONDA_PKG_VERSION-*.tar.bz2 -o $CONDA_BUILD_DIR
# anaconda upload $CONDA_BUILD_DIR/linux-64/$CONDA_PKG_NAME-$CONDA_PKG_VERSION-*.tar.bz2
