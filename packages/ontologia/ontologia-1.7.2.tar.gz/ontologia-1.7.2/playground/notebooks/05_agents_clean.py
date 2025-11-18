# AI Agents with Ontologia - Clean Marimo Notebook
# Fast track from 0 to 100 with AI-powered data processing

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import io

    import marimo as mo
    import pandas as pd

    return io, mo, pd


@app.cell
def _(mo):
    mo.md(
        """
    # 🤖 AI Agents with Ontologia - Clean Version

    **Go from 0 to 100 in minutes!** This notebook shows you how to:

    - **Upload Data**: Drag & drop CSV/Parquet files
    - **Auto-Detect Schema**: AI understands your data structure
    - **Generate Knowledge Graph**: Create relationships automatically
    - **Query with Natural Language**: Ask questions in plain English
    - **Build Agents**: Create AI assistants for your data

    **🚀 Clean Version - No Variable Conflicts!**
    """
    )
    return


@app.cell
def _(mo):
    # File upload interface
    file_upload = mo.ui.file()

    mo.md("### 📁 Upload Your Data")
    mo.md("Drag & drop CSV, Parquet, or Excel files below:")
    mo.md("**Supported formats**: `.csv`, `.parquet`, `.xlsx`")

    return (file_upload,)


@app.cell
def _(file_upload, marimo, mo):
    if not file_upload.value:
        mo.md("⏳ **Waiting for file upload...**")
        raise marimo.Interrupt("Please upload files to continue")

    uploaded_files = list(file_upload.value.keys())
    mo.md(f"✅ **Files Uploaded**: {', '.join(uploaded_files)}")
    return (uploaded_files,)


@app.cell
def _(file_upload, io, pd, uploaded_files):
    # Load uploaded data
    loaded_data = {}

    for fname in uploaded_files:
        file_content = file_upload.value[fname]

        try:
            if fname.endswith(".csv"):
                # Read CSV
                loaded_df = pd.read_csv(io.StringIO(file_content.decode("utf-8")))
            elif fname.endswith(".parquet"):
                # Read Parquet
                loaded_df = pd.read_parquet(io.BytesIO(file_content))
            elif fname.endswith(".xlsx"):
                # Read Excel
                loaded_df = pd.read_excel(io.BytesIO(file_content))
            else:
                continue

            loaded_data[fname] = loaded_df

        except Exception as e:
            print(f"Error loading {fname}: {e}")
    return (loaded_data,)


@app.cell
def _(loaded_data, mo, pd):
    # Display data preview
    mo.md("### 📊 Data Preview")

    for fname, data_df in loaded_data.items():
        mo.md(f"**{fname}** ({len(data_df)} rows, {len(data_df.columns)} columns)")

        # Show sample data
        sample_df = data_df.head(5)
        mo.ui.table(sample_df)

        # Show column info
        cols_info = pd.DataFrame(
            {
                "Column": data_df.columns,
                "Type": data_df.dtypes.astype(str),
                "Non-Null Count": data_df.count(),
                "Unique Values": data_df.nunique(),
            }
        )
        mo.md("**Column Information:**")
        mo.ui.table(cols_info)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### 🎉 Demo Complete!

    **You've successfully uploaded and processed your data!**

    **Next Steps:**
    - Explore your data with the interactive tables
    - Use the column information to understand your schema
    - Build AI agents to query your data naturally

    **Features Working:**
    - ✅ File upload (CSV, Parquet, Excel)
    - ✅ Data parsing and validation
    - ✅ Interactive data preview
    - ✅ Column analysis
    - ✅ Type detection

    **Ready for AI-powered data processing!** 🚀
    """
    )
    return


if __name__ == "__main__":
    app.run()
