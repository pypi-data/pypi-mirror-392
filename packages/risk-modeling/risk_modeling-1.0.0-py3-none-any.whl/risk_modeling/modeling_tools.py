
def calculate_numeric_psi(df_expected, df_actual, features, bin_method='equal_interval', bins=10,
                          min_pct=1e-6, special_codes=None):
    """
    Calculates the PSI (Population Stability Index) for numerical features, supporting separate binning for missing values and special codes.

    Parameters:
    df_expected: pandas.DataFrame - Expected distribution dataset (baseline)
    df_actual: pandas.DataFrame - Actual distribution dataset (monitoring period)
    features: list - List of features to calculate
    bin_method: str - Binning method ('equal_interval' for equal-width, 'equal_volume' for equal-frequency)
    bins: int - Number of bins
    min_pct: float - Minimum percentage (to avoid division by zero errors)
    special_codes: list - Special code values requiring independent binning

    Returns:
    total_psi_df: pandas.DataFrame - Total PSI values for each feature
    detail_df: pandas.DataFrame - Detailed bin-level PSI data per feature
    """
    import pandas as pd
    import numpy as np

    total_psi = []
    detail_dfs = {}

    # If special_codes is not provided, initialize as empty list
    if special_codes is None:
        special_codes = []

    for feature in features:
        # Extract feature data
        exp_data = df_expected[feature].copy()
        act_data = df_actual[feature].copy()

        # Split data into three parts: missing values, special codes, and normal values
        # Missing values (NaN)
        exp_missing = exp_data.isna()
        act_missing = act_data.isna()

        # Special codes
        exp_special = exp_data.isin(special_codes)
        act_special = act_data.isin(special_codes)

        # Normal values (non-missing, non-special codes)
        exp_normal = ~exp_missing & ~exp_special
        act_normal = ~act_missing & ~act_special

        # Calculate counts for each category
        exp_counts = {
            'missing': exp_missing.sum(),
            'special': exp_special.sum(),
            'normal': exp_normal.sum()
        }
        act_counts = {
            'missing': act_missing.sum(),
            'special': act_special.sum(),
            'normal': act_normal.sum()
        }
        exp_total = len(exp_data)
        act_total = len(act_data)

        # Process normal values portion (non-missing, non-special code)
        exp_normal_data = exp_data[exp_normal]
        act_normal_data = act_data[act_normal]

        # Initialize bin counters
        exp_bin_counts = pd.Series(dtype=float)
        act_bin_counts = pd.Series(dtype=float)

        # Process normal values portion
        if exp_normal.sum() > 0:
            # Obtain range of expected data
            exp_min = exp_normal_data.min()
            exp_max = exp_normal_data.max()

            # Handle out-of-range values in actual data
            # Values below the minimum value of the expected data
            act_below_min = act_normal_data[act_normal_data < exp_min]
            # Values above the maximum value of the expected data
            act_above_max = act_normal_data[act_normal_data > exp_max]
            # Values within the range of the expected data
            act_in_range = act_normal_data[(act_normal_data >= exp_min) & (act_normal_data <= exp_max)]

            # No special treatment for expected data
            exp_in_range = exp_normal_data.copy()

            # Create three special bin labels
            below_min_label = f"< {exp_min}"
            above_max_label = f"> {exp_max}"
            range_label = f"[{exp_min}, {exp_max}]"

            # Calculate count of actual data which exceeds the range of the expected data
            act_below_min_count = len(act_below_min)
            act_above_max_count = len(act_above_max)

            # Bin data within the range of the expected data
            if len(exp_in_range) > 0 and len(act_in_range) > 0:
                if bin_method == 'equal_interval':
                    # Equal-interval binning
                    bin_edges = np.linspace(exp_normal_data.min(), exp_normal_data.max(), bins + 1)
                elif bin_method == 'equal_volume':
                    # Equal-volume binning
                    bin_edges = np.percentile(exp_normal_data, np.linspace(0, 100, bins + 1))
                else:
                    raise ValueError("bin_method 必须是 'equal_interval', 'equal_volume'")

                # Ensure boundary uniqueness
                bin_edges = np.unique(bin_edges)
                if len(bin_edges) < 2:
                    bin_edges = np.array([exp_min, exp_max])

                # Bin for the within-range data
                exp_cut = pd.cut(exp_in_range, bins=bin_edges, include_lowest=True)
                act_cut = pd.cut(act_in_range, bins=bin_edges, include_lowest=True)

                # Obtain bin counts (keep the original order)
                exp_bin_counts_range = exp_cut.value_counts()
                act_bin_counts_range  = act_cut.value_counts()

                # Sort by the left boundary (ascending) of the bins
                sorted_index = sorted(
                    exp_bin_counts_range.index,
                    key=lambda x: x.left if pd.notna(x.left) else -np.inf
                )

                # Create sorted bin labels
                sorted_labels = [f"{str(interval)}" for interval in sorted_index]

                # Reindex using sorted labels
                exp_bin_counts_range = exp_bin_counts_range.reindex(sorted_index).set_axis(sorted_labels)
                act_bin_counts_range = act_bin_counts_range.reindex(sorted_index).set_axis(sorted_labels)

                # Add to the main Series
                exp_bin_counts = exp_bin_counts_range
                act_bin_counts = act_bin_counts_range
                sorted_bins = sorted_labels

            # Add the bins for the out-of-range data
            if act_below_min_count > 0:
                exp_bin_counts[below_min_label] = 0
                act_bin_counts[below_min_label] = act_below_min_count

            if act_above_max_count > 0:
                exp_bin_counts[above_max_label] = 0
                act_bin_counts[above_max_label] = act_above_max_count

            # If no within-range data exists, add range label placeholder
            if len(exp_bin_counts) == 0:
                exp_bin_counts[range_label] = exp_counts['normal']
                act_bin_counts[range_label] = act_counts['normal'] - act_below_min_count - act_above_max_count

            # Add the bins for the out-of-range data to the sorted bin list (positioned at start/end)
            sorted_bins = [below_min_label] + sorted_bins + [above_max_label]

        # Add bins for the special codes (one bin per unique value)
        special_labels = []
        for code in special_codes:
            exp_code_count = (exp_data == code).sum()
            act_code_count = (act_data == code).sum()

            if exp_code_count > 0 or act_code_count > 0:
                exp_bin_counts[f"Special: {code}"] = exp_code_count
                act_bin_counts[f"Special: {code}"] = act_code_count
                special_labels.append(f"Special: {code}")

        # Add the bin for the missing value
        missing_label="Missing"
        if exp_counts['missing'] > 0 or act_counts['missing'] > 0:
            exp_bin_counts["Missing"] = exp_counts['missing']
            act_bin_counts["Missing"] = act_counts['missing']

        # Ensure at least one bin exists
        if len(exp_bin_counts) == 0:
            exp_bin_counts = pd.Series([exp_total], index=["All"])
            act_bin_counts = pd.Series([act_total], index=["All"])

        # Create the order for all bins: normal bins (sorted) + special codes + missing value
        all_bins = sorted_bins + special_labels
        if exp_counts['missing'] > 0 or act_counts['missing'] > 0:
            all_bins.append(missing_label)

        # Ensure the bin ordering
        exp_bin_counts = exp_bin_counts.reindex(all_bins, fill_value=0)
        act_bin_counts = act_bin_counts.reindex(all_bins, fill_value=0)

        # Calculate the percentage
        exp_pct = exp_bin_counts / exp_total
        act_pct = act_bin_counts / act_total

        # Ensure all bins exist
        all_bins = exp_pct.index.union(act_pct.index)
        exp_pct = exp_pct.reindex(all_bins, fill_value=min_pct)
        act_pct = act_pct.reindex(all_bins, fill_value=min_pct)

        # Avoid zero-value issues
        exp_pct = exp_pct.clip(lower=min_pct)
        act_pct = act_pct.clip(lower=min_pct)

        # Calculate PSI components and total PSI
        psi_components = (act_pct - exp_pct) * np.log(act_pct / exp_pct)
        total_psi_value = psi_components.sum()

        # Store the results
        total_psi.append({'feature': feature, 'PSI': total_psi_value})

        # Create detailed psi table
        detail_df = pd.DataFrame({
            'feature':feature,
            'bin_range': exp_pct.index,
            'expected_pct': exp_pct.values,
            'actual_pct': act_pct.values,
            'psi_component': psi_components.values
        })
        detail_dfs[feature] = detail_df

    detail_df_tmp = []
    for feature_name, df in detail_dfs.items():
        detail_df_tmp.append(df)

    detail_df_fnl = pd.concat(detail_df_tmp, ignore_index=True)

    # Remove the empty bins
    detail_df_fnl_clean=detail_df_fnl[~((detail_df_fnl['expected_pct']==min_pct)&(detail_df_fnl['actual_pct']==min_pct)&(detail_df_fnl['psi_component']==0))].reset_index(drop=True)

    total_psi_df = pd.DataFrame(total_psi)

    return total_psi_df, detail_df_fnl_clean

