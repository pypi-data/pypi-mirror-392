"""
Tests for CRUDSundaeView search and filter functionality.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django_filters import FilterSet, CharFilter
from search.models import SavedSearch
from search.views.admin_search import SaveSearchSundaeView


User = get_user_model()


class TestSearchFunctionality(TestCase):
    """Test search functionality in CRUDSundaeView."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create test SavedSearch objects with different names
        self.search1 = SavedSearch.objects.create(
            name="Charter Greece",
            search_type="public",
            description="Greek islands charter search"
        )
        self.search2 = SavedSearch.objects.create(
            name="Croatia Sailing",
            search_type="broker",
            description="Croatia yacht search"
        )
        self.search3 = SavedSearch.objects.create(
            name="Mediterranean Adventure",
            search_type="public",
            description="Mediterranean routes"
        )

    def test_search_queryset_filters_by_term(self):
        """Test that get_search_queryset filters results."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/")
        view.search_fields = ["name", "description"]

        queryset = SavedSearch.objects.all()

        # Search for "Greece"
        filtered = view.get_search_queryset(queryset, "Greece")
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.search1, filtered)

        # Search for "Croatia"
        filtered = view.get_search_queryset(queryset, "Croatia")
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.search2, filtered)

        # Search for "Mediterranean" (in description)
        filtered = view.get_search_queryset(queryset, "Mediterranean")
        self.assertEqual(filtered.count(), 1)
        self.assertIn(self.search3, filtered)

    def test_search_queryset_case_insensitive(self):
        """Test that search is case-insensitive."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/")
        view.search_fields = ["name"]

        queryset = SavedSearch.objects.all()

        # Search with different cases
        filtered_lower = view.get_search_queryset(queryset, "greece")
        filtered_upper = view.get_search_queryset(queryset, "GREECE")
        filtered_mixed = view.get_search_queryset(queryset, "GrEeCe")

        self.assertEqual(filtered_lower.count(), 1)
        self.assertEqual(filtered_upper.count(), 1)
        self.assertEqual(filtered_mixed.count(), 1)

    def test_search_queryset_or_logic(self):
        """Test that search uses OR logic across fields."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/")
        view.search_fields = ["name", "description"]

        queryset = SavedSearch.objects.all()

        # "Sailing" appears in name of search2
        filtered = view.get_search_queryset(queryset, "Sailing")
        self.assertIn(self.search2, filtered)

    def test_search_queryset_empty_term(self):
        """Test that empty search term returns unfiltered queryset."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/")
        view.search_fields = ["name"]

        queryset = SavedSearch.objects.all()

        # Empty string
        filtered = view.get_search_queryset(queryset, "")
        self.assertEqual(filtered.count(), queryset.count())

        # Whitespace only
        filtered = view.get_search_queryset(queryset, "   ")
        self.assertEqual(filtered.count(), 0)  # Empty after strip

    def test_search_queryset_no_search_fields(self):
        """Test that no search_fields returns unfiltered queryset."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/")
        view.search_fields = []

        queryset = SavedSearch.objects.all()
        filtered = view.get_search_queryset(queryset, "Greece")
        self.assertEqual(filtered.count(), queryset.count())


class TestFilterFunctionality(TestCase):
    """Test filter functionality in CRUDSundaeView."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create test SavedSearch objects
        self.search1 = SavedSearch.objects.create(
            name="Public Search 1",
            search_type="public"
        )
        self.search2 = SavedSearch.objects.create(
            name="Broker Search 1",
            search_type="broker"
        )
        self.search3 = SavedSearch.objects.create(
            name="Public Search 2",
            search_type="public"
        )

    def test_get_active_filters_extracts_filters(self):
        """Test that get_active_filters extracts filter information."""
        view = SaveSearchSundaeView()
        request = self.factory.get("/?search_type=public&name=test")
        view.request = request

        queryset = SavedSearch.objects.all()
        filterset = view.get_filterset(queryset)

        active_filters = view.get_active_filters(filterset)

        # Should have filters for search_type and name if they're in the FilterSet
        self.assertIsInstance(active_filters, list)

    def test_get_active_filters_returns_empty_for_none(self):
        """Test that get_active_filters handles None filterset."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/")

        active_filters = view.get_active_filters(None)
        self.assertEqual(active_filters, [])

    def test_get_filter_querystring_preserves_params(self):
        """Test that get_filter_querystring preserves filter params."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/?search_type=public&name=test&page=2")

        querystring = view.get_filter_querystring(exclude_page=True)

        # Should preserve search_type and name but exclude page
        self.assertIn("search_type=public", querystring)
        self.assertIn("name=test", querystring)
        self.assertNotIn("page=", querystring)

    def test_get_filter_querystring_includes_page(self):
        """Test that get_filter_querystring can include page param."""
        view = SaveSearchSundaeView()
        view.request = self.factory.get("/?search_type=public&page=2")

        querystring = view.get_filter_querystring(exclude_page=False)

        # Should include page when exclude_page=False
        self.assertIn("page=2", querystring)


