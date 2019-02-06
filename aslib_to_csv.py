import os
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata as rankdata1d
from aslib_scenario.aslib_scenario import ASlibScenario


class AsLibToKebiTransformer:
    PREFIX_FEATURE = 'F_'
    PREFIX_ALGORITHM = 'A_'
    DOUBLE_STRING = 'DOUBLE'
    NUMERIC_STRING = 'NUMERIC'

    def __init__(self,
                 root_folder_aslib_scenarios,
                 output_folder,
                 separator='\t',
                 output_format='kebi_names',
                 rank_assignment_method_for_tied_ranks='average',
                 replacement_string_null_feature_values='NULL'):

        self.absolute_path_root_folder_aslib_scenarios = os.path.join(os.getcwd(), root_folder_aslib_scenarios)
        self.absolute_path_output_folder = os.path.join(os.getcwd(), output_folder)
        self.supported_output_formats = ['kebi', 'kebi_names', 'plain']
        self.output_format = output_format
        self.separator = separator
        self.supported_rank_assignment_methods_for_tied_ranks = ['average', 'min', 'max', 'dense', 'ordinal', 'no_ranking']
        self.rank_assignment_method_for_tied_ranks = rank_assignment_method_for_tied_ranks
        self.replacement_string_null_feature_values = replacement_string_null_feature_values

    def transform_all_scenarios_to_kebi_format(self):
        self._check_params()

        scenario_folder_paths = self._get_scenario_folder_paths(self.absolute_path_root_folder_aslib_scenarios)
        for scenario_folder_path in scenario_folder_paths:
            scenario = self._transform_aslib_scenario_to_kebi_format(scenario_folder_path)
            print("ASlib scenario " + scenario.scenario + " is transformed to a " + self.output_format + " formatted CSV file.")

    def _transform_aslib_scenario_to_kebi_format(self, scenario_folder_path):

        # read scenario
        scenario = ASlibScenario()
        scenario.logger.disabled = True
        scenario.read_scenario(dn=str(scenario_folder_path))

        # prepare performance data and ranking data in XY_concationation DataFrame
        X = scenario.feature_data
        Y = self._performances_to_rankings(scenario)
        X, Y = self._adapt_column_names_according_to_the_output_format(X, Y)
        XY_concatination = pd.concat([X, Y], axis=1, join_axes=[X.index])

        # Save in CSV file
        output_file_path = os.path.join(str(self.absolute_path_output_folder), scenario.scenario + ".csv")
        XY_concatination.to_csv(output_file_path, sep=self.separator, encoding='UTF-8', index=False, float_format='%g', na_rep=self.replacement_string_null_feature_values)

        # post step: add column types and empty line according to KEBI format to exported csv file
        self._add_value_type_column_name_line_in_kebi_formatted_csv(output_file_path, X.columns, Y.columns)
        return scenario

    def _add_value_type_column_name_line_in_kebi_formatted_csv(self, output_file_path, feature_column_names, ranking_column_names):
        if self.output_format in ["kebi", "kebi_names"]:
            feature_value_types_column_name_line = [self.DOUBLE_STRING] * len(feature_column_names)
            algorithm_value_types_column_name_line = [self.NUMERIC_STRING] * len(ranking_column_names)
            value_types_column_name_line = feature_value_types_column_name_line + algorithm_value_types_column_name_line

            with open(output_file_path, "r") as in_file:
                buf = in_file.readlines()

            with open(output_file_path, "w") as out_file:
                line_number = 1
                for line in buf:
                    if line_number == 1:
                        line = line + self.separator.join(value_types_column_name_line) + "\n\n"
                    out_file.write(line)
                    line_number += 1

    def _adapt_column_names_according_to_the_output_format(self, X, Y):
        if self.output_format == "kebi":
            X.columns = ["A" + str(number) for number in list(range(1, len(X.columns) + 1))]
            Y.columns = ['{:02d}'.format(number) for number in list(range(1, len(Y.columns) + 1))]
        elif self.output_format == "kebi_names":
            x_plain_kebi_column_names = ["A" + str(number) for number in list(range(1, len(X.columns) + 1))]
            y_plain_kebi_column_names = ['{:02d}'.format(number) for number in list(range(1, len(Y.columns) + 1))]
            X.columns = [plain_kebi_column_name + "_" + str(column_name) for plain_kebi_column_name, column_name in zip(x_plain_kebi_column_names, X.columns)]
            Y.columns = [plain_kebi_column_name + "_" + str(column_name) for plain_kebi_column_name, column_name in zip(y_plain_kebi_column_names, Y.columns)]
        elif self.output_format == "plain":
            X.add_prefix(self.PREFIX_FEATURE)
            Y.add_prefix(self.PREFIX_ALGORITHM)
        return X, Y

    def _performances_to_rankings(self, scenario: ASlibScenario):
        # The performance data is changed in the read_scenario method in the ASlibScenario class.
        if scenario.performance_type[0] == "solution_quality" and scenario.maximize[0]:
            scenario.performance_data *= -1

        Y = scenario.performance_data
        if self.rank_assignment_method_for_tied_ranks is not "no_ranking":
            ranking_order = "desc" if scenario.maximize[0] else "asc"
            Y = self._rankdata(Y, order=ranking_order, is_2d=True, method=self.rank_assignment_method_for_tied_ranks)
            return pd.DataFrame(data=Y, index=scenario.performance_data.index, columns=scenario.performance_data.columns)
        return Y

    def _get_scenario_folder_paths(self, root_path_aslib_scearios):
        path = Path(root_path_aslib_scearios)

        if not path.is_dir():
            raise Exception("Folder path is not existing, folder path: %s" % root_path_aslib_scearios)
        scenario_folder_paths = []
        for scenario_folder_path in path.iterdir():
            if not scenario_folder_path.is_dir():
                continue
            scenario_folder_paths.append(scenario_folder_path)

        return scenario_folder_paths

    def _check_params(self):
        if not Path(self.absolute_path_root_folder_aslib_scenarios).exists():
            raise Exception("Folder path of ASlib scenarios couldn't be found, ASlib scenario path: " + self.absolute_path_root_folder_aslib_scenarios)
        output_folder = Path(self.absolute_path_output_folder)
        output_folder.mkdir(exist_ok=True)
        if not output_folder.exists():
            raise Exception("Output folder couldn't be created, CSV output folder path: " + self.absolute_path_output_folder)
        if self.output_format not in self.supported_output_formats:
            raise Exception("Output format is not supported, output format is: " + self.output_format + ", supported output formats: " + self.supported_output_formats)
        if self.separator != '\t' and len(self.separator) != 1:
            raise ValueError("The separator value should be one char, specified separator: " + self.separator)
        if self.rank_assignment_method_for_tied_ranks not in self.supported_rank_assignment_methods_for_tied_ranks:
            raise ValueError("Unsupported rank assignment method for tied ranking.")

    def _rankdata(self, y, order='asc', is_2d=True, method='ordinal'):
        if is_2d:
            if order is 'asc':
                return np.apply_along_axis(rankdata1d, 1, y, method=method)
            if order is 'desc':
                return np.apply_along_axis(self._rankdata, 1, y, order='desc', is_2d=False, method=method)
        if order is 'asc':
            return rankdata1d(y, method=method)
        if order is 'desc':
            return len(y) - rankdata1d(y, method=method) + 1
        raise ValueError("_dankdata method is not used correctly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='The following arguments can be used for transforming ASlib scenarios to CSV files, It is also possible to transform the ASlib scenarios into KEBI formatted CSV files.')
    parser.add_argument('--aslib_scenarios_folder', default='aslib_scenarios', type=str,
                        help='Provide the folder name containing the ASlib scenarios relative to the called python program.')
    parser.add_argument('--csv_output_folder', default='csv_output', type=str, help="Provide the output folder for the created CSV files.")
    parser.add_argument('--rank_assignment_method_for_tied_ranks', default='average', type=str,
                        help="This parameter defines which method is used to transform performance values to rankings, possible ranking methods are: "
                             + "'average', 'min', 'max', 'dense', 'ordinal', 'no_ranking'")
    parser.add_argument('--replacement_string_null_feature_values', default='NULL', type=str, help="This string is used to replace feature values, which are equals null.")
    parser.add_argument('--output_format', default='plain', type=str, help="This parameter is used to specify the different CSV output formats. Possible output formats are " +
                                                                           "'kebi', 'kebi_names', 'plain': " +
                                                                           "'kebi': is formatted in the same way as the KEBI CSV files., " +
                                                                           "'kebi_names': is like the kebi output_format but with the feature and algorithm names in the header, " +
                                                                           "'plain': a simple CSV output formatted file with the feature and algorithm names without the value type line.")
    parser.add_argument('--separator', default='\t', type=str, help="This character is used for the CSV separator.")

    args = parser.parse_args()
    parsed_aslib_scenarios_folder = args.aslib_scenarios_folder
    parsed_output_folder = args.csv_output_folder
    parsed_rank_assignment_method_for_tied_ranks = args.rank_assignment_method_for_tied_ranks
    parsed_replacement_string_null_feature_values = args.replacement_string_null_feature_values
    parsed_output_format = args.output_format
    parsed_separator = args.separator

    transformer = AsLibToKebiTransformer(parsed_aslib_scenarios_folder,
                                         parsed_output_folder,
                                         rank_assignment_method_for_tied_ranks=parsed_rank_assignment_method_for_tied_ranks,
                                         replacement_string_null_feature_values=parsed_replacement_string_null_feature_values,
                                         output_format=parsed_output_format,
                                         separator=parsed_separator)
    transformer.transform_all_scenarios_to_kebi_format()
