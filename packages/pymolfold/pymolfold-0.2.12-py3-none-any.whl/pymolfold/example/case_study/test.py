import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def create_performance_plot():
    """
    Generates a high-quality, publication-ready plot comparing the prediction times
    of different models across various protein lengths.
    """
    # 1. 整理您的原始数据
    # A structured list of dictionaries is easy to convert to a DataFrame.
    data = [
        # CYCLOSPORIN A (11 aa)
        # ALLVTAGLVLA
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "Boltz2 w/MSA (cyclic)",
            "time": 13.13,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "Boltz2 w/MSA (cyclic)",
            "time": 12.61,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "Boltz2 w/MSA (cyclic)",
            "time": 12.61,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "Boltz2 (cyclic)",
            "time": 2.13,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "Boltz2 (cyclic)",
            "time": 2.24,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "Boltz2 (cyclic)",
            "time": 2.51,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "ESM3 (linear)",
            "time": 3.95,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "ESM3 (linear)",
            "time": 4.10,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "ESM3 (linear)",
            "time": 3.98,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "ESMFold (linear)",
            "time": 1.161,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "ESMFold (linear)",
            "time": 0.905,
        },
        {
            "protein": "Cyclosporin A",
            "pdb_id": "1CSA",
            "length": 11,
            "model": "ESMFold (linear)",
            "time": 0.7600,
        },
        # FYNOMER (85 aa)
        # MRGSGVTLFVALYDYQADRWTDLSFHKGEKFQILDASPPGDWWEARSLTTGETGYIPSNYVAPVDSIQGEQKLISEEDLHHHHHH
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "Boltz-2 w/MSA",
            "time": 13.62,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "Boltz-2 w/MSA",
            "time": 12.39,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "Boltz-2 w/MSA",
            "time": 13.19,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "Boltz-2",
            "time": 2.43,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "Boltz-2",
            "time": 3.39,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "Boltz-2",
            "time": 3.53,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "ESM3",
            "time": 5.51,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "ESM3",
            "time": 5.18,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "ESM3",
            "time": 5.44,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "ESMFold",
            "time": 2.3432,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "ESMFold",
            "time": 1.0584,
        },
        {
            "protein": "Fynomer",
            "pdb_id": "4AFQ",
            "length": 85,
            "model": "ESMFold",
            "time": 1.1270,
        },
        # ALB8(VHH) (123 aa)
        # EVQLVESGGGLVQPGNSLRLSCAASGFTFSSFGMSWVRQAPGKGLEWVSSISGSGSDTLYADSVKGRFTISRDNAKTTLYLQMNSLRPEDTAVYYCTIGGSLSRSSQGTLVTVSSTSHHHHHH
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "Boltz-2 w/MSA",
            "time": 15.05,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "Boltz-2 w/MSA",
            "time": 11.45,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "Boltz-2 w/MSA",
            "time": 13.49,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "Boltz-2",
            "time": 2.64,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "Boltz-2",
            "time": 2.10,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "Boltz-2",
            "time": 3.18,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "ESM3",
            "time": 5.54,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "ESM3",
            "time": 5.42,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "ESM3",
            "time": 4.96,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "ESMFold",
            "time": 2.9876,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "ESMFold",
            "time": 1.34754,
        },
        {
            "protein": "ALB8(VHH)",
            "pdb_id": "8Z8V-B",
            "length": 123,
            "model": "ESMFold",
            "time": 1.1064,
        },
        # Hydrolase mutant (298 aa)
        # MNFPRASRLMQAAVLGGLMAVSAAATAQTNPYARGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTFDYPSSRSSQQMAALRQVASLNGDSSSPIYGKVDTARMGVMGHSMGGGASLRSAANNPSLKAAIPQAPWDSQTNFSSVTVPTLIFACENDSIAPVNSHALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTAVSDFRTANCSLEHHHHHH
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "Boltz-2 w/MSA",
            "time": 20.62,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "Boltz-2 w/MSA",
            "time": 13.15,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "Boltz-2 w/MSA",
            "time": 13.30,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "Boltz-2",
            "time": 3.02,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "Boltz-2",
            "time": 2.94,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "Boltz-2",
            "time": 3.03,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "ESM3",
            "time": 6.19,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "ESM3",
            "time": 6.77,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "ESM3",
            "time": 6.54,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "ESMFold",
            "time": 4.481,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "ESMFold",
            "time": 2.309,
        },
        {
            "protein": "Hydrolase mutant",
            "pdb_id": "6KY5",
            "length": 298,
            "model": "ESMFold",
            "time": 1.740,
        },
        # Human Serum Albumin (585 aa)
        # DAHKSEVAHRFKDLGEENFKALVLIAFAQYLQQCPFEDHVKLVNEVTEFAKTCVADESAENCDKSLHTLFGDKLCTVATLRETYGEMADCCAKQEPERNECFLQHKDDNPNLPRLVRPEVDVMCTAFHDNEETFLKKYLYEIARRHPYFYAPELLFFAKRYKAAFTECCQAADKAACLLPKLDELRDEGKASSAKQRLKCASLQKFGERAFKAWAVARLSQRFPKAEFAEVSKLVTDLTKVHTECCHGDLLECADDRADLAKYICENQDSISSKLKECCEKPLLEKSHCIAEVENDEMPADLPSLAADFVESKDVCKNYAEAKDVFLGMFLYEYARRHPDYSVVLLLRLAKTYETTLEKCCAAADPHECYAKVFDEFKPLVEEPQNLIKQNCELFEQLGEYKFQNALLVRYTKKVPQVSTPTLVEVSRNLGKVGSKCCKHPEAKRMPCAEDYLSVVLNQLCVLHEKTPVSDRVTKCCTESLVNRRPCFSALEVDETYVPKEFNAETFTFHADICTLSEKERQIKKQTALVELVKHKPKATKEQLKAVMDDFAAFVEKCCKADDKETCFAEEGKKLVAASQAALGL
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "Boltz-2 w/MSA",
            "time": 18.63,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "Boltz-2 w/MSA",
            "time": 16.86,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "Boltz-2 w/MSA",
            "time": 18.49,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "Boltz-2",
            "time": 6.76,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "Boltz-2",
            "time": 6.72,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "Boltz-2",
            "time": 6.85,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "ESM3",
            "time": 8.57,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "ESM3",
            "time": 8.46,
        },
        {
            "protein": "Human Serum Albumin",
            "pdb_id": "8Z8V-A",
            "length": 585,
            "model": "ESM3",
            "time": 9.03,
        },
        # ALPHA-ACTININ-2 (876 aa)
        # YMIQEEEWDRDLLLDPAWEKQQRKTFTAWCNSHLRKAGTQIENIEEDFRNGLKLMLLLEVISGERLPKPDRGKMRFHKIANVNKALDYIASKGVKLVSIGAEEIVDGNVKMTLGMIWTIILRFAIQDISVEETSAKEGLLLWCQRKTAPYRNVNIQNFHTSWKDGLGLCALIHRHRPDLIDYSKLNKDDPIGNINLAMEIAEKHLDIPKMLDAEDIVNTPKPDERAIMTYVSCFYHAFAGAEQAETAANRICKVLAVNQENERLMEEYERLASELLEWIRRTIPWLENRTPAATMQAMQKKLEDFRDYRRKHKPPKVQEKCQLEINFNTLQTKLRISNRPAFMPSEGKMVSDIAGAWQRLEQAEKGYEEWLLNEIRRLERLEHLAEKFRQKASTHETWAYGKEQILLQKDYESASLTEVRALLRKHEAFESDLAAHQDRVEQIAAIAQELNELDYHDAVNVNDRCQKICDQWDRLGTLTQKRREALERMEKLLETIDQLHLEFAKRAAPFNNWMEGAMEDLQDMFIVHSIEEIQSLITAHEQFKATLPEADGERQSIMAIQNEVEKVIQSYNIRISSSNPYSTVTMDELRTKWDKVKQLVPIRDQSLQEELARQHANERLRRQFAAQANAIGPWIQNKMEEIARSSIQITGALEDQMNQLKQYEHNIINYKNNIDKLEGDHQLIQEALVFDNKHTNYTMEHIRVGWELLLTTIARTINEVETQILTRDAKGITQEQMNEFRASFNHFDRRKNGLMDHEDFRACLISMGYDLGEAEFARIMTLVDPNGQGTVTFQSFIDFMTRETADTDTAEQVIASFRILASDKPYILAEELRRELPPDQAQYCIKRMPAYSGPGSVPGALDYAAFSSALYGESDL
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "Boltz-2 w/MSA",
            "time": 34.81,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "Boltz-2 w/MSA",
            "time": 27.37,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "Boltz-2 w/MSA",
            "time": 28.06,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "Boltz-2",
            "time": 14.45,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "Boltz-2",
            "time": 14.66,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "Boltz-2",
            "time": 14.68,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "ESM3",
            "time": 10.89,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "ESM3",
            "time": 10.37,
        },
        {
            "protein": "alpha-Actinin-2",
            "pdb_id": "4D1E",
            "length": 876,
            "model": "ESM3",
            "time": 11.49,
        },
    ]
    df = pd.DataFrame(data)

    # 简化模型名称以便于绘图
    df["model"] = df["model"].replace(
        {
            "Boltz2 w/MSA (cyclic)": "Boltz-2 w/MSA",
            "Boltz2 (cyclic)": "Boltz-2",
            "ESM3 (linear)": "ESM3",
            "ESMFold (linear)": "ESMFold",
        }
    )

    # 2. 计算均值和标准差
    agg_df = (
        df.groupby(["model", "length", "pdb_id"])
        .agg(mean_time=("time", "mean"), std_time=("time", "std"))
        .reset_index()
    )

    # 3. 设置绘图风格 (专业、适合出版)
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.5)
    fig, ax = plt.subplots(figsize=(12, 8))

    # 4. 定义颜色、标记和线条样式以区分模型
    palette = {
        "ESMFold": "#d95f02",  # Vermillion f6d638
        "ESM3": "#f6c770",  # Muted Blue
        "Boltz-2": "#80b1d3",  # Safety Orange
        "Boltz-2 w/MSA": "#8dd3c7",  # Cooked Asparagus Green
    }
    markers = {
        "ESMFold": "o",
        "ESM3": "o",  # Circle
        "Boltz-2": "s",  # Square
        "Boltz-2 w/MSA": "s",  # Triangle
    }
    linestyles = {
        "ESMFold": "--",  # Solid
        "ESM3": "--",  # Solid
        "Boltz-2": ":",  # Dashed
        "Boltz-2 w/MSA": ":",  # Dotted
    }

    # 5. 循环绘制每个模型的数据
    for model_name in ["ESMFold", "ESM3", "Boltz-2", "Boltz-2 w/MSA"]:
        model_data = agg_df[agg_df["model"] == model_name].sort_values("length")

        # Special handling for ESMFold to not connect missing data points
        if model_name == "ESMFold":
            # Split data into continuous segments
            segments = []
            current_segment = []
            if not model_data.empty:
                current_segment.append(model_data.iloc[0])
                for i in range(1, len(model_data)):
                    # A large gap in length might indicate a new segment,
                    # here we assume data is continuous unless a point is missing.
                    # The unique lengths are [11, 85, 123, 298, 585, 876]
                    # The gap between 298 and 585 is where ESMFold stops.
                    # A simple way is to check if the length is > 400.
                    if model_data.iloc[i]["length"] > 400:
                        segments.append(pd.DataFrame(current_segment))
                        current_segment = []
                    current_segment.append(model_data.iloc[i])
                if current_segment:
                    segments.append(pd.DataFrame(current_segment))

            for i, segment in enumerate(segments):
                ax.errorbar(
                    x=segment["length"],
                    y=segment["mean_time"],
                    yerr=segment["std_time"],
                    label=model_name if i == 0 else "",  # Only label the first segment
                    marker=markers[model_name],
                    color=palette[model_name],
                    linestyle=linestyles[model_name],
                    linewidth=2.5,
                    markersize=10,
                    capsize=5,
                    elinewidth=1.5,
                )
            # Add annotation for ESMFold limit
            last_esm_point = model_data[model_data["length"] < 400].iloc[-1]
            # ax.text(last_esm_point['length'] + 20, last_esm_point['mean_time'] + 1,
            #         'ESMFold limit (~400 aa)', fontsize=12, color=palette['ESMFold'],
            #         ha='left')
        else:
            ax.errorbar(
                x=model_data["length"],
                y=model_data["mean_time"],
                yerr=model_data["std_time"],
                label=model_name,
                marker=markers[model_name],
                color=palette[model_name],
                linestyle=linestyles[model_name],
                linewidth=2.5,
                markersize=10,
                capsize=5,  # Error bar caps
                elinewidth=1.5,
            )

    # 6. 美化和标注图表
    ax.set_title(
        "Prediction Time vs. Protein Length for Different Models", fontsize=20, pad=20
    )
    ax.set_xlabel("Protein Length (amino acids)", fontsize=16, labelpad=15)
    ax.set_ylabel("Prediction Time (seconds)", fontsize=16, labelpad=15)

    # 自定义X轴刻度以显示蛋白质ID和长度
    unique_lengths = sorted(agg_df["length"].unique())
    pdb_map = (
        agg_df[["length", "pdb_id"]].drop_duplicates().set_index("length")["pdb_id"]
    )
    ax.set_xticks(unique_lengths)
    ax.set_xticklabels(
        [f"{pdb_map[length]} ({length} aa)" for length in unique_lengths],
        rotation=30,
        ha="right",
        fontsize=12,
    )

    ax.tick_params(axis="both", which="major", labelsize=14)
    ax.grid(which="major", linestyle="--", linewidth="0.7")

    # 将Y轴的起点设置为0
    ax.set_ylim(bottom=0)

    # 创建并放置图例
    legend = ax.legend(title="Model", fontsize=14, title_fontsize=16)
    legend.get_frame().set_alpha(0.9)
    legend.get_frame().set_facecolor("white")

    # 添加边框
    for spine in ax.spines.values():
        spine.set_edgecolor("black")
        spine.set_linewidth(1.2)

    plt.tight_layout()

    # 7. 保存为高分辨率PNG和矢量PDF
    plt.savefig("model_performance_comparison.png", dpi=300, bbox_inches="tight")
    plt.savefig("model_performance_comparison.pdf", bbox_inches="tight")

    print(
        "Plots saved as 'model_performance_comparison.png' and 'model_performance_comparison.pdf'"
    )


create_performance_plot()