def calculate_categorical_psi(df_expected, df_actual, features, min_pct_merge=0.01, min_pct=1e-6):
    """
    Calculate PSI (Population Stability Index) for categorical features, supporting separate binning for missing values and category merging.

    Parameters:
    df_expected: pandas.DataFrame - Expected distribution dataset (baseline)
    df_actual: pandas.DataFrame - Actual distribution dataset (monitoring period)
    features: list - List of features to calculate
    min_pct_merge: float - Category merging threshold (categories below this percentage will be merged)
    min_pct: float - Minimum percentage (to avoid division by zero errors)

    Returns:
    total_psi_df: pandas.DataFrame - Total PSI values for each feature
    detail_df: pandas.DataFrame - Detailed bin-level PSI data per feature
    """
    import pandas as pd
    import numpy as np

    total_psi_list = []
    detail_dfs = []

    for feature in features:
        # Handle missing values
        exp_data = df_expected[feature].copy().fillna('Missing')
        act_data = df_actual[feature].copy().fillna('Missing')

        # 1. Process df_expected
        # Calculate category distribution
        exp_counts = exp_data.value_counts()
        exp_total = len(exp_data)
        exp_pct = exp_counts / exp_total

        # Merge small categories
        small_categories = exp_pct[exp_pct < min_pct_merge].index
        if not small_categories.empty:
            exp_data_replaced = exp_data.replace(dict.fromkeys(small_categories, 'Other'))
            exp_data_replaced[exp_data == 'Missing'] = 'Missing'
        else:
            exp_data_replaced = exp_data.copy()

        # Recalculate distribution of df_expected
        exp_counts_final = exp_data_replaced.value_counts()
        exp_pct_final = exp_counts_final / exp_total

        # 2. Process df_actual
        # Handle new categories not present in df_expected
        expected_categories = exp_counts_final.index.tolist()
        new_categories = set(act_data) - set(expected_categories)

        # Replace new categories with "New_Categories" while preserving merged the small categories
        if new_categories:
            act_data_replaced = act_data.replace(dict.fromkeys(new_categories, 'New_Categories'))
        else:
            act_data_replaced = act_data.copy()

        # Replace the merged small categories with "Other"
        if not small_categories.empty:
            act_data_replaced = act_data_replaced.replace(dict.fromkeys(small_categories, 'Other'))

        # Recalculate distribution of df_actual
        act_counts_final = act_data_replaced.value_counts()
        act_total = len(act_data)
        act_pct_final = act_counts_final / act_total

        # 3. Align the bins of categories
        all_categories = list(set(exp_pct_final.index.tolist() + act_pct_final.index.tolist()))

        # Ensure ordering
        category_order = sorted(all_categories, key=lambda x: (x != 'Missing', x != 'Other', x != 'New_Categories', x))

        # Reindex for alignment
        exp_pct_aligned = exp_pct_final.reindex(category_order, fill_value=0)
        act_pct_aligned = act_pct_final.reindex(category_order, fill_value=0)

        # Avoid division by zero
        exp_pct_aligned = exp_pct_aligned.clip(lower=min_pct)
        act_pct_aligned = act_pct_aligned.clip(lower=min_pct)

        # 4. Calculate PSI
        psi_components = (act_pct_aligned - exp_pct_aligned) * np.log(act_pct_aligned / exp_pct_aligned)
        total_psi = psi_components.sum()

        # Store the results
        total_psi_list.append({'feature': feature, 'PSI': total_psi})

        # Create data for detailed PSI
        detail_df_raw = pd.DataFrame({
            'feature': feature,
            'category': category_order,
            'expected_pct': exp_pct_aligned.values,
            'actual_pct': act_pct_aligned.values,
            'psi_component': psi_components.values
        })

        # Sort output by specified order
        category_priority = {
            'Other': 1,
            'New_Categories': 2,
            'Missing': 3
        }

        detail_df_raw['priority'] = detail_df_raw['category'].apply(
            lambda x: category_priority.get(x, 0)  # 普通类别优先级为0
        )

        detail_df = detail_df_raw.sort_values(
            by=['priority', 'category'],
            ascending=[True, True]
        ).drop(columns='priority')

        detail_dfs.append(detail_df)

    # Merge the results
    total_psi_df = pd.DataFrame(total_psi_list)
    detail_df_final = pd.concat(detail_dfs, ignore_index=True)

    return total_psi_df, detail_df_final

