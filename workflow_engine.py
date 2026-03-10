def recommend_workflow(query):

    q = query.lower()

    # RNA-seq
    if "paired-end rna" in q or "rna-seq" in q:

        return {
            "omics": "Transcriptomics",

            "workflow": [
                ("Quality control", "FastQC"),
                ("Trimming", "Trimmomatic"),
                ("Alignment", "HISAT2"),
                ("Quantification", "featureCounts"),
                ("Differential expression", "DESeq2")
            ]
        }

    # single cell RNA-seq
    if "single cell" in q or "scrna" in q:

        return {
            "omics": "Single-cell Transcriptomics",

            "workflow": [
                ("Read processing", "Cell Ranger"),
                ("Quality control", "Seurat"),
                ("Normalization", "SCTransform"),
                ("Clustering", "Seurat"),
                ("Visualization", "UMAP"),
                ("Cell annotation", "SingleR")
            ]
        }

    # ATAC-seq
    if "atac" in q:

        return {
            "omics": "Epigenomics",

            "workflow": [
                ("Quality control", "FastQC"),
                ("Alignment", "Bowtie2"),
                ("Peak calling", "MACS2"),
                ("Peak annotation", "Homer"),
                ("Visualization", "DeepTools")
            ]
        }

    # WGS / variant calling
    if "wgs" in q or "variant calling" in q:

        return {
            "omics": "Genomics",

            "workflow": [
                ("Quality control", "FastQC"),
                ("Alignment", "BWA"),
                ("Post-processing", "SAMtools"),
                ("Variant calling", "GATK"),
                ("Variant annotation", "ANNOVAR")
            ]
        }

    return None