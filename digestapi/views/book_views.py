"""Views for handling book-related API endpoints"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from digestapi.models import Book
from .category_views import CategorySerializer


class BookSerializer(serializers.ModelSerializer):
    """Serializer for the Book model.

    Converts Book instances to/from JSON for API responses.

    Two fields here go beyond simple model-field mapping and are worth
    understanding:

    1. `categories` — the Book model defines a ManyToManyField to Category
       through the BookCategory join table.  By default DRF would serialize
       this as a flat list of integer primary keys, e.g. [2, 4, 9].  Replacing
       it with a nested CategorySerializer(many=True) makes the response richer:
       [{"id": 2, "name": "Fiction"}, {"id": 4, "name": "History"}, ...].
       `many=True` tells DRF to iterate over the queryset and serialize each
       Category object individually.

    2. `is_owner` — this is NOT a real database column.  SerializerMethodField
       is a DRF escape-hatch that lets you add any computed value to the
       serialized output.  The paired `get_is_owner` method is called
       automatically for each object being serialized.
    """

    # Override the default categories field (which would output a list of IDs)
    # with the full CategorySerializer so the client gets category objects.
    # many=True is required whenever the relationship can return more than one item.
    categories = CategorySerializer(many=True)

    # Declare a computed, read-only field that is not stored in the database.
    # DRF looks for a method named get_<field_name> to populate it.
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        """Return True if the requesting user created this book.

        `self.context["request"]` is available because we pass
        context={"request": request} everywhere we instantiate this serializer.
        Without that, this line would raise a KeyError.
        """
        return self.context["request"].user == obj.user

    class Meta:
        model = Book
        # Field names here must match the actual attribute names on the Book
        # model (or be declared explicitly above, like `categories` and
        # `is_owner`).  A mismatch will raise ImproperlyConfigured at startup.
        fields = [
            "id",
            "title",
            "author",
            "isbn",           # matches Book.isbn (CharField, optional)
            "cover_image_url",  # matches Book.cover_image_url (URLField)
            "is_owner",
            "categories",
        ]


class BookViewSet(viewsets.ViewSet):
    """ViewSet for CRUD operations on the Book model.

    Each method maps to an HTTP verb + URL pattern wired up in urls.py via
    a DRF router:
        GET    /books/        → list
        POST   /books/        → create
        GET    /books/<pk>/   → retrieve
        PUT    /books/<pk>/   → update
        DELETE /books/<pk>/   → destroy
    """

    def list(self, request):
        """Return all books in the database.

        Passing context={"request": request} threads the current request
        through to BookSerializer so `get_is_owner` can compare the
        authenticated user against each book's owner.
        """
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Return a single book identified by its primary key (pk).

        The router extracts <pk> from the URL and passes it here as a string.
        `Book.objects.get(pk=pk)` converts it and hits the database.
        If no row exists, Django raises Book.DoesNotExist — we catch that and
        return a 404 rather than letting it bubble up as a 500.
        """
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book, context={"request": request})
            return Response(serializer.data)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """Create a new book and link it to one or more categories.

        Expected JSON payload shape:
        {
            "title":         "The Hobbit",
            "author":        "J.R.R. Tolkien",
            "isbn":          "9780618968633",   # optional
            "cover_image_url": "https://...",   # optional
            "categories":    [1, 3]             # array of Category primary keys
        }

        Why do we save the book FIRST, then handle categories?
        -------------------------------------------------------
        A ManyToManyField is stored in a separate join table (BookCategory).
        Every row in that table needs a book_id foreign key, so the book must
        already have a primary key before we can create those join rows.
        Calling `Book.objects.create(...)` performs an INSERT and Django
        immediately gives us back the new pk.

        How `.set()` handles the incoming ID array
        -------------------------------------------
        `book.categories.set(category_ids)` accepts a list of integer IDs,
        a list of Category objects, or a mix of both.  Internally Django:
          1. Queries which categories are *already* linked (none on a brand-new
             book).
          2. Adds any IDs in the new list that are not yet linked.
          3. Removes any currently-linked IDs that are absent from the new list.
        This makes `.set()` idempotent — safe to call with the full desired
        state rather than diffing manually.  On creation the list is simply
        inserted wholesale.
        """
        # --- 1. Extract scalar fields from the JSON body ---
        title = request.data.get("title")
        author = request.data.get("author")
        isbn = request.data.get("isbn")
        cover_image_url = request.data.get("cover_image_url")

        # --- 2. INSERT the book row to obtain a primary key ---
        book = Book.objects.create(
            user=request.user,
            title=title,
            author=author,
            cover_image_url=cover_image_url,
            isbn=isbn,
        )

        # --- 3. Link categories via the join table ---
        # request.data.get("categories", []) safely returns an empty list if
        # the client omitted the key, so we never pass None to .set().
        # The client sends an array of integer IDs, e.g. [1, 3].
        # Django resolves each ID against the Category table and creates the
        # corresponding BookCategory rows automatically.
        category_ids = request.data.get("categories", [])
        book.categories.set(category_ids)

        # --- 4. Serialize the fully-populated book and return it ---
        serializer = BookSerializer(book, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Replace all fields on an existing book (full update / HTTP PUT).

        Expected JSON payload shape is the same as create.

        Why not use BookSerializer(data=request.data).is_valid() here?
        ----------------------------------------------------------------
        BookSerializer's `categories` field is a *nested* CategorySerializer
        that expects full objects — {"id": 1, "name": "Fiction"} — not bare
        integers.  The client sends integers, so validation would fail for
        every request that includes categories.

        The recommended pattern when the write shape differs from the read
        shape is to extract fields manually (as in `create`) rather than
        running them through the read-serializer's validator.  A production
        app might define a separate write-only serializer, but manual
        extraction keeps things simple while we're learning.
        """
        try:
            book = Book.objects.get(pk=pk)

            # Confirm the authenticated user owns this book before allowing
            # modifications.  check_object_permissions raises PermissionDenied
            # (HTTP 403) if the permission check fails.
            self.check_object_permissions(request, book)

            # --- 1. Update scalar fields directly from the request payload ---
            book.title = request.data.get("title", book.title)
            book.author = request.data.get("author", book.author)
            book.isbn = request.data.get("isbn", book.isbn)
            book.cover_image_url = request.data.get("cover_image_url", book.cover_image_url)
            book.save()

            # --- 2. Replace the category relationships ---
            # .set() diffs the new list against the current join-table rows:
            #   • IDs in the new list that are missing → INSERT into BookCategory
            #   • IDs currently linked that are absent → DELETE from BookCategory
            #   • IDs present in both → no-op (no duplicate rows created)
            # Passing [] would remove ALL category links, which is valid for PUT.
            category_ids = request.data.get("categories", [])
            book.categories.set(category_ids)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Delete a book and its related join-table rows.

        The BookCategory rows are removed automatically because the Book model's
        ManyToManyField uses a `through` model that participates in Django's
        cascade delete behaviour.
        """
        try:
            book = Book.objects.get(pk=pk)
            self.check_object_permissions(request, book)
            book.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
