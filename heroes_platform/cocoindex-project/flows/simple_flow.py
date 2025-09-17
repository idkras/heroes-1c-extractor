import cocoindex


@cocoindex.flow_def(name="SimpleTextFlow")
def simple_text_flow(
    flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope
):
    # Add a data source to read files from a directory
    data_scope["documents"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(path="data/markdown_files")
    )

    # Add a collector for data to be exported
    doc_texts = data_scope.add_collector()

    # Transform data of each document
    with data_scope["documents"].row() as doc:
        # Split the document into chunks, put into `chunks` field
        doc["chunks"] = doc["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="markdown",
            chunk_size=2000,
            chunk_overlap=500,
        )

        # Transform data of each chunk
        with doc["chunks"].row() as chunk:
            # Collect the chunk into the collector.
            doc_texts.collect(
                filename=doc["filename"],
                location=chunk["location"],
                text=chunk["text"],
            )

    # Export collected data to PostgreSQL
    doc_texts.export(
        "doc_texts",
        cocoindex.targets.Postgres(),
        primary_key_fields=["filename", "location"],
    )


if __name__ == "__main__":
    print("Simple CocoIndex flow defined successfully!")
