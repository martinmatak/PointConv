# This file handles all our argument hyperparameters and setting up the training.

import argparse
import os
import sys

# Get our model functions:
from sdf_model import get_fc_model, get_fc_no_bn_model, get_fc_no_bn_dropout_model, get_fc_small_model, get_fc_no_bn_small_model
from sdf_pointconv_deep_model import get_pointconv_deep_model, get_pointconv_deep_bn_model
from sdf_pointconv_model import get_pointconv_model

# Get running function.
from run_sdf_model import run, extract_voxel

import pdb

# Use the folder of the script to determine save/load/log paths etc.
parent_dir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description='Run SDF model.')
parser.add_argument('--learning_rate', type=float, help='Initial learning rate.', default=1e-5)
parser.add_argument('--optimizer', type=str, help='Optimizer to use [adam, momentum].', default='adam')
parser.add_argument('--model_func', type=str, help='Model function to call.', default='pointconv', required=True)
parser.add_argument('--model_name', type=str, help='Model name for logging/saving.', default='model_name', required=True)

parser.add_argument('--warm_start', dest='warm_start', action='store_true', help='Whether to continue training from the model of the given name.')
parser.set_defaults(warm_start=False)

parser.add_argument('--batch_size', type=int, help='Batch size to run.', default=16)
parser.add_argument('--epochs', type=int, help='Epochs to run.', default=1000)
parser.add_argument('--epoch_start', type=int, help='If continuing a run, the epoch number to start at.', default=0)

parser.add_argument('--training', dest='training', action='store_true', help='If training this run.')
parser.add_argument('--testing', dest='training', action='store_false', help='If testing this run.')
parser.set_defaults(training=True)

# Data inputs.
parser.add_argument('--train_path', type=str, help='Path to Training folder.', required=True)
parser.add_argument('--validation_path', type=str, help='Path to Validation folder.', required=True)
parser.add_argument('--pc_h5_file', type=str, help='Path to Point Cloud h5 file.')

parser.add_argument('--alpha', type=float, help='Alpha for loss tradeoff between voxel and SDF.', default=0.5)
parser.add_argument('--loss_function', type=str, help='Loss function to use.', default='mse')

parser.add_argument('--voxelize', dest='voxelize', action='store_true', help='If should create a voxel.')
parser.set_defaults(voxelize=False)

parser.add_argument('--sdf_count', type=int, help='Number of SDF points to run together for each example. Points are randomly down sampled to this count.', default=64)

args = parser.parse_args()

# Set up model/logging folders as needed.
model_folder = os.path.join(parent_dir, 'model/' + args.model_name)
if not os.path.exists(model_folder):
   os.mkdir(model_folder)
logs_folder = os.path.join(parent_dir, 'logs/' + args.model_name)
if not os.path.exists(logs_folder):
   os.mkdir(logs_folder)

model_ = args.model_func
if model_ == 'fc':
   model_func = get_fc_model
elif model_ == 'fc_no_bn':
   model_func = get_fc_no_bn_model
elif model_ == 'fc_no_bn_dropout':
   model_func = get_fc_no_bn_dropout_model
elif model_ == 'fc_small':
   model_func = get_fc_small_model
elif model_ == 'fc_small_no_bn':
   model_func = get_fc_no_bn_small_model
elif model_ == 'pointconv':
   model_func = get_pointconv_model
elif model_ == 'pointconv_deep':
   model_func = get_pointconv_deep_model
elif model_ == 'pointconv_deep_bn':
   model_func = get_pointconv_deep_bn_model   
    
# Run!
if not args.voxelize:
   run(get_model=model_func,
       train_path=args.train_path,
       validation_path=args.validation_path,
       pc_h5_file=args.pc_h5_file,
       model_path=model_folder,
       logs_path=logs_folder,
       batch_size=args.batch_size,
       epoch_start=args.epoch_start,
       epochs=args.epochs,
       learning_rate=args.learning_rate,
       optimizer=args.optimizer,
       train=args.training,
       warm_start=args.warm_start,
       alpha=args.alpha,
       loss_function=args.loss_function)
else:
   extract_voxel(model_func, model_path=model_folder, loss_function=args.loss_function)
