from .qrl import (
    monte_carlo_code,
    td_code,
    complete_policy_iteration_code,
    complete_value_iteration_code,
    tensor_operations_code,
    perceptron_operations_code,
    perceptron_manual_code,
    ADALINE_complete_code,
    MLP_complete_code,
    MLP_titanic_houses_code,
    CNN_og_code,
    CNN_modified_code,
    CNN_filters_code,

)

from .qsp import (
    mfcc_manual_vs_auto_code,
    analysis_formants_harmonics_code,
    generate_consonants_code,
    quiz_code,
    lab2_code,
    oel1_code,
    mfcc_from_scratch_code,
    mfcc_feature_extraction_code,
    mfcc_file_features_code,


)

from .utils import display_snippet, save_snippet

__all__ = [
    "monte_carlo_code",
    "td_code",
    "complete_policy_iteration_code",
    "complete_value_iteration_code",
    "display_snippet",
    "save_snippet",
    "tensor_operations_code",
    "perceptron_operations_code",
    "perceptron_manual_code",
    "ADALINE_complete_code",
    "MLP_complete_code",
    "MLP_titanic_houses_code",
    "CNN_og_code",
    "CNN_modified_code",
    "CNN_filters_code",
    "mfcc_manual_vs_auto_code",
    "analysis_formants_harmonics_code",
    "generate_consonants_code",
    "quiz_code",
    "lab2_code",
    "oel1_code",
    "mfcc_from_scratch_code",
    "mfcc_feature_extraction_code",
    "mfcc_file_features_code",

]
