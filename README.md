# swarm-tools
Tools that run on top of slurm, in particular `swarm` and helper scripts for easily submitting big slurm array jobs.
swarm was ported from the US National Institutes of Health HPC cluster, previously known as biowulf. See also the current (?) [NIH-HPC swarm](https://github.com/NIH-HPC/swarm).

## Motivation

Array jobs are the easiest slurm method for bundling multiple related jobs. Typically one array job would contain separate processes that are part of the same overall processing step. This can be done using your own sbatch scripts, but this requires constantly modifying sbatch scripts, creating separate run scripts and controlling log files with process outputs / errors. A script was developed at the NIH called [swarm](https://hpc.nih.gov/apps/swarm.html) that automates this process so that the only requirement is a single file that contains a single command-line per process that you would like to run in parallel. swarm still allows command line parameters / directives to be passed to sbatch directly. swarm has been modified in this repository so that it works on the axon and soma (MPINB&mdash;caesar) clusters. It has also been given more flexible packing / bundling options, meaning that the functionality and usage has diverged from the original biowulf swarm. The toolchain also includes a few other convenience scripts, some also ported from biowulf. It has also been extended so that it can also create pipelines of jobs with dependencies (simple workflows).

## Dependencies

- bash
- perl5
- python3
  - numpy
  - python-dateutil
- slurm

NOTE: Theoretically specific versions do not matter much since the scripts are relatively simple. Thus specifically tested versions have been omitted (xxx).

NOTE: None of the toolchain has been tested using any other shell besides bash. Some things likely will break.

## Installation

Clone this repo. Copy the bin directory to somewhere in your path, or a new dir and add to your path.
Everything below this point will assume that you copied the bin directory to `~/biowulf_bin`:
```
cp -R bin ~/biowulf_bin
```

Required additions to `~/.bashrc` (on the soma clusters recommend adding to `~/.bash_profile`):
```
# modify me appropriately depending on where swarm-tools/bin contents were copied to:
PATH=$PATH:$HOME/biowulf_bin

# modify me to point to the location of the user scratch dir (cluster dependent)
export SCRATCH=/gpfs/soma_fs/scratch/$USER
export SWARMDIR=${SCRATCH}/swarm
export DELDIR=${SCRATCH}/.to_delete

# clears all the swarm command files and logs, must be done periodically
alias swarmc="mkdir -p $DELDIR; mv $SWARMDIR $DELDIR; mkdir -p $SWARMDIR/logs; nohup rm -rf $DELDIR/swarm >/dev/null 2>&1 &"
```

After modifying `.bashrc` or `.bash_profile`, either re-`source` it or log out and back in.

You need python3 with a few basic modules (i.e., anaconda3 would work). If you do not have this you can create a conda environment that would work (after installing miniconda), for example:
```
conda create -y --name swarm numpy python-dateutil
```

## Getting Started / Short Tutorial

### One-time initializations

Initialize the required directories:
```
swarmc
```
NOTE: This also MUST be done periodically. `swarm` writes command files for each slurm array job, so eventually this will create lots and lots of small files in your scratch dir (and you will be unnecessarily wasting inode space).

Create a location for your batch runs, highly recommended is your user scratch directory:
```
mkdir -p $SCRATCH/batches
cd $SCRATCH/batches
```
Scratch is preferred because typically scratch is not backed up, and a use case in which these batch log files need to be backed up is unlikely.

### Run some test jobs using the swarm toolchain

Activate an appropriate python env (or your own with minimal dependencies installed, see Installation):
```
conda activate swarm
```

Check node availability / usage:
```
freen
```

In case you are not satisfied, look at everyone else's jobs:
```
sjobs -an
```

Copy demo files from the swarm-tools repo into your `batches` directory:
```
cd $SCRATCH/batches
cp -R ~/gits/swarm-tools/demo .
cd demo/
```
NOTE: the script for this demo just idles cpus; do not make a habit of this.

`swarm` always processes swarm files, which contain a single command line to be executed per line. You can of course create these manually, but the toolchain includes a script to automate this, particularly useful if your swarm files exceed a few 10s of lines.

Create the swarm files:
```
for i in {1..6}; do
create_swarm --set-env python --run-script ../idle.py --beg-args iprocess --other-flags " --idle_time_secs 15 --nprocesses 240 " --iterate-ranges 0 240 --id-str test-${i}
done
for i in {7..8}; do
create_swarm --set-env python --run-script ../../../idle.py --beg-args iprocess --other-flags " --idle_time_secs 15 --nprocesses 240 " --iterate-ranges 0 240 --id-str test-${i}
done
```

Demo / verify the submissions:
```
pipeline --workflow-file demo-soma-pipeline.txt --mock-run
```
There should not be any errors, but just a printout of the submission commands for each line (`rolling_submit`).

Submit:
```
pipeline --workflow-file demo-soma-pipeline.txt
```

Check your jobs while they are running or pending:
```
sjobs
```

Once your jobs are completed, validate that they ran to completion without errors:
```
pipeline --workflow-file demo-soma-pipeline.txt --validate
```

Create detailed job histories:
```
jobhist .
```
This creates a file in each subdirectory called `jobhist.txt` that contains the `sacct` information and the `swarm` and `sbatch` command lines for each array job. Alternatively one can show the job history for a specific job with `jobhist <jobid>`. For convenience job ids are stored in each directory created by `rolling_submit` (called by `pipeline`) in a file called `job_id.txt`.

Clean up your log files periodically (again to not waste inode space):
```
tar_swarms . --verbose
```

## Manifest

The complete toolset (contents of bin) categorized by language each script is written in:

bash
  - aswarm
  - mrolling_submit
  - rolling_submit
  - tar_swarms

perl
  - batchlim *
  - swarm *

python
  - freen *
  - jobhist *
  - sjobs **
  - pipeline
  - create_swarm

(*) Indicates original biowulf scripts that have been ported / modified.

(**) Indicates original biowulf scripts in name/spirit only that have been entirely rewritten.

Job submission tool hierarchy:

  - pipeline -> [mrolling_submit] -> rolling_submit -> aswarm -> swarm -> sbatch

NOTE: mrolling_submit support from pipeline is optional. This allows for "master job" rolling submission.

NOTE: jobs can be submitted starting at any level in the hierarchy.

Utility tools (not part of the submission hierarchy):

  - create_swarm
  - sjobs
  - jobhist
  - freen
  - batchlim
  - tar_swarms

### TODOS

xxx - short term, consider doing away with bash scripts and move to python?

xxx - long term, rewrite swarm in python (major task)
