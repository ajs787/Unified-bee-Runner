# TODO: Test the steps, raise errors if something breaks
import os
import logging


def test_step_0(main_repo_name: str):
    """
    1. Check if the the git repo was created
    2. Check if there are no errors in the number of workers
    3. Check for irregulaties in the counts.csv file -> OMP,
    """
    ...


def test_step_1(main_repo_name: str):
    """
    Check if the background subtraction repo was clones
    Check log for any errors -> OMP
    """
    ...


def test_step_2(main_repo_name: str):
    """
    1. Check if the repo was clones
    2. Check if the dataset.csv file exists
    """
    ...


def test_step_3(main_repo_name: str):
    """
    1. Check if the data has been split, repo clones
    2. Check the files exist
    """
    ...


def test_step_4(main_repo_name: str):
    """
    1. Check if all the temporary dirs have been removed
    2. Check for errors in dataprep.log
    3. Check if cloned repos exists
    """
    ...


def test_step_5(main_repo_name: str):
    """
    1. Check if training run are executing
    """
    ...