class TestIntegratedSearchAndFilter(TestCase):
    """Test integrated search and filter in show_list."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )

        # Create test data
        self.search1 = SavedSearch.objects.create(
            name="Greece Charter",
            search_type="public"
        )
        self.search2 = SavedSearch.objects.create(
            name="Greece Sailing",
            search_type="broker"
        )
        self.search3 = SavedSearch.objects.create(
            name="Croatia Charter",
            search_type="public"
        )

    def test_show_list_applies_search(self):
        """Test that show_list applies search term."""
        view = SaveSearchSundaeView()
        request = self.factory.get("/?q=Greece")
        request.user = self.user
        view.request = request
        view.kwargs = {}  # Initialize kwargs
        view.template_name_suffix = "_list"  # Required for template rendering
        view.search_fields = ["name"]

        response = view.show_list(request)

        # Should have 2 results (both Greece searches)
        self.assertEqual(len(response.context_data["object_list"]), 2)

    def test_show_list_passes_context_variables(self):
        """Test that show_list passes filter context to template."""
        view = SaveSearchSundaeView()
        request = self.factory.get("/?q=Greece&search_type=public")
        request.user = self.user
        view.request = request
        view.kwargs = {}  # Initialize kwargs
        view.template_name_suffix = "_list"  # Required for template rendering
        view.search_fields = ["name"]

        response = view.show_list(request)

        # Check context variables
        self.assertIn("search_term", response.context_data)
        self.assertEqual(response.context_data["search_term"], "Greece")
        self.assertIn("filterset", response.context_data)
        self.assertIn("active_filters", response.context_data)
        self.assertIn("filter_querystring", response.context_data)

    def test_show_list_htmx_adds_push_url_header(self):
        """Test that HTMX requests add HX-Push-Url header."""
        view = SaveSearchSundaeView()
        request = self.factory.get("/?q=Greece")
        request.user = self.user
        request.htmx = True  # Simulate HTMX request
        view.request = request
        view.kwargs = {}  # Initialize kwargs
        view.template_name_suffix = "_list"  # Required for template rendering
        view.search_fields = ["name"]

        response = view.show_list(request)

        # Should have HX-Push-Url header
        self.assertIn("HX-Push-Url", response)


class TestFilterSetIntegration(TestCase):
    """Test integration with django-filter FilterSet."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create test data
        SavedSearch.objects.create(name="Test 1", search_type="public")
        SavedSearch.objects.create(name="Test 2", search_type="broker")
        SavedSearch.objects.create(name="Test 3", search_type="public")

    def test_filterset_filters_queryset(self):
        """Test that filterset properly filters queryset."""
        view = SaveSearchSundaeView()
        request = self.factory.get("/")
        request.user = self.user
        view.request = request

        queryset = view.get_queryset()
        filterset = view.get_filterset(queryset)

        # Check that filterset was created
        self.assertIsNotNone(filterset)
        # Check that it has a queryset
        self.assertIsNotNone(filterset.qs)

    def test_search_and_filter_combined(self):
        """Test that search and filter work together."""
        # Clear existing data to avoid interference
        SavedSearch.objects.all().delete()

        # Create specific test data
        SavedSearch.objects.create(name="Greece Public", search_type="public")
        SavedSearch.objects.create(name="Greece Broker", search_type="broker")

        view = SaveSearchSundaeView()
        request = self.factory.get("/?q=Greece")
        request.user = self.user
        view.request = request
        view.kwargs = {}  # Initialize kwargs
        view.template_name_suffix = "_list"  # Required for template rendering
        view.search_fields = ["name"]

        response = view.show_list(request)

        # Should have 2 results (both Greece searches)
        self.assertEqual(len(response.context_data["object_list"]), 2)


@pytest.mark.e2e
class TestSearchFilterE2E(TestCase):
    """End-to-end tests for search and filter UI."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )

        # Create test data
        SavedSearch.objects.create(name="Greece Charter", search_type="public")
        SavedSearch.objects.create(name="Croatia Sailing", search_type="broker")

    def test_search_form_submission(self):
        """Test search form submission via GET."""
        self.client.login(username="admin", password="adminpass123")

        response = self.client.get(reverse("savedsearch-list"), {"q": "Greece"})

        self.assertEqual(response.status_code, 200)
        # Should have search term in context
        self.assertEqual(response.context["search_term"], "Greece")

    def test_filter_form_submission(self):
        """Test filter form submission via GET."""
        self.client.login(username="admin", password="adminpass123")

        response = self.client.get(
            reverse("savedsearch-list"),
            {"search_type": "public"}
        )

        self.assertEqual(response.status_code, 200)
        # Should have filterset in context
        self.assertIsNotNone(response.context.get("filterset"))

    def test_pagination_preserves_filters(self):
        """Test that pagination links preserve filter params."""
        self.client.login(username="admin", password="adminpass123")

        # Create many searches to trigger pagination
        for i in range(150):
            SavedSearch.objects.create(
                name=f"Test Search {i}",
                search_type="public"
            )

        response = self.client.get(
            reverse("savedsearch-list"),
            {"q": "Test", "page": 1}
        )

        self.assertEqual(response.status_code, 200)
        # Check that filter_querystring is in context
        self.assertIn("filter_querystring", response.context)
        self.assertIn("q=Test", response.context["filter_querystring"])
