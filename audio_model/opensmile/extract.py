import os
import pandas as pd
import pdb
import numpy as np

# Load csv files in dataframes
train_df = pd.read_csv('omg_TrainVideos.csv')
valid_df = pd.read_csv('omg_ValidationVideos.csv')

# Remove ".mp4" in the name of utterance
train_df['utterance'] = train_df['utterance'].map(lambda x: str(x)[:-4])
valid_df['utterance'] = valid_df['utterance'].map(lambda x: str(x)[:-4])

# Construct filenames of wav files
train_utts_filenames = train_df['video'] + '#' + train_df['utterance'] + '.wav'
valid_utts_filenames = valid_df['video'] + '#' + valid_df['utterance'] + '.wav'


# This function iterate through wav files, call opensmile that output a csv containing the features corresponding to the conf_path
def compute_opensmile_features(data_path, files, conf_path, feature_path):
    for id_sentence in files:

        wave_path = os.path.join(data_path, id_sentence)

        if (not os.path.exists(feature_path)):
            os.makedirs(feature_path)

        features_file = os.path.join(feature_path, id_sentence[:-4] + '.csv')
        # pdb.set_trace()

        if not os.path.isfile(features_file):  # if the file doesn't exist, compute features with opensmile
            opensmile_binary_path = '/home/jb/Downloads/opensmile-2.3.0/bin/linux_x64_standalone_static/'
            command = opensmile_binary_path + "SMILExtract -I {input_file} -C {conf_file} --csvoutput {output_file}".format(
                input_file=wave_path,
                conf_file=conf_path,
                output_file=features_file)
            os.system(command)


import sys

conf_name = 'IS13_ComParE'

data_path = './data/'

conf_path = '/home/jb/Downloads/opensmile-2.3.0/config/' + conf_name + '.conf'

feature_path = os.path.join('./features/opensmile_features/', conf_name)

# compute feature and store csv output in feature_path
compute_opensmile_features(data_path, train_utts_filenames, conf_path, feature_path)
compute_opensmile_features(data_path, valid_utts_filenames, conf_path, feature_path)

# Construct filenames of csv files
train_utts_csv = train_df['video'] + '#' + train_df['utterance'] + '.csv'
valid_utts_csv = valid_df['video'] + '#' + valid_df['utterance'] + '.csv'

train_csv_paths = feature_path + '/' + train_utts_csv
valid_csv_paths = feature_path + '/' + valid_utts_csv


def load_features(paths):
    dfs = []
    for path in paths:
        # pdb.set_trace()
        try:
            df = pd.read_csv(path, sep=';')

            # If opensmile didn't extract anything, add a row of nans
            if df.shape[0] == 0:
                df.loc[0] = np.nan
            dfs.append(df.iloc[0].iloc[2:])  # discard two first useless elements (name and frametime)
        except:
            pdb.set_trace()
    feat_df = pd.concat(dfs, axis=1).transpose()

    # mean_features=[i for i in feat_df.columns.tolist() if i.endswith('mean')]
    # data_select_mean_features=data_select[mean_features]
    feat_df.index = paths.index
    return feat_df


feat_train_df = load_features(train_csv_paths)
np.save(os.path.join(feature_path, 'train.npy'), feat_train_df.as_matrix())

feat_valid_df = load_features(valid_csv_paths)
np.save(os.path.join(feature_path, 'valid.npy'), feat_valid_df.as_matrix())

# pdb.set_trace()