def calculate_numeric_iv(df, features, target, binning_method='equal_volume', n_bins=10, special_codes=[],min_pct=1e-10):
    """
    Calculate IV (Information Value) for numerical features,supporting separate binning for missing values and special codes.

    Parameters:
    df: pandas.DataFrame - Dataset to calculate IV
    features: list - List of features to calculate
    target: str - Name of the target/label variable column
    binning_method: str - Binning method ('equal_interval' for equal-width, 'equal_volume' for equal-frequency)
    n_bins: int - Number of bins
    special_codes: list - Special code values requiring independent binning
    min_pct : float - Minimum percentage (to avoid division by zero errors)

    Returns:
    iv_summary_df: pandas.DataFrame - Summary DataFrame(feature name, IV value)
    iv_detail_df: pandas.DataFrame - Detailed binned DataFrame (feature name, bin, statistics, etc.)
    """
    import pandas as pd
    import numpy as np

    iv_summary_list = []
    iv_detail_list = []

    for feat in features:
        # Create a copy to avoid modifying the original data
        data = df[[feat, target]].copy()

        data['_temp_group'] = ""

        # Deal with special values and missing values
        missing_mask = data[feat].isna()
        special_mask = data[feat].isin(special_codes)
        normal_mask = ~missing_mask & ~special_mask

        # Group missing values separately
        data.loc[missing_mask, '_temp_group'] = 'Missing'

        # Group special codes separately
        for code in special_codes:
            data.loc[data[feat] == code, '_temp_group'] = f'{code}'

        # Process normal values through binning
        normal_data = data[normal_mask].copy()

        if binning_method == 'equal_interval':
            normal_data.loc[:, '_temp_group'] = pd.cut(normal_data[feat], bins=n_bins, duplicates='drop')
        elif binning_method == 'equal_volume':
            normal_data.loc[:, '_temp_group'] = pd.qcut(normal_data[feat], q=n_bins, duplicates='drop')

        # Update the grouping information
        data.loc[normal_mask, '_temp_group'] = normal_data['_temp_group']

        # Calculate the statistics of groups
        grouped = data.groupby('_temp_group', observed=True).agg(
            total=(target, 'count'),
            bad=(target, 'sum'),
            good=(target, lambda x: x.count() - x.sum())
        ).reset_index()

        # Add bad rate
        grouped['bad_rate'] = grouped['bad'] / grouped['total']

        # Calculate the total good/bad sample counts
        total_good = grouped['good'].sum()
        total_bad = grouped['bad'].sum()

        def safe_woe(row):
            bad_ratio = row['bad'] / total_bad
            good_ratio = row['good'] / total_good

            if good_ratio==0:
                ratio = bad_ratio / (good_ratio + min_pct)
            else:
                ratio = bad_ratio / good_ratio

            if ratio==0:
                return np.log(ratio + min_pct)

            return np.log(ratio)

        # Calculate WOE and IV
        grouped['woe'] = grouped.apply(safe_woe, axis=1)
        grouped['iv_contribution'] = (
                (grouped['bad'] / total_bad - grouped['good'] / total_good) * grouped['woe']
        )

        # Summarize the results
        total_iv = grouped['iv_contribution'].sum()

        iv_summary_list.append({
            'feature': feat,
            'iv': total_iv
        })

        # Add details
        detail_df = grouped.rename(columns={'_temp_group': 'bin'})
        detail_df = detail_df[['bin', 'total', 'good', 'bad', 'bad_rate', 'woe', 'iv_contribution']]
        detail_df.insert(0, 'feature', feat)  # 添加特征名列
        iv_detail_list.append(detail_df)

    # Create the final output
    iv_summary_df = pd.DataFrame(iv_summary_list)
    iv_detail_df = pd.concat(iv_detail_list, ignore_index=True)

    return iv_summary_df, iv_detail_df

