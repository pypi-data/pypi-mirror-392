# -*- coding: utf-8 -*-

import sys
import logging
from argparse import ArgumentParser, RawTextHelpFormatter
import os
import pandas as pd
import re
import subprocess
import numpy as np


def build_parser():
    description = (
        "Description:\n\n"
        "This script calculates CircDEAS differential PSI results.\n"
        "You need to provide the working folder path, control and treat column indices.\n"
    )
    parser = ArgumentParser(description=description,
                            formatter_class=RawTextHelpFormatter,
                            add_help=False)
    parser.add_argument("-f", "--folder", default=os.getcwd(),
                        help="Path to the working folder (default: current working directory)"
                        )
    parser.add_argument("-c", "--control-columns", required=True, nargs='+', type=int,
                        help="Indices for control group columns, space-separated (e.g., -c 0 1 2)")
    parser.add_argument("-t", "--treat-columns", required=True, nargs='+', type=int,
                        help="Indices for treatment group columns, space-separated (e.g., -t 0 3 4)")
    parser.add_argument("-o", "--result_folder_name", default="CircDEAS_DPSI_result",
                        help="Name of the result folder under the input folder "
                             "(e.g., CircDEAS_DPSI_result_v2)"
                        )
    parser.add_argument("-m", "--mode", default="INFO",
                        help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    parser.add_argument("-h", "--help", action="help", help="Show help and exit.")
    return parser


def setup_logger(level="INFO"):
    level = level.upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logger(args.mode)

    folder = args.folder
    control_columns = args.control_columns
    treat_columns = args.treat_columns
    result_folder_name = args.result_folder_name
    CircDEAS_result = os.path.join(folder, result_folder_name)
    os.makedirs(CircDEAS_result, exist_ok=True)
    logging.info("Running CircDEAS pipeline...")
    logging.info(f"Folder: {folder}")
    logging.info(f"Control columns: {control_columns}")
    logging.info(f"Treat columns: {treat_columns}")
    logging.info(f"Output will be saved to: {CircDEAS_result}")

    process_folder = os.path.join(folder, 'process_result')
    os.makedirs(process_folder, exist_ok=True)
    input_folder = process_folder

    def process_file_pair(full_file, as_file, output_file):
        try:
            df_full = pd.read_csv(full_file, sep='\t')
            df_as = pd.read_csv(as_file, sep='\t')
        except FileNotFoundError as e:
            print(f"not found：{e}")
            return

        if 'alternatively_spliced_exon' in df_as.columns:
            df_as['alternatively_spliced_exon'] = (
                df_as['alternatively_spliced_exon'].astype(str).str.replace(':', '-')
            )
            df_as_modified = df_as
        else:
            print(" 'alternatively_spliced_exon' does not exist.！")
            return
        df_result = df_full.copy()
        if 'Image_ID' in df_result.columns:
            df_result = df_result.drop(columns=['Image_ID'])
        if 'geneid' in df_result.columns:
            df_result = df_result[df_result['geneid'].notna() & (df_result['geneid'] != '')]
        # TPM-cal
        if 'estimated_isoform_read_count' in df_result.columns and 'isoform_length' in df_result.columns:
            df_result['isoform_RPK'] = (
                    df_result['estimated_isoform_read_count'] / (df_result['isoform_length'] / 1000)
            )
            RPK_sum = df_result['isoform_RPK'].sum(skipna=True)
            df_result['TPM'] = (df_result['isoform_RPK'] / RPK_sum) * 1e6
        else:
            print("The column used for calculating TPM is missing.")
            return
        result_list = []
        for _, row_result in df_result.iterrows():
            circle_id = row_result['Circle_ID']
            isoform_cirexon = row_result['isoform_cirexon']
            matching_as_rows = df_as_modified[df_as_modified['circRNA_id'] == circle_id]
            if matching_as_rows.empty:
                result_list.append(
                    {**row_result.to_dict(), 'AS_type': 'NO_AS', 'alternatively_spliced_exon': 'NO_AS_exon'})
            else:
                cirexon_list = isoform_cirexon.split(',')
                for _, as_row in matching_as_rows.iterrows():
                    alternatively_spliced_exon = as_row['alternatively_spliced_exon']
                    as_type = as_row['AS_type']
                    if alternatively_spliced_exon in cirexon_list:
                        result_list.append({**row_result.to_dict(), 'AS_type': as_type,
                                            'alternatively_spliced_exon': alternatively_spliced_exon})
                    else:
                        result_list.append(
                            {**row_result.to_dict(), 'AS_type': 'NO_AS', 'alternatively_spliced_exon': 'NO_AS_exon'})

        df_final = pd.DataFrame(result_list)

        processed_rows = []
        for _, row in df_final.iterrows():
            as_type = row['AS_type']
            if pd.notna(as_type) and ',' in as_type:
                for split_as in [x.strip() for x in as_type.split(',') if x.strip()]:
                    new_row = row.copy()
                    new_row['AS_type'] = split_as
                    processed_rows.append(new_row)
            else:
                processed_rows.append(row)
        df_result_with_AS = pd.DataFrame(processed_rows)

        def custom_deduplicate(df):
            key_columns = ['Chr', 'start', 'end', 'geneid', 'isoform_cirexon']
            deduplicated_rows = []
            grouped = df.groupby(key_columns)
            for _, group_data in grouped:
                non_no_as_rows = group_data[group_data['AS_type'] != 'NO_AS']
                if len(non_no_as_rows) > 0:
                    deduplicated_rows.extend(non_no_as_rows.to_dict('records'))
                else:
                    deduplicated_rows.append(group_data.iloc[0].to_dict())
            return pd.DataFrame(deduplicated_rows)

        df_result_with_AS = custom_deduplicate(df_result_with_AS)
        df_result_with_AS = df_result_with_AS.drop_duplicates()
        df_result_with_AS.to_csv(output_file, sep='\t', index=False)

    file_list = os.listdir(folder)
    results = set(f.replace('_prefix.list', '') for f in file_list if f.endswith('_prefix.list'))
    merged_file = os.path.join(folder, "merged_result_with_TPM.list")
    expression_output_file = os.path.join(CircDEAS_result, "all_isoform_expression.list")
    final_output_file = os.path.join(CircDEAS_result, "all_event_with_isoform.ioe")

    for result in results:
        full_file = os.path.join(folder, f'{result}_prefix.list')
        as_file = os.path.join(folder, f'{result}_AS.list')
        output_file = os.path.join(process_folder, f'{result}_result_with_AS.list')
        # print(f"\n Processing file group：{result}")
        process_file_pair(full_file, as_file, output_file)

    files = [f for f in os.listdir(input_folder) if f.endswith(".list")]
    sample_ids = sorted(
        [f.split("_")[0] for f in files],
        key=lambda x: int(re.search(r"\d+", x).group())
    )
    sample_num = len(sample_ids)
    control_cols = control_columns[1:]
    treat_cols = treat_columns[1:]
    merged_data = pd.DataFrame()

    sample_order = []
    for file in files:
        file_path = os.path.join(input_folder, file)
        df = pd.read_csv(file_path, sep="\t")
        sample_id = file.split("_")[0]
        sample_order.append(sample_id)
        df = df.rename(columns={"TPM": sample_id})

        columns_to_keep = [
            "Circle_ID", "Chr", "start", "end", "isoform_length", "isoform_state",
            "geneid", "isoform_cirexon", "AS_type", "alternatively_spliced_exon", sample_id
        ]
        df = df[columns_to_keep]

        if merged_data.empty:
            merged_data = df
        else:
            merged_data = pd.merge(
                merged_data, df,
                on=["Circle_ID", "Chr", "start", "end", "isoform_length", "isoform_state",
                    "geneid", "isoform_cirexon", "AS_type", "alternatively_spliced_exon"],
                how="outer"
            )
    key_columns = [
        "Circle_ID", "Chr", "start", "end", "isoform_length", "isoform_state",
        "geneid", "isoform_cirexon", "AS_type", "alternatively_spliced_exon"
    ]
    sample_columns_sorted = [id for id in sample_order if id in merged_data.columns]
    merged_data = merged_data[key_columns + sample_columns_sorted]
    merged_data = merged_data.fillna(0)
    duplicate_mask = merged_data.duplicated('isoform_cirexon', keep=False)
    to_process = merged_data[duplicate_mask].copy()
    remaining = merged_data[~duplicate_mask].copy()

    if len(to_process) == 0:
        final_result = remaining
    else:
        key_columns = ["Circle_ID", "Chr", "start", "end", "isoform_length",
                       "isoform_state", "geneid", "isoform_cirexon"]

        expr_columns = [col for col in to_process.columns
                        if col not in key_columns + ["AS_type", "alternatively_spliced_exon"]]
        grouped = to_process.groupby(key_columns)
        processed_rows = []
        for keys, group in grouped:
            merged_row = group.iloc[0][key_columns].copy()
            for col in expr_columns:
                merged_row[col] = group[col].max()
            as_types = group['AS_type'].dropna()
            if len(as_types) > 0:
                as_list = [str(x) for x in as_types]
                if len(as_list) > 1 and 'NO_AS' in as_list:
                    as_list = [x for x in as_list if x != 'NO_AS']
                merged_row['AS_type'] = ", ".join(as_list)
            else:
                merged_row['AS_type'] = np.nan
            alt_exons = group['alternatively_spliced_exon'].dropna()
            if len(alt_exons) > 0:
                alt_list = [str(x) for x in alt_exons]
                if len(alt_list) > 1 and 'NO_AS_exon' in alt_list:
                    alt_list = [x for x in alt_list if x != 'NO_AS_exon']
                merged_row['alternatively_spliced_exon'] = ", ".join(alt_list)
            else:
                merged_row['alternatively_spliced_exon'] = np.nan
            processed_rows.append(merged_row)

        processed_df = pd.DataFrame(processed_rows)

        def split_AS_columns(row):
            as_types = str(row['AS_type']).split(", ") if pd.notna(row['AS_type']) else []
            alt_exons = str(row['alternatively_spliced_exon']).split(", ") if pd.notna(
                row['alternatively_spliced_exon']) else []
            if len(as_types) > 1 and len(alt_exons) > 1 and len(as_types) == len(alt_exons):
                new_rows = []
                for as_type, alt_exon in zip(as_types, alt_exons):
                    new_row = row.copy()
                    new_row['AS_type'] = as_type
                    new_row['alternatively_spliced_exon'] = alt_exon
                    new_rows.append(new_row)
                return new_rows
            elif len(as_types) > 1:
                new_rows = []
                for as_type in as_types:
                    new_row = row.copy()
                    new_row['AS_type'] = as_type
                    new_row['alternatively_spliced_exon'] = alt_exons[0] if len(alt_exons) > 0 else np.nan
                    new_rows.append(new_row)
                return new_rows
            elif len(alt_exons) > 1:
                new_rows = []
                for alt_exon in alt_exons:
                    new_row = row.copy()
                    new_row['AS_type'] = as_types[0] if len(as_types) > 0 else np.nan
                    new_row['alternatively_spliced_exon'] = alt_exon
                    new_rows.append(new_row)
                return new_rows
            else:
                return [row]

        split_rows = []
        for _, row in processed_df.iterrows():
            split_rows.extend(split_AS_columns(row))
        processed_df = pd.DataFrame(split_rows)
        merged_data = pd.concat([processed_df, remaining], ignore_index=True)
        merged_data = merged_data.drop_duplicates()

    def process_isoform_cirexon(isoform_cirexon):
        isoform_cirexon = isoform_cirexon.rstrip(',')
        intervals = isoform_cirexon.split(',')
        starts = [int(interval.split('-')[0]) for interval in intervals]
        ends = [int(interval.split('-')[1]) for interval in intervals]
        number_of_exons = len(intervals)
        exon_sizes = [end - start + 1 for start, end in zip(starts, ends)]
        exon_offsets = [start - starts[0] for start in starts]
        return {
            'Number_of_exons': number_of_exons,
            'Exon_sizes': '-'.join(map(str, exon_sizes)),
            'Exon_offsets': '-'.join(map(str, exon_offsets))
        }

    processed_data = merged_data['isoform_cirexon'].apply(process_isoform_cirexon)
    merged_data['Number_of_exons'] = processed_data.apply(lambda x: x['Number_of_exons'])
    merged_data['Exon_sizes'] = processed_data.apply(lambda x: x['Exon_sizes'])
    merged_data['Exon_offsets'] = processed_data.apply(lambda x: x['Exon_offsets'])

    merged_data["event"] = (
            merged_data["geneid"].astype(str) + "_" +
            merged_data["Chr"].astype(str) + "_" +
            merged_data["AS_type"].astype(str) + "_" +
            merged_data["alternatively_spliced_exon"].astype(str)
    )
    merged_data["isoform"] = (
            merged_data["Chr"].astype(str) + "_" +
            merged_data["geneid"].astype(str) + "_" +
            merged_data["Circle_ID"].astype(str) + "_" +
            merged_data["Number_of_exons"].astype(str) + "_" +
            merged_data["Exon_sizes"].astype(str) + "_" +
            merged_data["Exon_offsets"].astype(str) + "_" +
            merged_data["isoform_length"].astype(str)
    )
    merged_data.to_csv(merged_file, sep="\t", index=False)
    print(f"Merge is complete and saved. The result has been saved to:{merged_file}")
    expression_columns = ["isoform"] + sample_ids
    extracted_data = merged_data[expression_columns]
    extracted_data = extracted_data.drop_duplicates(subset=["isoform"])
    # extracted_data = extracted_data.drop_duplicates()
    isoform_expression = merged_data[expression_columns]
    isoform_expression = isoform_expression.drop_duplicates(subset=["isoform"])
    extracted_data.to_csv(expression_output_file, sep="\t", index=False, header=False)
    with open(expression_output_file, 'r') as f:
        lines = f.readlines()
    sample_id_line = "\t".join(sample_ids) + "\n"
    lines.insert(0, sample_id_line)
    with open(expression_output_file, 'w') as f:
        f.writelines(lines)

    filtered_data = merged_data[merged_data["AS_type"] != "NO_AS"]
    alternative_transcripts = filtered_data.groupby(["Chr", "geneid", "event"])["isoform"].apply(
        lambda x: ",".join(sorted(set(x)))
    ).reset_index()
    alternative_transcripts.rename(columns={"isoform": "alternative_transcripts"}, inplace=True)
    # print("Alternative transcripts preview:")
    # print(alternative_transcripts.head())

    total_transcripts = merged_data.groupby(["Chr", "geneid"])["isoform"].apply(
        lambda x: ",".join(sorted(set(x)))
    ).reset_index()

    total_transcripts.rename(columns={"isoform": "total_transcripts"}, inplace=True)
    final_result = pd.merge(alternative_transcripts, total_transcripts, on=["Chr", "geneid"], how="left")
    # print("Final result preview:")
    # print(final_result.head())

    final_result = final_result.rename(columns={
        "event": "event_id",
        "alternative_transcripts": "alt_iso",
        "total_transcripts": "total_iso"
    })
    final_result.to_csv(final_output_file, sep='\t', index=False)

    def run_suppa_psi(ioe_path, expr_path, output_dir, total_filter=10):
        os.makedirs(output_dir, exist_ok=True)
        cmd = [
            "python",
            "psiCalculator.py",
            "-i", ioe_path,
            "-e", expr_path,
            "-o", os.path.join(output_dir, "psi_results"),
            "-f", str(total_filter),
            "--save_tpm_events"
        ]
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return {
                "psi": os.path.join(output_dir, "psi_results.psi"),
                "tpm": os.path.join(output_dir, "psi_results.tpm")
            }

        except subprocess.CalledProcessError as e:
            print("PSI calculation failed:")
            print(e.stderr)
            raise

    def run_suppa_diffsplice(
            ioe_path,
            psi_files,
            tpm_files,
            output_prefix,
            method="empirical",
            gene_correction=True,
            save_tpm_events=True,
            alpha=0.05,
            paired=False,
            lower_bound=0.0,
            tpm_threshold=0.0,
            nan_threshold=0.0,
            area=1000,
            combination=False,
            median=False
    ):

        out_dir = os.path.dirname(output_prefix) or "."
        os.makedirs(out_dir, exist_ok=True)

        cmd = [
            "python",
            "significanceCalculator.py",
            "-m", method,
            "-i", ioe_path,
            "-o", output_prefix,
            "-al", str(alpha),
            "-l", str(lower_bound),
            "-th", str(tpm_threshold),
            "-nan", str(nan_threshold),
            "-a", str(area),
            "-p", *psi_files,
            "-e", *tpm_files,
        ]
        if gene_correction:
            cmd.append("-gc")
        if save_tpm_events:
            cmd.append("--save_tpm_events")
        if paired:
            cmd.append("-pa")
        if combination:
            cmd.append("-c")
        if median:
            cmd.append("-me")
        # logging.info(" ".join(cmd) + "\n")
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # print(result.stdout)

            outputs = {
                "dpsi": f"{output_prefix}_dpsi.tsv",
                "pvalues": f"{output_prefix}_pvalues.tsv"
            }
            return outputs

        except subprocess.CalledProcessError as e:
            print("differential analysis has failed.：")
            print(e.stderr)
            raise

    def handle_missing_values(df, columns):
        col_names = [df.columns[i] for i in columns]
        for index in df.index:
            row_subset = df.loc[index, col_names]
            nan_count = row_subset.isna().sum()
            if int(sample_num / 4) < 2:
                sample_half = 2
            else:
                sample_half = sample_num / 4
            if nan_count <= sample_half and nan_count > 0:
                non_zero_non_na = row_subset[row_subset != 0].dropna()
                if len(non_zero_non_na) > 0:
                    row_mean = non_zero_non_na.mean()
                else:
                    row_mean = 0
                for col in col_names:
                    if pd.isna(df.at[index, col]):
                        df.at[index, col] = row_mean

    
    CircDEAS_ioe_file = os.path.join(CircDEAS_result, "all_event_with_isoform.ioe")
    CircDEAS_expr_file = os.path.join(CircDEAS_result, "all_isoform_expression.list")

    try:
        suppa_results = run_suppa_psi(
            ioe_path=CircDEAS_ioe_file,
            expr_path=CircDEAS_expr_file,
            output_dir=CircDEAS_result,
            total_filter=0
        )

        df_psi = pd.read_csv(suppa_results["psi"], sep="\t")
        df_psi = df_psi.reset_index().rename(columns={"index": "event_id"})
        df_psi_file = os.path.join(CircDEAS_result, 'all_events.psi')
        df_psi.to_csv(df_psi_file, sep="\t", index=False)

        df_events = pd.read_csv(CircDEAS_ioe_file, sep="\t")
        merged_df = pd.merge(
            df_events,
            df_psi,
            on="event_id",
            how="left"
        )
        final_output = os.path.join(CircDEAS_result, "final_results_with_psi.list")
        merged_df.to_csv(final_output, sep="\t", index=False)
        df_psi = pd.read_csv(suppa_results["psi"], sep="\t")
        isoform_expression = isoform_expression.set_index(isoform_expression.columns[0])
        isoform_expression_output = os.path.join(CircDEAS_result, "all_isoform_expression.list")
        isoform_expression.to_csv(isoform_expression_output, sep="\t", index=True)
        project_events_output = os.path.join(CircDEAS_result, 'all_events.psi')
        project_events = pd.read_csv(project_events_output, sep='\t', header=0)
        handle_missing_values(project_events, control_cols)
        handle_missing_values(project_events, treat_cols)
        project_events = project_events.dropna()
        project_events_file = os.path.join(CircDEAS_result, 'all_events.psi')
        project_events.to_csv(project_events_file, sep='\t', index=False)
        all_isoform_expression_output = os.path.join(CircDEAS_result, 'all_isoform_expression.list')
        all_isoform_expression = pd.read_csv(all_isoform_expression_output, sep='\t')
        control_data = project_events.iloc[:, control_columns]
        control_data_output = os.path.join(CircDEAS_result, 'control.psi')
        control_data.to_csv(control_data_output, sep='\t', header=True, index=False)
        control_tpm = all_isoform_expression.iloc[:, control_columns]
        control_tpm_output = os.path.join(CircDEAS_result, 'control.tpm')
        control_tpm.to_csv(control_tpm_output, sep='\t', header=True, index=False)
        treat_data = project_events.iloc[:, treat_columns]
        treat_data_output = os.path.join(CircDEAS_result, 'treat.psi')
        treat_data.to_csv(treat_data_output, sep='\t', header=True, index=False)
        treat_tpm = all_isoform_expression.iloc[:, treat_columns]
        treat_tpm_output = os.path.join(CircDEAS_result, 'treat.tpm')
        treat_tpm.to_csv(treat_tpm_output, sep='\t', header=True, index=False)
        psi_files = [
            os.path.join(CircDEAS_result, "treat.psi"),
            os.path.join(CircDEAS_result, "control.psi"),
        ]
        tpm_files = [
            os.path.join(CircDEAS_result, "treat.tpm"),
            os.path.join(CircDEAS_result, "control.tpm"),
        ]
        diff_out_prefix = os.path.join(CircDEAS_result, "all_event_diffSplice")
        diff_results = run_suppa_diffsplice(
            ioe_path=CircDEAS_ioe_file,
            psi_files=psi_files,
            tpm_files=tpm_files,
            output_prefix=diff_out_prefix,
            method="empirical",
            gene_correction=True,
            save_tpm_events=True
        )
        files_to_delete = ["psi_results.psi", "psi_results.tpm", "final_results_with_psi.list",
                           "all_event_diffSplice.psivec", "all_event_diffSplice_avglogtpm.tab"]
        for filename in files_to_delete:
            file_path = os.path.join(CircDEAS_result, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Process execution failed：{str(e)}")
        exit(1)
    print(f"All processes have been completed!")

if __name__ == "__main__":
    main()
