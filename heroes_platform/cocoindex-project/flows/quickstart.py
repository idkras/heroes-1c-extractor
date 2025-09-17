import cocoindex


@cocoindex.flow_def(name="TextEmbedding")
def text_embedding_flow(
    flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope
):
    # Add a data source to read files from a directory
    data_scope["documents"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(path="data/markdown_files")
    )

    # Add a collector for data to be exported to the vector index
    doc_embeddings = data_scope.add_collector()

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
            # Embed the chunk, put into `embedding` field
            chunk["embedding"] = chunk["text"].transform(
                cocoindex.functions.SentenceTransformerEmbed(
                    model="sentence-transformers/all-MiniLM-L6-v2"
                )
            )

            # Collect the chunk into the collector.
            doc_embeddings.collect(
                filename=doc["filename"],
                location=chunk["location"],
                text=chunk["text"],
                embedding=chunk["embedding"],
            )

    # Export collected data to a vector index.
    doc_embeddings.export(
        "doc_embeddings",
        cocoindex.targets.Postgres(),
        primary_key_fields=["filename", "location"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
            )
        ],
    )


if __name__ == "__main__":
    print("CocoIndex flow defined successfully!")