def calculate_categorical_iv(df, features, target, min_pct_merge=0.05, min_pct=1e-10):
    """
    Calculate IV (Information Value) for categorical features, supporting separate binning for missing values and category merging

    Parameters:
    df: pandas.DataFrame - Dataset to calculate IV
    features: list - List of features to calculate
    target: str - Name of the target/label variable column
    min_pct_merge: float - Category merging threshold (categories below this percentage will be merged)
    min_pct: float - Minimum percentage (to avoid division by zero errors)

    Returns:
    iv_summary_df: pandas.DataFrame - Summary DataFrame(feature name, IV value)
    iv_detail_df: pandas.DataFrame - Detailed binned DataFrame (feature name, bin, statistics, etc.)
    """
    import pandas as pd
    import numpy as np

    iv_summary_list = []
    iv_detail_list = []

    for feat in features:
        # Create a copy to avoid modifying the original data
        data = df[[feat, target]].copy()
        data['_temp_group'] = None

        # Handle missing values (group separately)
        missing_mask = data[feat].isna()
        data.loc[missing_mask, '_temp_group'] = 'Missing'

        # Process non-missing values
        non_missing_data = data[~missing_mask]

        # Calculate category frequencies
        category_counts = non_missing_data[feat].value_counts(normalize=True)

        # Identify small categories which require merging
        small_categories = category_counts[category_counts < min_pct_merge].index.tolist()

        def map_category(x):
            if x in small_categories:
                return 'Other'
            return str(x)

        # Apply grouping rules
        non_missing_data.loc[:, '_temp_group'] = non_missing_data[feat].apply(map_category)
        data.loc[~missing_mask, '_temp_group'] = non_missing_data['_temp_group']

        # Calculate statistics of groups
        grouped = data.groupby('_temp_group', observed=True).agg(
            total=(target, 'count'),
            bad=(target, 'sum'),
            good=(target, lambda x: x.count() - x.sum())
        ).reset_index()

        # Add bad/label rate
        grouped['bad_rate'] = grouped['bad'] / grouped['total']

        # Calculate the total good/bad sample counts
        total_good = grouped['good'].sum()
        total_bad = grouped['bad'].sum()

        # Calculate WOE and IV
        def safe_woe(row):
            bad_ratio = row['bad'] / total_bad
            good_ratio = row['good'] / total_good

            # Handle division-by-zero cases
            if good_ratio == 0:
                ratio = bad_ratio / (good_ratio + min_pct)
            else:
                ratio = bad_ratio / good_ratio

            # Avoid log(0)
            if ratio == 0:
                return np.log(ratio + min_pct)
            return np.log(ratio)

        grouped['woe'] = grouped.apply(safe_woe, axis=1)
        grouped['iv_contribution'] = (grouped['bad'] / total_bad - grouped['good'] / total_good) * grouped['woe']

        # Summarize IV values
        total_iv = grouped['iv_contribution'].sum()

        # Add feature name to the detailed IV
        grouped.insert(0, 'feature', feat)
        grouped = grouped.rename(columns={'_temp_group': 'bin'})

        custom_order = ['Missing', 'Other']
        current_categories = [c for c in grouped['bin'] if c not in custom_order]
        sorted_categories = sorted(current_categories) + ['Other'] + ['Missing']

        sorted_categories = [c for c in sorted_categories if c in grouped['bin'].values]
        grouped['bin'] = pd.Categorical(grouped['bin'], categories=sorted_categories, ordered=True)
        grouped = grouped.sort_values('bin')

        # Output
        detail_df = grouped[['feature', 'bin', 'total', 'good', 'bad', 'bad_rate', 'woe', 'iv_contribution']]

        # Store results
        iv_summary_list.append({'feature': feat, 'iv': total_iv})
        iv_detail_list.append(detail_df)

    # Create final output in pandas.DataFrame
    iv_summary_df = pd.DataFrame(iv_summary_list)
    iv_detail_df = pd.concat(iv_detail_list, ignore_index=True)

    return iv_summary_df, iv_detail_df

