#!/usr/bin/bash 
source venv/bin/activate 
# batch file for getting the training results 
 
cd /research/projects/grail/dyd7/orig-files 
echo start-is: `date` 
 
sbatch -G 3 -c 8  -n 4  --mem=300G  --time=28800  -o dataset_trainlog_0.log train_0.sh 
sbatch -G 3 -c 8  -n 4  --mem=300G  --time=28800  -o dataset_trainlog_1.log train_1.sh 
#sbatch -G 3 -c 8  -n 4  --mem=300G  --time=28800  -o dataset_trainlog_2.log train_2.sh 
echo end-is: `date` 
 
