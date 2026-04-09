from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Initialize or rebuild RAG vector data for chatbot"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            default=False,
            help="Delete the full collection and rebuild from all selected sources",
        )
        parser.add_argument(
            "--only-markdown",
            action="store_true",
            default=False,
            help="Ingest only markdown/txt files from chatbot/rag/raw_data",
        )
        parser.add_argument(
            "--only-catalog",
            action="store_true",
            default=False,
            help="Ingest only Dish + Category catalog data",
        )
        parser.add_argument(
            "--dish-id",
            type=int,
            default=None,
            help="Ingest one dish only by primary key",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Run ingest even if vector DB already has documents",
        )

    def handle(self, *args, **options):
        from restaurantBE.chatbot.rag.ingest import IngestService

        service = IngestService()

        dish_id = options.get("dish_id")
        if dish_id is not None:
            self.stdout.write(f"Updating dish {dish_id} in vector DB...")
            success = service.ingest_single_dish(dish_id)
            if not success:
                raise CommandError(f"Cannot ingest dish {dish_id}")
            self.stdout.write(self.style.SUCCESS(f"Done. Dish {dish_id} indexed."))
            return

        only_markdown = bool(options.get("only_markdown"))
        only_catalog = bool(options.get("only_catalog"))

        if only_markdown and only_catalog:
            raise CommandError("Cannot combine --only-markdown and --only-catalog")

        include_markdown = not only_catalog
        include_catalog = not only_markdown
        reset_collection = bool(options.get("reset"))
        force = bool(options.get("force"))

        if service.is_ready() and not reset_collection and not force:
            current_count = service.vector_db_service.count()
            self.stdout.write(
                self.style.WARNING(
                    "Vector DB already initialized "
                    f"({current_count} documents). "
                    "Skipping. Use --force or --reset to run again."
                )
            )
            return

        self.stdout.write("Starting RAG ingestion...")
        if reset_collection:
            self.stdout.write(self.style.WARNING("Collection reset requested."))

        result = service.ingest_all(
            reset_collection=reset_collection,
            include_markdown=include_markdown,
            include_catalog=include_catalog,
        )

        if "catalog" in result:
            catalog = result["catalog"]
            self.stdout.write(
                self.style.SUCCESS(
                    "Catalog indexed: "
                    f"{catalog.get('categories', 0)} categories, "
                    f"{catalog.get('dishes', 0)} dishes"
                )
            )

        if "markdown" in result:
            markdown = result["markdown"]
            self.stdout.write(
                self.style.SUCCESS(
                    "Markdown indexed: "
                    f"{markdown.get('total_files', 0)} files, "
                    f"{markdown.get('total_chunks', 0)} chunks"
                )
            )

        total = result.get("total_documents_in_db", 0)
        self.stdout.write(self.style.SUCCESS(f"Done. Total documents in DB: {total}"))