def proc_compare(df1, df2, features, keys, tolerance, output_file):
    """
    Compare feature values between two Pandas DataFrames

    Parameters:
    df1: pandas DataFrame - Dataset to compare
    df2: pandas DataFrame - Dataset to compare
    features: list - List of features to compare
    keys: list - List of primary key column names (can contain multiple keys, e.g., ID and timestamp)
    tolerance: float - Tolerance threshold for numerical feature comparisons
    output_file: str - Output filename (stores absolute difference values)

    Returns:
    None
    """
    import pandas as pd
    import numpy as np
    from collections import defaultdict

    results = []

    # Basic information
    n_df1, n_df2 = len(df1), len(df2)
    unique_keys_df1 = df1[keys].drop_duplicates().shape[0]
    unique_keys_df2 = df2[keys].drop_duplicates().shape[0]

    results.append("Number of records:")
    results.append(f"  DataFrame1: {n_df1}")
    results.append(f"  DataFrame2: {n_df2}")
    results.append("")

    results.append("Number of unique keys:")
    results.append(f"  DataFrame1: {unique_keys_df1}")
    results.append(f"  DataFrame2: {unique_keys_df2}")
    results.append("")

    # Data preparation
    # Merge datasets while preserving all records (even with non-unique keys)
    merged = pd.merge(df1, df2, on=keys, suffixes=('_df1', '_df2'), how='outer', indicator=True)

    # Separate keys
    common_keys = merged[merged['_merge'] == 'both']
    only_df1 = merged[merged['_merge'] == 'left_only']
    only_df2 = merged[merged['_merge'] == 'right_only']

    # Feature comparison
    diff_summary = {}
    feature_diffs = defaultdict(list)

    for feat in features:
        col1 = f"{feat}_df1"
        col2 = f"{feat}_df2"

        # Check the data types
        is_numeric = pd.api.types.is_numeric_dtype(df1[feat]) and \
                     pd.api.types.is_numeric_dtype(df2[feat])

        # Compare the numeric features
        if is_numeric:
            # Create the absolute difference column
            common_keys = common_keys.assign(__abs_diff=np.nan)

            # Handle missing values
            both_missing = common_keys[[col1, col2]].isna().all(axis=1)
            one_missing = common_keys[[col1, col2]].isna().sum(axis=1) == 1
            both_present = ~(both_missing | one_missing)

            # Calculate the absolute differences for non-missing values
            common_keys.loc[both_present, '__abs_diff'] = (
                    common_keys.loc[both_present, col1] - common_keys.loc[both_present, col2]
            ).abs()

            diff_mask = (common_keys['__abs_diff'] > tolerance) | one_missing

            diff_count = diff_mask.sum()
            max_diff = common_keys.loc[both_present, '__abs_diff'].max() if both_present.any() else np.nan

            if diff_count > 0:
                diff_summary[feat] = (diff_count, max_diff)
                # Sort by the absolute difference in descending order
                diff_records = common_keys[diff_mask].sort_values(by='__abs_diff', ascending=False).head(5)

                for _, row in diff_records.iterrows():
                    key_val = tuple(str(row[k]) for k in keys)
                    diff_value = row['__abs_diff'] if not pd.isna(row['__abs_diff']) else np.nan
                    feature_diffs[feat].append({
                        'keys': key_val,
                        'value_df1': row[col1],
                        'value_df2': row[col2],
                        'diff': diff_value
                    })

        # Compare the categorical features
        else:
            # Handle missing values
            both_missing = common_keys[[col1, col2]].isna().all(axis=1)
            one_missing = common_keys[[col1, col2]].isna().sum(axis=1) == 1
            value_diff = common_keys[col1] != common_keys[col2]

            diff_mask = (value_diff & ~both_missing) | one_missing
            diff_count = diff_mask.sum()

            if diff_count > 0:
                diff_summary[feat] = (diff_count, np.nan)
                diff_records = common_keys[diff_mask].head(5)

                for _, row in diff_records.iterrows():
                    key_val = tuple(str(row[k]) for k in keys)
                    feature_diffs[feat].append({
                        'keys': key_val,
                        'value_df1': row[col1],
                        'value_df2': row[col2],
                        'diff': np.nan
                    })

    # Output the results
    # Feature Comparison Summary
    results.append("Feature Comparison Summary:")
    if not diff_summary:
        results.append("  All features are identical")
    else:
        results.append("  {:<15} {:<15} {:<15}".format("Feature", "Number of records with different values", "Maximum Difference"))
        for feat, (diff_count, max_diff) in diff_summary.items():
            diff_str = f"{max_diff:.4f}" if not np.isnan(max_diff) else "N/A"
            results.append(f"  {feat:<15} {diff_count:<15} {diff_str}")
    results.append("")

    # Feature Comparison Details
    results.append("Feature Comparison Details:")
    if not feature_diffs:
        results.append("  No records with different values")
    else:
        for feat, diffs in feature_diffs.items():
            results.append(f"  Feature: {feat}")
            # 计算最大键长度用于对齐
            max_key_len = max(len(", ".join(diff['keys'])) for diff in diffs) if diffs else 30
            key_width = max(30, max_key_len)
            fmt_str = f"  {{:<{key_width}}} {{:<15}} {{:<15}} {{:<10}}"

            results.append(fmt_str.format("Keys", "Value from df1", "Value from df2", "Difference"))

            for diff in diffs:
                keys_str = ", ".join(diff['keys'])
                diff_val = f"{diff['diff']:.4f}" if not np.isnan(diff['diff']) else "N/A"

                # Handle the display of the missing values
                val1 = str(diff['value_df1']) if not pd.isna(diff['value_df1']) else "NaN"
                val2 = str(diff['value_df2']) if not pd.isna(diff['value_df2']) else "NaN"

                results.append(fmt_str.format(keys_str, val1, val2, diff_val))
            results.append("")

    # Keys difference
    if not only_df1.empty or not only_df2.empty:
        results.append("The difference of keys:")
        results.append(f"  Number of keys only in df1: {len(only_df1)}")
        results.append(f"  Number of keys only in df2: {len(only_df2)}")
        results.append("")

    # Write the records to the file
    with open(output_file, 'w') as f:
        f.write("\n".join(results))

