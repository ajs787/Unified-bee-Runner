# Unified Bee Runner

Unified Bee Runner is a pipeline for processing and analyzing bee-related datasets. This project includes several steps such as dataset creation, video conversion, data splitting, and model training. The model is meant to run on ilab, and through slurm.

## Pipeline

![PipelineImage](RunImage.png)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Pipeline Steps](#pipeline-steps)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/Elias2660/Unified-bee-Runner.git
   ```

## Usage

To run the pipeline, use the provided [shell script](Unifier_Run.sh) in [SLURM](https://slurm.schedmd.com/documentation.html). If you don't want to, please copy the [Unifier_Run.sh](Unifier_Run.sh) file and execute it in your command line:

Run `squeue -u <user>` to be able to find your current jobs and the servers that they are running on.

You can edit the [Unifier_Run.sh](Unifier_Run.sh) file with the settings that you desire. You can check the settings by running `python3 Unified-bee-Runner/master_run.py -h` or checking in [ArgParser.py](ArgParser.py) for the arguements that can be used. Not all of them work, including those that crop, and this pipeline is still working through many bugs.

Then run:

```sh
sbatch -x [servers, such as server1,server2] Unified-bee-Runner/Unifier_Run.sh
```

## Pipeline Steps

This is run using the chapter system, so you can choose the specific steps that are used here by editing the `--start` and `--end` commands, which are by default respectively set at 0 and 6. 

0. `Video Conversion and Counting`: Converts .h264 videos to .mp4 format and creates counts.csv. ([link](https://github.com/Elias2660/Video_Frame_Counter))
1. `Background Subtraction`: Applies background subtraction to the video frames to isolate the bees ([link](https://github.com/Elias2660/Video_Subtractions))
2. `Dataset Creation`: Creates the dataset.csv ([link](https://github.com/Elias2660/Dataset_Creator))
2. `Data Splitting`: Splits the data into training and testing sets ([link](https://github.com/Elias2660/working_bee_analysis/blob/main/make_validation_training.py))
3. `Video Sampling`: Clones the VideoSamplerRewrite repository and samples the video frames ([link](https://github.com/Elias2660/VideoSamplerRewrite))
4. `Model Training`: Runs the model training script ([link](https://github.com/Elias2660/working_bee_analysis/blob/main/VidActRecTrain.py))

## Contributing

[Contributions](CONTRIBUTING.md) are welcome! Please open an issue or submit a pull request.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## [Security Policy](SECURITY.md)

### Reporting a Vulnerability

If you discover a security vulnerability within this project, please report it. We will respond to your report promptly and work with you to understand and address the issue.

## License

This project is licensed under the [MIT License](LICENSE).
