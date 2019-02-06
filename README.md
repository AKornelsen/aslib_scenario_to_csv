# ASlib scenarios to CSV files, with a ranking target type

This repository contains a simple python script, which can be used to transform ASlib scenarios into CSV files. In the default configuration of the script, performance runtimes are transformed into rankings. In this way it easier to use the ASlib scenarios for the label ranking problem.


# HowTo transform ASlib scenarios to CSV files
There are different ways possible to make the contained code of this repository running. The next section shows one possibility.
## Setup the environment
First of all we assume that an [Anaconda][1] distribution is installed on your OS.
Then, creating a conda environment is the first step. This step is optional but convenient in order to avoid an incorrect configuration.

```Shell
$ conda create -n kebi_env python=3.6 anaconda
```
Then activate the newly created conda environment to make it work in the console.
```Shell
$ source activate kebi_env
```

## Setup the project
The environment is ready and the next step is to setup the project with the following commands.
```Shell
$ git clone https://github.com/AKornelsen/aslib_scenario_to_csv.git
$ cd aslib_scenarios_to_csv
$ pip install -r requirements.txt
```

Download the scenarios into a new folder ```aslib_scenarios``, for example with the following commands.
```Shell
$ curl -LOk https://github.com/coseal/aslib_data/archive/aslib-v4.0.zip
$ unzip aslib-v4.0.zip -d aslib_scenarios
$ rm aslib-v4.0.zip
```

Now it should be possible to transform the scenarios by running the aslib_to_csv.py script. The scenarios are transformed in the default case to plain CSV files with a ranking target type. The CSV files can be customized to some extent by passing other parameters.

The following command is an example for how to calling the script.
```Shell
$ python aslib_to_csv.py --output_format='kebi'
```

Possible parameters and the description can be shown with the following command.
```Shell
$ python aslib_to_csv.py -help

usage: aslib_to_csv.py [-h] [--aslib_scenarios_folder ASLIB_SCENARIOS_FOLDER]
                       [--csv_output_folder CSV_OUTPUT_FOLDER]
                       [--rank_assignment_method_for_tied_ranks RANK_ASSIGNMENT_METHOD_FOR_TIED_RANKS]
                       [--replacement_string_null_feature_values REPLACEMENT_STRING_NULL_FEATURE_VALUES]
                       [--output_format OUTPUT_FORMAT] [--separator SEPARATOR]

The following arguments can be used for transforming ASlib scenarios to KEBI
formatted, as well as plain formatted CSV files.

optional arguments:
  -h, --help            show this help message and exit
  --aslib_scenarios_folder ASLIB_SCENARIOS_FOLDER
                        Provide the folder name containing the ASlib scenarios
                        relative to the called python program.
  --csv_output_folder CSV_OUTPUT_FOLDER
                        Provide the output folder for the created CSV files.
  --rank_assignment_method_for_tied_ranks RANK_ASSIGNMENT_METHOD_FOR_TIED_RANKS
                        This parameter defines which method is used to
                        transform performance values to rankings, possible
                        ranking methods are: 'average', 'min', 'max', 'dense',
                        'ordinal', 'no_ranking'
  --replacement_string_null_feature_values REPLACEMENT_STRING_NULL_FEATURE_VALUES
                        This string is used to replace feature values, which
                        are equals null.
  --output_format OUTPUT_FORMAT
                        This parameter is used to specify the different CSV
                        output formats. Possible output formats are 'kebi',
                        'kebi_names', 'plain': 'kebi': is formatted in the
                        same way as the KEBI CSV files., 'kebi_names': is like
                        the kebi output_format but with the feature and
                        algorithm names in the header, 'plain': a simple CSV
                        output formatted file with the feature and algorithm
                        names without the value type line.
  --separator SEPARATOR
                        This character is used for the CSV separator.


```

[1] https://www.anaconda.com