def compute_numeric_bivar(datasets,features,target,bin_method,n_bins,output_plot,figsize=(15, 10)):
    """
    Compute bivariate analysis (BIVAR) statistics for multiple datasets and features

    Parameters:
    datasets: dict - Dictionary of datasets {dataset_name: dataframe}
    features: list - List of numeric features to calculate
    target: str - Name of the target/label variable column
    bin_method: str - Binning method ('equal_interval' for equal-width, 'equal_volume' for equal-frequency)
    n_bins: int - Number of bins (excluding missing value bin)
    output_plot: bool - Whether to generate visualizations
    figsize: tuple - Figure size

    Returns:
    Bivar result: pandas.DataFrame - DataFrame with columns: ['dataset', 'feature', 'bin', 'count', 'good', 'bad', 'bad_rate']
    Figures: figures
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    # 1. Initialize results storage
    all_results = []

    # 2. Validate datasets and features
    for dname, df in datasets.items():
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Dataset '{dname}' missing features: {missing_features}")
        if target not in df.columns:
            raise ValueError(f"Dataset '{dname}' missing target column")

    # 3. Core calculation function
    def _calc_bivar(df: pd.DataFrame, feature: str, dname: str) -> pd.DataFrame:
        # Handle missing values
        is_na = df[feature].isna()
        df_clean = df[~is_na].copy()
        na_df = df[is_na]

        # Binning logic
        if bin_method == 'equal_interval':
            df_clean['bin'], bins = pd.cut(
                df_clean[feature], bins=n_bins,
                retbins=True, duplicates='drop'
            )
        elif bin_method == 'equal_volume':
            df_clean['bin'], bins = pd.qcut(
                df_clean[feature], q=n_bins,
                retbins=True, duplicates='drop'
            )

        # Format bin labels to 3 decimal places
        df_clean['bin'] = df_clean['bin'].apply(
            lambda x: f"({x.left:.3f}, {x.right:.3f}]"
        )

        # Calculate bin statistics
        binned = (
            df_clean.groupby('bin', observed=True)
            .agg(
                count=(target, 'size'),
                good=(target, lambda x: (x == 0).sum()),
                bad=(target, lambda x: (x == 1).sum())
            )
            .reset_index()
        )
        binned['bad_rate'] = binned['bad'] / binned['count']

        # Add missing value bin
        if not na_df.empty:
            na_stats = pd.DataFrame({
                'bin': ['Missing'],
                'count': [len(na_df)],
                'good': [(na_df[target] == 0).sum()],
                'bad': [(na_df[target] == 1).sum()]
            })
            na_stats['bad_rate'] = na_stats['bad'] / na_stats['count']
            binned = pd.concat([binned, na_stats], ignore_index=True)


        # Add dataset and feature identifiers
        binned.insert(0, 'feature', feature)
        binned.insert(0, 'dataset', dname)

        return binned

    # 4. Execute calculations
    for dname, df in datasets.items():
        for feature in features:
            result = _calc_bivar(df, feature, dname)
            all_results.append(result)

    # Combine all results into single DataFrame
    combined_results = pd.concat(all_results, ignore_index=True)

    # 5. Visualization
    if output_plot and len(features) > 0 and len(datasets) > 0:
        n_datasets = len(datasets)
        n_features = len(features)

        fig, axes = plt.subplots(
            n_features, n_datasets,
            figsize=(figsize[0], figsize[1] * n_features / max(n_datasets, 1)),
            squeeze=False
        )

        for j, dname in enumerate(datasets):
            for i, feature in enumerate(features):
                ax = axes[i, j]
                data = combined_results[
                    (combined_results['dataset'] == dname) &
                    (combined_results['feature'] == feature)
                    ]

                if len(data) == 0:
                    continue

                # Create positions for bars
                positions = np.arange(len(data))
                bar_width = 0.7

                # Bar chart for sample counts
                bars = ax.bar(
                    positions, data['count'],
                    width=bar_width,
                    color='skyblue',
                    alpha=0.7,
                    label='Sample Count'
                )

                # Calculate bad rate positions - FIXED
                # Convert to numpy array to avoid indexing issues
                max_count = data['count'].max()
                bad_rates = data['bad_rate'].to_numpy()

                # Calculate line points at the top center of each bar
                line_y = bad_rates * max_count * 1.1

                # Plot line connecting the points
                ax.plot(
                    positions, line_y,
                    color='red',
                    marker='o',
                    markersize=8,
                    label='Bad Rate'
                )

                # Add bad rate values as text above points - FIXED
                for pos, br in zip(positions, bad_rates):
                    text_y = br * max_count * 1.15  # Position above the point
                    ax.text(
                        pos, text_y,
                        f'{br:.3f}',
                        ha='center',
                        va='bottom',
                        color='red',
                        fontsize=9
                    )

                # Formatting
                ax.set_title(f"{dname} - {feature}", fontsize=12)
                ax.set_ylabel('Sample Count', color='skyblue')
                ax.tick_params(axis='y', labelcolor='skyblue')

                # Set x-ticks to avoid warning
                ax.set_xticks(positions)
                ax.set_xticklabels(
                    data['bin'].tolist(),
                    rotation=45,
                    ha='right',
                    fontsize=9
                )

                # Create second y-axis for bad rate
                ax2 = ax.twinx()
                ax2.set_ylim(0, bad_rates.max() * 1.3)
                ax2.set_ylabel('Bad Rate', color='red')
                ax2.tick_params(axis='y', labelcolor='red')

        plt.tight_layout()
        plt.show()

    return combined_results

def compute_categorical_bivar(datasets, features, target, output_plot, figsize=(15, 10)):
    """
    Compute bivariate analysis (BIVAR) statistics for categorical features

    Parameters:
    datasets: dict - Dictionary of datasets {dataset_name: dataframe}
    features: list - List of categorical features to calculate
    target: str - Name of the target/label variable column
    output_plot: bool - Whether to generate visualizations
    figsize: tuple - Figure size

    Returns:
    Bivar result: pandas.DataFrame - DataFrame with columns: ['dataset', 'feature', 'category', 'count', 'good', 'bad', 'bad_rate']
    Figures: figures
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    # 1. Initialize results storage
    all_results = []

    # 2. Validate datasets and features
    for dname, df in datasets.items():
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Dataset '{dname}' missing features: {missing_features}")
        if target not in df.columns:
            raise ValueError(f"Dataset '{dname}' missing target column")

    # 3. Core calculation function
    def _calc_bivar(df: pd.DataFrame, feature: str, dname: str) -> pd.DataFrame:
        # Create category column (treat NaN as separate category)
        df = df.copy()
        df['category'] = df[feature].astype(str)
        df.loc[df[feature].isna(), 'category'] = 'Missing'

        # Calculate category statistics
        binned = (
            df.groupby('category', observed=True)
            .agg(
                count=(target, 'size'),
                good=(target, lambda x: (x == 0).sum()),
                bad=(target, lambda x: (x == 1).sum())
            )
            .reset_index()
            .rename(columns={'category': 'category'})
        )
        binned['bad_rate'] = binned['bad'] / binned['count']

        # Add dataset and feature identifiers
        binned.insert(0, 'feature', feature)
        binned.insert(0, 'dataset', dname)

        return binned

    # 4. Execute calculations
    for dname, df in datasets.items():
        for feature in features:
            result = _calc_bivar(df, feature, dname)
            all_results.append(result)

    # Combine all results
    combined_results = pd.concat(all_results, ignore_index=True)

    # 5. Visualization with consistent category ordering and full category sets
    if output_plot and len(features) > 0 and len(datasets) > 0:
        # Determine global category order for each feature (Missing always last)
        global_category_order = {}
        for feature in features:
            # Get all unique categories across all datasets
            all_cats = combined_results[combined_results['feature'] == feature]['category'].unique()
            # Separate non-missing and missing categories
            non_missing = sorted([cat for cat in all_cats if cat != 'Missing'])
            # Add "Missing" at the end
            global_category_order[feature] = non_missing + ['Missing']

        n_datasets = len(datasets)
        n_features = len(features)

        fig, axes = plt.subplots(
            n_features, n_datasets,
            figsize=(figsize[0], figsize[1] * n_features / max(n_datasets, 1)),
            squeeze=False
        )

        for j, dname in enumerate(datasets):
            for i, feature in enumerate(features):
                ax = axes[i, j]

                # Get data for this dataset and feature
                data = combined_results[
                    (combined_results['dataset'] == dname) &
                    (combined_results['feature'] == feature)
                    ]

                # Create template with all categories in global order
                template = pd.DataFrame({
                    'category': global_category_order[feature],
                    'dataset': dname,
                    'feature': feature
                })

                # Merge with actual data to include missing categories
                data = template.merge(
                    data,
                    on=['dataset', 'feature', 'category'],
                    how='left'
                )

                # Fill missing values (categories not present in this dataset)
                data.fillna({
                    'count': 0,
                    'good': 0,
                    'bad': 0,
                    'bad_rate': 0
                }, inplace=True)

                # Create positions for bars
                positions = np.arange(len(data))
                bar_width = 0.7

                # Bar chart for sample counts
                bars = ax.bar(
                    positions, data['count'],
                    width=bar_width,
                    color='skyblue',
                    alpha=0.7,
                    label='Sample Count'
                )

                # Calculate bad rate positions
                max_count = max(data['count'].max(), 1)  # Avoid division by zero
                bad_rates = data['bad_rate'].to_numpy()
                line_y = bad_rates * max_count * 1.1

                # Plot line connecting the points
                ax.plot(
                    positions, line_y,
                    color='red',
                    marker='o',
                    markersize=8,
                    label='Bad Rate'
                )

                # Add bad rate values as text
                for pos, br, count in zip(positions, bad_rates, data['count']):
                    # Only show bad rate text if there are samples
                    if count > 0:
                        text_y = br * max_count * 1.15
                        ax.text(
                            pos, text_y, f'{br:.3f}',
                            ha='center', va='bottom',
                            color='red', fontsize=9
                        )
                    else:
                        # Show placeholder for missing categories
                        text_y = 0.05 * max_count
                        ax.text(
                            pos, text_y, 'N/A',
                            ha='center', va='bottom',
                            color='gray', fontsize=8, alpha=0.7
                        )

                # Formatting
                ax.set_title(f"{dname} - {feature}", fontsize=12)
                ax.set_ylabel('Sample Count', color='skyblue')
                ax.tick_params(axis='y', labelcolor='skyblue')
                ax.set_xticks(positions)
                ax.set_xticklabels(
                    data['category'].tolist(),
                    rotation=45,
                    ha='right',
                    fontsize=9
                )

                # Second y-axis for bad rate
                ax2 = ax.twinx()
                # Set y-axis limits based on actual bad rates (ignore placeholder 0s)
                actual_bad_rates = data[data['count'] > 0]['bad_rate']
                y_max = actual_bad_rates.max() * 1.3 if len(actual_bad_rates) > 0 else 0.3
                ax2.set_ylim(0, y_max)
                ax2.set_ylabel('Bad Rate', color='red')
                ax2.tick_params(axis='y', labelcolor='red')

        plt.tight_layout()
        plt.show()

    return combined_results

def proc_means(data,numeric_attrs_list,categorical_attrs_list,file_name,file_location):
    """
    Generate descriptive statistics for a dataset with the given feature list

    Parameters:
    data: pandas.DataFrame - Dataset
    numeric_attrs_list: list - List of numeric features
    categorical_attrs_list: list - List of categorical features
    file_name: str - Name of output file
    file_location: str - Location of output file

    Returns:
    None
    """
    if len(numeric_attrs_list) != 0:
        temp=data[numeric_attrs_list].describe().T
        temp['cover_rate']=temp['count']/data.shape[0]
        temp['missing_rate']=1-temp['cover_rate']
        temp=temp.drop(columns=['cover_rate'],axis=1)
        location=file_location+file_name+'_numeric.csv'
        temp.to_csv(location)
    if len(categorical_attrs_list) != 0:
        temp=data[categorical_attrs_list].describe(include='all').T
        temp['cover_rate']=temp['count']/data.shape[0]
        temp['missing_rate'] = 1 - temp['cover_rate']
        temp = temp.drop(columns=['cover_rate'], axis=1)
        location=file_location+file_name+'_categorical.csv'
        temp.to_csv(location)

