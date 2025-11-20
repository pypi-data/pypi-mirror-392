import json
import logging
from dataclasses import dataclass, asdict, field
from functools import wraps
from typing import (
    Literal,
    Callable,
    Optional,
    List,
    Dict,
    Any,
    Type,
    Union,
)

from django.contrib import messages
from django.core.exceptions import (
    ImproperlyConfigured,
    PermissionDenied,
    ValidationError,
)
from django.core.paginator import InvalidPage, Paginator, Page
from django.db import transaction, IntegrityError, OperationalError
from django.db.models import Model, QuerySet
from django import forms
from django.forms import models as model_forms
from django.forms.forms import BaseForm
from django.http import (
    Http404,
    HttpResponseRedirect,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import URLPattern, path, reverse
from django.utils.decorators import classonlymethod
from django.utils.translation import gettext as _
from django.views.generic import View
from django_filters.filterset import filterset_factory, FilterSet

# Plugin system imports
from sundae.plugins.mixins import PluginMixin


class MultipleIntegersField(forms.TypedMultipleChoiceField):
    """
    A form field for multiple integers. Bypasses validation of values against the "choices" value.
    """

    def __init__(self, *args, **kwargs):
        super(MultipleIntegersField, self).__init__(*args, **kwargs)
        self.coerce = int

    def valid_value(self, value):
        return True


class BulkActionConfirmationForm(forms.Form):
    confirm = forms.BooleanField(
        required=True, initial=True, widget=forms.HiddenInput()
    )
    action = forms.CharField(required=True, widget=forms.HiddenInput())
    selected = MultipleIntegersField(
        required=True, widget=forms.MultipleHiddenInput(), coerce=int
    )


@dataclass
class HandlerConf:
    """
    Configuration for a view handler method.

    Attributes:
        handler: Name of the method to handle this HTTP method (e.g., 'show_list', 'process_create')
        template_name_suffix: Optional template suffix to use (e.g., '_list', '_form')
    """

    handler: str
    template_name_suffix: Optional[str] = None


@dataclass
class BulkActionResult:
    """
    Result of a bulk action execution.

    Attributes:
        success_count: Number of successfully processed items
        failure_count: Number of failed items
        total_count: Total number of items attempted
        errors: List of error messages for failures
        action_past_tense: Past tense description of action (e.g., "deleted", "archived")
    """

    success_count: int
    failure_count: int
    total_count: int
    errors: List[str] = field(default_factory=list)
    action_past_tense: str = "processed"

    @property
    def all_succeeded(self) -> bool:
        """Return True if all items succeeded."""
        return self.failure_count == 0 and self.success_count > 0

    @property
    def all_failed(self) -> bool:
        """Return True if all items failed."""
        return self.success_count == 0 and self.failure_count > 0

    @property
    def partial_success(self) -> bool:
        """Return True if some items succeeded and some failed."""
        return self.success_count > 0 and self.failure_count > 0


@dataclass
class BulkActionConfig:
    """
    Configuration for a registered bulk action.

    Attributes:
        name: Internal name of the action (method name)
        display_name: Human-readable name shown in UI
        handler: Reference to the handler method
        confirmation_required: Whether to show confirmation dialog
        permission_required: Permission(s) required for this action
        confirmation_template: Template to use for confirmation (if custom needed)
        use_transaction: If True, wraps action in database transaction with rollback
    """

    name: str
    display_name: str
    handler: Callable
    confirmation_required: bool = True
    permission_required: Optional[Union[str, List[str]]] = None
    confirmation_template: Optional[str] = None
    use_transaction: bool = False


ViewActionType = Literal[
    "detail",
    "create",
    "listing",
    "list_item",
    "bulk_edit_proxy",
    "bulk_edit",
    "single_item_extra",
    "list_item_extra",
]


@dataclass
class ViewActionConf:
    """
    Configuration for a view action (e.g., list, create, update, delete).

    Attributes:
        path: URL path pattern for this action (can include {verbose_name} placeholder)
        get: Handler configuration for GET requests
        post: Handler configuration for POST requests
        put: Handler configuration for PUT requests
        delete: Handler configuration for DELETE requests
        patch: Handler configuration for PATCH requests
        head: Handler configuration for HEAD requests
        options: Handler configuration for OPTIONS requests
        trace: Handler configuration for TRACE requests
        display_name: Human-readable name for the action (used in UI links)
        type: Type of action to determine UI rendering behavior
        permission_required: Optional permission(s) required for this action
        login_required: Whether login is required for this action
    """

    path: str
    get: Optional[HandlerConf] = None
    post: Optional[HandlerConf] = None
    put: Optional[HandlerConf] = None
    delete: Optional[HandlerConf] = None
    patch: Optional[HandlerConf] = None
    head: Optional[HandlerConf] = None
    options: Optional[HandlerConf] = None
    trace: Optional[HandlerConf] = None
    display_name: Optional[str] = None
    type: ViewActionType = "crud"
    permission_required: Optional[Union[str, List[str]]] = None
    login_required: bool = False


def action(
    detail: bool = False,
    url_path: Optional[str] = None,
    methods: Optional[List[str]] = None,
    display_name: Optional[str] = None,
    permission_required: Optional[Union[str, List[str]]] = None,
    login_required: bool = False,
) -> Callable:
    """
    Decorator to register a method as a custom action in a CRUDSundaeView.

    Inspired by Django admin's action decorator, this provides a simpler API
    for registering custom actions on models.

    Usage:
        # Detail action (operates on single object)
        @action(detail=True, url_path="approve")
        def approve_item(self, request, sqid):
            object = self.get_object()
            object.approved = True
            object.save()
            return HttpResponseRedirect(self.get_list_url())

        # List action (operates on list view)
        @action(detail=False, url_path="export")
        def export_list(self, request):
            # Export logic...
            return HttpResponse(csv_data, content_type='text/csv')

        # With permissions and multiple methods
        @action(
            detail=True,
            methods=["GET", "POST"],
            permission_required="myapp.approve_model",
            display_name="Approve Item"
        )
        def approve_item(self, request, sqid):
            # ... handle approval logic
            return HttpResponseRedirect(self.get_list_url())

    Args:
        detail: If True, action operates on individual objects (includes lookup field in URL).
                If False, action operates on list view. Default: False
        url_path: URL path segment (e.g., "approve" becomes "savedsearch/approve/").
                  If not provided, defaults to method name with underscores as hyphens.
        methods: List of HTTP methods (default: ["GET"])
        display_name: Human-readable name for the action (auto-generated if not provided)
        permission_required: Permission(s) required to access this action
        login_required: Whether login is required for this action

    Returns:
        Decorated method with action metadata attached
    """
    if methods is None:
        methods = ["GET"]

    def decorator(func: Callable) -> Callable:
        # Auto-generate url_path from function name if not provided
        func_url_path = url_path or func.__name__.replace("_", "-")

        # Auto-generate display_name from function name if not provided
        func_display_name = display_name or func.__name__.replace("_", " ").title()

        # Construct full path based on detail parameter
        if detail:
            # Detail action: operates on single object
            full_path = f"{{verbose_name}}/<slug:{{lookup_url_kwarg}}>/{func_url_path}/"
            action_type: ViewActionType = "single_item_extra"
        else:
            # List action: operates on list view
            full_path = f"{{verbose_name}}/{func_url_path}/"
            action_type = "list_item_extra"

        # Attach action metadata to the function
        func._sundae_action = True
        func._action_config = ViewActionConf(
            path=full_path,
            display_name=func_display_name,
            type=action_type,
            permission_required=permission_required,
            login_required=login_required,
        )

        # Configure handlers for each HTTP method
        for method in methods:
            method_lower = method.lower()
            handler_conf = HandlerConf(handler=func.__name__, template_name_suffix=None)
            setattr(func._action_config, method_lower, handler_conf)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def bulk_action(
    display_name: Optional[str] = None,
    permission_required: Optional[Union[str, List[str]]] = None,
    confirmation_required: bool = True,
    use_transaction: bool = False,
) -> Callable:
    """
    Decorator to register a method as a bulk action in a CRUDSundaeView.

    Bulk actions operate on multiple selected objects at once.

    Usage:
        @bulk_action(display_name="Archive Selected", confirmation_required=True)
        def archive_selected(self, request, queryset):
            # queryset contains the selected objects
            queryset.update(archived=True)
            return len(queryset), "archived"  # count, past tense action

        @bulk_action(display_name="Delete Selected", use_transaction=True)
        def delete_selected(self, request, queryset):
            # Wrapped in transaction - will rollback if any error occurs
            for obj in queryset:
                obj.delete()
            return len(queryset), "deleted"

    Args:
        display_name: Human-readable name for the bulk action
        permission_required: Permission(s) required for this bulk action
        confirmation_required: Whether to show confirmation dialog
        use_transaction: If True, wraps the action in a database transaction with
                        automatic rollback on failure. All items succeed or all fail.

    Returns:
        Decorated method with bulk action metadata
    """

    def decorator(func: Callable) -> Callable:
        # Attach bulk action metadata
        func._sundae_bulk_action = True
        func._bulk_action_name = func.__name__
        func._bulk_action_display = (
            display_name or func.__name__.replace("_", " ").title()
        )
        func._bulk_action_permission = permission_required
        func._bulk_action_confirmation = confirmation_required
        func._bulk_action_use_transaction = use_transaction

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


class CRUDSundaeView(PluginMixin, View):
    """
    A base view class for creating CRUD interfaces with minimal configuration.

    Inspired by Django's generic views and Neapolitan, this class provides:
    - Automatic URL generation with hyphen-separated naming (model-action)
    - Convention-based template resolution
    - Built-in CRUD operations (list, create, read, update, delete)
    - Django admin-style action registration with @action decorator
    - Bulk action support with @bulk_action decorator
    - Pagination and filtering
    - Comprehensive validation hooks and error handling
    - Plugin system for extending functionality

    Custom Actions:
        Use the @action decorator to register custom actions:

        @action(detail=True, url_path="approve")
        def approve_item(self, request, sqid):
            obj = self.get_object()
            obj.approved = True
            obj.save()
            return HttpResponseRedirect(self.get_list_url())

    Bulk Actions:
        Use the @bulk_action decorator for operations on multiple objects:

        @bulk_action(display_name="Archive Selected", use_transaction=True)
        def archive_selected(self, request, queryset):
            queryset.update(archived=True)
            return len(queryset), "archived"
    """

    # Model configuration
    model: Optional[Type[Model]] = None

    # Plugin configuration
    enable_plugins: bool = True
    skip_hooks: List[str] = []

    # Default view action configurations
    list_conf: ViewActionConf = ViewActionConf(
        path="{verbose_name}/", get=HandlerConf("show_list", "_list"), type="listing"
    )
    update_conf: ViewActionConf = ViewActionConf(
        path="{verbose_name}/<slug:{lookup_url_kwarg}>/update/",
        get=HandlerConf("show_update", "_form"),
        post=HandlerConf("process_update", "_form"),
        display_name="Edit",
        type="detail",
    )
    bulk_update_conf: ViewActionConf = ViewActionConf(
        path="{verbose_name}/bulk-update/",
        post=HandlerConf("show_bulk_update", "_bulk_form"),
        display_name="Bulk Edit",
        type="bulk_edit_proxy",
    )
    create_conf: ViewActionConf = ViewActionConf(
        path="{verbose_name}/create/",
        get=HandlerConf("show_create", "_form"),
        post=HandlerConf("process_create", "_form"),
        display_name="Add",
        type="create",
    )
    detail_conf: ViewActionConf = ViewActionConf(
        path="{verbose_name}/<slug:{lookup_url_kwarg}>/",
        get=HandlerConf("show_detail", "_detail"),
        display_name="View",
        type="detail",
    )
    delete_conf: ViewActionConf = ViewActionConf(
        path="{verbose_name}/<slug:{lookup_url_kwarg}>/delete/",
        get=HandlerConf("handle_delete", "_confirm_delete"),
        post=HandlerConf("process_delete", "_confirm_delete"),
        display_name="Delete",
        type="detail",
    )

    # Action configuration
    list_item_actions: List[str] = ["update", "delete", "detail"]
    bulk_edit_actions: List[str] = []
    excluded_actions: List[str] = []

    # Field configuration for different action types
    fields: Optional[List[str]] = None
    list_fields: Optional[List[str]] = None
    detail_fields: Optional[List[str]] = None
    update_fields: Optional[List[str]] = None
    create_fields: Optional[List[str]] = None

    # Object lookup configuration
    lookup_field: str = "sqid"
    lookup_url_kwarg: str = "sqid"
    object: Optional[Model] = None

    # Query and form configuration
    queryset: Optional[QuerySet] = None
    form_class: Optional[Type[BaseForm]] = None
    template_name: Optional[str] = None
    context_object_name: Optional[str] = None

    # Pagination configuration
    paginate_by: Optional[int] = 2
    page_kwarg: str = "page"
    allow_empty: bool = True

    # Template configuration
    template_name_suffix: Optional[str] = None
    widgets: Optional[Dict[str, Any]] = None

    # Filtering configuration
    filterset_class: Optional[Type[FilterSet]] = None

    # Success message configuration
    success_message_create: str = "{verbose_name} was created successfully."
    success_message_update: str = "{verbose_name} was updated successfully."
    success_message_delete: str = "{verbose_name} was deleted successfully."
    success_message_bulk_delete: str = (
        "{count} {verbose_name_plural} were deleted successfully."
    )
    enable_success_messages: bool = True

    # HTMX integration configuration
    enable_htmx_support: bool = True
    htmx_redirect_header: str = "HX-Redirect"
    htmx_refresh_header: str = "HX-Refresh"
    htmx_trigger_header: str = "HX-Trigger"

    # Permission and authentication configuration
    login_required: bool = False
    permission_required: Optional[Union[str, List[str]]] = None
    raise_exception: bool = False  # If True, raise PermissionDenied instead of redirect
    permission_denied_message: str = (
        "You do not have permission to perform this action."
    )

    # Per-action permissions (override global permissions for specific actions)
    create_permission_required: Optional[Union[str, List[str]]] = None
    update_permission_required: Optional[Union[str, List[str]]] = None
    delete_permission_required: Optional[Union[str, List[str]]] = None
    list_permission_required: Optional[Union[str, List[str]]] = None
    detail_permission_required: Optional[Union[str, List[str]]] = None

    # Django admin-style parameters (not yet fully implemented)
    list_display_links: List[str] = []
    list_filter: List[str] = []
    list_select_related: List[str] = []
    list_per_page: int = 100
    list_max_show_all: int = 200
    list_editable: List[str] = []
    search_fields: List[str] = []
    date_hierarchy: Optional[str] = None
    save_as: bool = False
    save_on_top: bool = False
    preserve_filters: bool = True
    view_on_site: bool = False
    actions: List[Callable] = []
    actions_on_top: bool = True
    actions_on_bottom: bool = False
    actions_selection_counter: bool = True
    show_full_result_count: bool = True
    ordering: List[str] = []
    empty_value_display: str = "-empty-"

    @classonlymethod
    def as_view(cls, view_action: str, **view_action_conf: Any) -> Callable:
        """
        Main entry point for a request-response process.

        Args:
            view_action: The name of the action being performed (e.g., 'list', 'create')
            **view_action_conf: Configuration dict for the view action

        Returns:
            A callable view function
        """

        # Validate handler configurations
        for key, val in view_action_conf.items():
            if key not in cls.http_method_names or val is None:
                continue
            handler_conf = val
            handler_name = handler_conf["handler"]
            if handler_name in cls.http_method_names:
                raise TypeError(
                    "The method name %s is not accepted as a keyword argument to %s()."
                    % (handler_name, cls.__name__)
                )
            if handler_name in [
                "list",
                "detail",
                "show_form",
                "process_form",
                "confirm_delete",
                "process_deletion",
            ]:
                raise TypeError(
                    "CRUDView handler name %s is not accepted as a keyword argument "
                    "to %s()." % (handler_name, cls.__name__)
                )
            if not hasattr(cls, handler_name):
                raise TypeError(
                    "%s() received an invalid keyword %r. as_view "
                    "only accepts arguments that are already "
                    "attributes of the class." % (cls.__name__, handler_name)
                )

        def view(request, *args, **kwargs):
            self = cls()
            self.setup(request, *args, **kwargs)
            if not hasattr(self, "request"):
                raise AttributeError(
                    f"{cls.__name__} instance has no 'request' attribute. Did you "
                    "override setup() and forget to call super()?"
                )

            # Set template_name_suffix if any HTTP method config has it
            # This is used for template resolution in render_to_response
            for method_name in cls.http_method_names:
                method_config = view_action_conf.get(method_name)
                if (
                    method_config
                    and isinstance(method_config, dict)
                    and method_config.get("template_name_suffix")
                ):
                    self.template_name_suffix = method_config["template_name_suffix"]
                    break  # Use the first one found

            for method, action in view_action_conf.items():
                if method not in cls.http_method_names or action is None:
                    continue
                # Ensure action is a dict before accessing it
                if not isinstance(action, dict):
                    continue
                handler = getattr(self, action["handler"])
                setattr(self, method, handler)

            fields = (
                view_action_conf.get("fields")
                or getattr(cls, f"{view_action}_fields", None)
                or getattr(cls, "fields", None)
                or [
                    i.name
                    for i in cls.model._meta.fields
                    if i.primary_key is False and i.editable is True
                ]
            )
            if view_action == "list":
                fields = (
                    view_action_conf.get("fields")
                    or getattr(cls, "list_display", None)
                    or getattr(cls, f"{view_action}_fields", None)
                    or getattr(cls, "fields", None)
                    or [
                        i.name for i in cls.model._meta.fields if i.primary_key is False
                    ]
                )

            if fields:
                setattr(self, "fields", fields)

            return self.dispatch(request, *args, **kwargs)

        view.view_class = cls
        view.view_initkwargs = {}

        # __name__ and __qualname__ are intentionally left unchanged as
        # view_class should be used to robustly determine the name of the view
        # instead.
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__annotations__ = cls.dispatch.__annotations__
        # Copy possible attributes set by decorators, e.g. @csrf_exempt, from
        # the dispatch method.
        view.__dict__.update(cls.dispatch.__dict__)

        # Mark the callback if the view class is async.
        # if cls.view_is_async:
        #     markcoroutinefunction(view)

        return view

    @classonlymethod
    def get_urls(cls) -> List[URLPattern]:
        """
        Generate URL patterns for all view actions.

        Auto-discovers methods decorated with @action and registers them as actions.

        Returns:
            List of Django URL patterns for this view's CRUD operations
        """
        # Start with default CRUD actions
        # NOTE: Order matters! Specific paths must come before generic paths with parameters
        view_actions: dict = {
            "list": asdict(cls.list_conf),
            "create": asdict(cls.create_conf),
            "bulk_update": asdict(
                cls.bulk_update_conf
            ),  # Must come before detail (has no path params)
            "detail": asdict(cls.detail_conf),  # Has <slug:sqid> which matches anything
            "update": asdict(cls.update_conf),
            "delete": asdict(cls.delete_conf),
        }

        # Auto-discover decorator-based actions
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "_sundae_action"):
                # Found a decorator-based action
                action_config = attr._action_config
                view_actions[attr_name] = asdict(action_config)

        # Filter out excluded actions
        view_actions = {
            k: v for k, v in view_actions.items() if k not in cls.excluded_actions
        }
        cls.view_actions = view_actions

        # Generate URL patterns with hyphen-separated names (model-action)
        verbose_name = cls.model._meta.model_name
        lookup_url_kwarg = cls.lookup_url_kwarg
        urlpatterns = []
        for view_action, view_action_conf in cls.view_actions.items():
            urlpatterns.append(
                path(
                    view_action_conf["path"].format(
                        verbose_name=verbose_name,
                        lookup_url_kwarg=lookup_url_kwarg
                    ),
                    cls.as_view(view_action, **view_action_conf),
                    name=f"{verbose_name}-{view_action}",
                ),
            )
        return urlpatterns

    # Filtering.

    def get_filterset(self, queryset: Optional[QuerySet] = None) -> Optional[FilterSet]:
        filterset_class = getattr(self, "filterset_class", None)
        filterset_fields = getattr(self, "filterset_fields", None)

        if filterset_class is None and filterset_fields:
            filterset_class = filterset_factory(self.model, fields=filterset_fields)

        if filterset_class is None:
            return None

        filtered = filterset_class(
            self.request.GET,
            queryset=queryset,
            request=self.request,
        )
        return filtered

    def get_search_queryset(self, queryset: QuerySet, search_term: str) -> QuerySet:
        """
        Filter queryset by search term across configured search_fields.

        Args:
            queryset: The queryset to filter
            search_term: The search term from user input

        Returns:
            Filtered queryset matching the search term
        """
        from django.db.models import Q

        if not search_term or not self.search_fields:
            return queryset

        # Build Q object for OR queries across all search fields
        query = Q()
        for field in self.search_fields:
            # Support field lookups (e.g., "name__icontains" → "name__icontains__icontains")
            # If field already has a lookup, use it; otherwise default to icontains
            if "__" in field:
                query |= Q(**{field: search_term})
            else:
                query |= Q(**{f"{field}__icontains": search_term})

        return queryset.filter(query)

    def get_active_filters(
        self, filterset: Optional[FilterSet]
    ) -> List[Dict[str, Any]]:
        """
        Extract active filter information for display in templates.

        Args:
            filterset: The FilterSet instance (or None)

        Returns:
            List of dicts with 'name', 'value', 'label', and 'display_value' keys
        """
        if filterset is None:
            return []

        active_filters = []
        for name, field in filterset.form.fields.items():
            # Check if this filter has a value in the request
            if name in filterset.data and filterset.data[name]:
                value = filterset.data[name]
                # Handle multiple values (e.g., checkboxes)
                if isinstance(value, list):
                    display_value = ", ".join(str(v) for v in value)
                else:
                    display_value = str(value)

                # Try to get choice label if it's a choice field
                if hasattr(field, "choices") and field.choices:
                    try:
                        choice_dict = dict(field.choices)
                        if value in choice_dict:
                            display_value = choice_dict[value]
                    except (TypeError, ValueError):
                        pass

                active_filters.append({
                    "name": name,
                    "value": value,
                    "label": field.label or name.replace("_", " ").title(),
                    "display_value": display_value,
                })

        return active_filters

    def get_filter_querystring(self, exclude_page: bool = True) -> str:
        """
        Build query string preserving filter and search parameters.

        Args:
            exclude_page: If True, exclude the 'page' parameter

        Returns:
            Query string for use in pagination URLs
        """
        from django.http import QueryDict

        params = QueryDict(mutable=True)
        for key, value in self.request.GET.items():
            if exclude_page and key == self.page_kwarg:
                continue
            params[key] = value

        return params.urlencode()

    # Success messages

    def add_success_message(self, message: str, **kwargs: Any) -> None:
        """
        Add a success message to the request.

        Args:
            message: Message template string with {placeholders}
            **kwargs: Additional context for message formatting
        """
        if not self.enable_success_messages:
            return

        context = {
            "verbose_name": self.model._meta.verbose_name,
            "verbose_name_plural": self.model._meta.verbose_name_plural,
            **kwargs,
        }
        formatted_message = message.format(**context)
        messages.success(self.request, formatted_message)

    def get_success_message(self, action: str) -> str:
        """
        Get the success message template for an action.

        Args:
            action: The action name ('create', 'update', 'delete', etc.)

        Returns:
            Message template string
        """
        return getattr(self, f"success_message_{action}", "")

    # HTMX integration helpers

    def is_htmx_request(self) -> bool:
        """
        Check if the current request is an HTMX request.

        Returns:
            True if request has HX-Request header
        """
        return self.request.headers.get("HX-Request") == "true"

    def htmx_redirect(self, url: str) -> Dict[str, str]:
        """
        Create HTMX redirect headers.

        Args:
            url: URL to redirect to

        Returns:
            Dict of headers for client-side redirect
        """
        if not self.enable_htmx_support:
            return {}
        return {self.htmx_redirect_header: url}

    def htmx_refresh(self) -> Dict[str, str]:
        """
        Create HTMX refresh headers to reload the page.

        Returns:
            Dict of headers for client-side refresh
        """
        if not self.enable_htmx_support:
            return {}
        return {self.htmx_refresh_header: "true"}

    def htmx_trigger(
        self, event_name: str, details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Create HTMX trigger headers to fire client-side events.

        Args:
            event_name: Name of the event to trigger
            details: Optional event details as dict

        Returns:
            Dict of headers with HX-Trigger
        """
        if not self.enable_htmx_support:
            return {}

        if details:
            trigger_value = json.dumps({event_name: details})
        else:
            trigger_value = event_name

        return {self.htmx_trigger_header: trigger_value}

    # Logging integration

    @property
    def logger(self) -> logging.Logger:
        """
        Get a logger instance for this view.

        Returns:
            Logger instance named after the view's module and class
        """
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(
                f"{self.__module__}.{self.__class__.__name__}"
            )
        return self._logger

    def get_user_friendly_error_message(self, exception: Exception) -> str:
        """
        Convert database and validation exceptions to user-friendly messages.

        Args:
            exception: The exception that was raised

        Returns:
            User-friendly error message string
        """
        if isinstance(exception, IntegrityError):
            error_str = str(exception).lower()
            if "unique" in error_str or "duplicate" in error_str:
                return "This item already exists or conflicts with existing data."
            elif (
                "foreign key" in error_str
                or "violates foreign key constraint" in error_str
            ):
                return "Cannot complete this action due to related data constraints."
            elif "not null" in error_str or "violates not-null constraint" in error_str:
                return (
                    "Required information is missing. Please check all required fields."
                )
            else:
                return "This operation conflicts with existing data."

        elif isinstance(exception, OperationalError):
            error_str = str(exception).lower()
            if "timeout" in error_str or "timed out" in error_str:
                return "The database operation timed out. Please try again."
            elif "lock" in error_str:
                return (
                    "The resource is currently locked by another operation. Please try"
                    " again."
                )
            else:
                return "A database error occurred. Please try again."

        elif isinstance(exception, ValidationError):
            # Django ValidationError can have different formats
            if hasattr(exception, "message_dict"):
                # Field-specific errors
                errors = []
                for field, messages in exception.message_dict.items():
                    field_label = field.replace("_", " ").title()
                    errors.append(f"{field_label}: {', '.join(messages)}")
                return " | ".join(errors)
            elif hasattr(exception, "messages"):
                # List of error messages
                return " | ".join(exception.messages)
            else:
                return str(exception)

        elif isinstance(exception, PermissionDenied):
            return (
                str(exception)
                if str(exception)
                else "You do not have permission to perform this action."
            )

        else:
            # Generic fallback
            return f"An error occurred: {str(exception)}"

    # Permission and authentication

    def get_permission_required(self, action: Optional[str] = None) -> List[str]:
        """
        Get the permissions required for a specific action or the view.

        Args:
            action: The action name ('create', 'update', 'delete', etc.)

        Returns:
            List of permission strings required
        """
        # Check for per-action permissions first
        if action:
            action_perms = getattr(self, f"{action}_permission_required", None)
            if action_perms:
                if isinstance(action_perms, str):
                    return [action_perms]
                return list(action_perms)

        # Fall back to global permission_required
        if self.permission_required:
            if isinstance(self.permission_required, str):
                return [self.permission_required]
            return list(self.permission_required)

        return []

    def has_permission(self) -> bool:
        """
        Check if the current user has permission to access this view.

        Override this method to implement custom permission logic.

        Returns:
            True if user has permission, False otherwise
        """
        # Check login requirement
        if self.login_required and not self.request.user.is_authenticated:
            return False

        # Check permissions
        perms = self.get_permission_required()
        if perms:
            return self.request.user.has_perms(perms)

        return True

    def handle_no_permission(self) -> HttpResponse:
        """
        Handle the case when a user doesn't have permission.

        Returns:
            HTTP response for permission denied case
        """
        if self.raise_exception:
            raise PermissionDenied(self.permission_denied_message)

        # Redirect to login if user is not authenticated
        if not self.request.user.is_authenticated:
            from django.conf import settings
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(
                self.request.get_full_path(),
                settings.LOGIN_URL,
            )

        # Otherwise raise PermissionDenied
        raise PermissionDenied(self.permission_denied_message)

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Handle request dispatching with permission checks.

        Args:
            request: The HTTP request
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HTTP response

        Raises:
            PermissionDenied: If user doesn't have permission and raise_exception is True
        """
        # Check permissions before dispatching
        if not self.has_permission():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    # Save hooks for extending behavior

    def before_create(self, form: BaseForm) -> None:
        """
        Hook called before creating an object.

        Override this to add custom logic before object creation.

        Args:
            form: The valid form instance
        """
        pass

    def after_create(self, obj: Model) -> None:
        """
        Hook called after creating an object.

        Override this to add custom logic after object creation
        (e.g., logging, notifications, related object updates).

        Args:
            obj: The newly created model instance
        """
        pass

    def before_update(self, form: BaseForm) -> None:
        """
        Hook called before updating an object.

        Override this to add custom logic before object update.

        Args:
            form: The valid form instance
        """
        pass

    def after_update(self, obj: Model) -> None:
        """
        Hook called after updating an object.

        Override this to add custom logic after object update
        (e.g., logging, notifications, cache invalidation).

        Args:
            obj: The updated model instance
        """
        pass

    def before_delete(self, obj: Model) -> None:
        """
        Hook called before deleting an object.

        Override this to add custom logic before object deletion
        (e.g., archiving, logging).

        Args:
            obj: The model instance about to be deleted
        """
        pass

    def after_delete(self, obj_id: Any) -> None:
        """
        Hook called after deleting an object.

        Override this to add custom logic after object deletion
        (e.g., cleanup, notifications).

        Args:
            obj_id: The ID of the deleted object
        """
        pass

    # New unified validation and save hooks

    def clean_object(self, obj: Model) -> None:
        """
        Hook for custom object validation before saving.

        Called before save for both create and update operations.
        Use this to validate the object state before persisting to database.
        Raise ValidationError if validation fails.

        Note: This hook is NOT called for bulk actions - only for single-object
        create/update operations.

        Args:
            obj: The model instance about to be saved

        Raises:
            ValidationError: If validation fails

        Example:
            def clean_object(self, obj):
                if obj.start_date > obj.end_date:
                    raise ValidationError("Start date must be before end date")
        """
        pass

    def before_save(self, form: BaseForm) -> None:
        """
        Unified hook called before saving an object (create or update).

        This hook is called for both create and update operations, after form
        validation but before the object is saved to the database. It's called
        in addition to before_create/before_update hooks.

        Use this for logic that should run for both create and update operations.

        Args:
            form: The valid form instance (has .instance attribute)

        Example:
            def before_save(self, form):
                # Set modified_by for both create and update
                form.instance.modified_by = self.request.user
        """
        pass

    def after_save(self, obj: Model, created: bool) -> None:
        """
        Unified hook called after saving an object (create or update).

        This hook is called for both create and update operations, after the
        object has been saved to the database. It's called in addition to
        after_create/after_update hooks.

        Use this for logic that should run for both create and update operations.

        Args:
            obj: The saved model instance
            created: True if object was created, False if it was updated

        Example:
            def after_save(self, obj, created):
                action = "created" if created else "updated"
                self.logger.info(f"{obj} was {action} by {self.request.user}")
        """
        pass

    # Queryset and object lookup

    def get_object(self) -> Model:
        """
        Returns the object the view is displaying.

        Returns:
            The model instance for this view

        Raises:
            Http404: If the object doesn't exist
            ImproperlyConfigured: If lookup parameters are not properly configured
        """
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        try:
            lookup = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        except KeyError:
            msg = "Lookup field '%s' was not provided in view kwargs to '%s'"
            raise ImproperlyConfigured(
                msg % (lookup_url_kwarg, self.__class__.__name__)
            )

        return get_object_or_404(queryset, **lookup)

    def get_queryset(self) -> QuerySet:
        """
        Returns the base queryset for the view.

        Either used as a list of objects to display, or as the queryset
        from which to perform the individual object lookup.

        Returns:
            QuerySet of model instances

        Raises:
            ImproperlyConfigured: If neither queryset nor model is defined
        """
        if self.queryset is not None:
            return self.queryset._clone()

        if self.model is not None:
            return self.model._default_manager.all()

        msg = (
            "'%s' must either define 'queryset' or 'model', or override "
            + "'get_queryset()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    # Form instantiation

    def get_form_class(self) -> Type[BaseForm]:
        """
        Returns the form class to use in this view.

        Returns:
            Form class to instantiate

        Raises:
            ImproperlyConfigured: If form_class, model, and fields are not properly configured
        """
        if self.form_class is not None:
            # Allow plugins to filter the form class
            return self.filter_hook('filter_form_class', self.form_class)

        if self.model is not None and self.fields is not None:
            # Get initial widgets (either from view attribute or empty dict)
            widgets = self.widgets.copy() if self.widgets else {}

            # Allow plugins to customize widgets
            widgets = self.filter_hook('filter_form_widgets', widgets)

            return model_forms.modelform_factory(
                self.model, fields=self.fields, widgets=widgets
            )

        msg = (
            "'%s' must either define 'form_class' or both 'model' and "
            "'fields', or override 'get_form_class()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_form(
        self,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> BaseForm:
        """
        Returns a form instance.

        Args:
            data: POST data for the form
            files: Uploaded files for the form
            **kwargs: Additional kwargs to pass to the form constructor

        Returns:
            Instantiated form
        """
        cls = self.get_form_class()
        return cls(data=data, files=files, **kwargs)

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        Called when a valid form is submitted.

        This method is deprecated in favor of using process_create/process_update
        which have proper hook support. Kept for backwards compatibility.

        Args:
            form: The validated form instance

        Returns:
            HTTP response redirecting to success URL
        """
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form: BaseForm) -> TemplateResponse:
        """
        Called when an invalid form is submitted.

        Args:
            form: The invalid form instance with errors

        Returns:
            Template response with form errors
        """
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    # Pagination

    def get_paginate_by(self) -> Optional[int]:
        """
        Returns the size of pages to use with pagination.

        Returns:
            Page size or None if pagination is disabled
        """
        return self.paginate_by

    def get_paginator(self, queryset: QuerySet, page_size: int) -> Paginator:
        """
        Returns a paginator instance.

        Args:
            queryset: The queryset to paginate
            page_size: Number of items per page

        Returns:
            Paginator instance
        """
        return Paginator(queryset, page_size)

    def paginate_queryset(self, queryset: QuerySet, page_size: int) -> Page:
        """
        Paginates a queryset, and returns a page object.

        Args:
            queryset: The queryset to paginate
            page_size: Number of items per page

        Returns:
            Page object with the requested page of results

        Raises:
            Http404: If the requested page is invalid
        """
        paginator = self.get_paginator(queryset, page_size)
        page_kwarg = self.kwargs.get(self.page_kwarg)
        page_query_param = self.request.GET.get(self.page_kwarg)
        page_number = page_kwarg or page_query_param or 1
        try:
            page_number = int(page_number)
        except ValueError:
            if page_number == "last":
                page_number = paginator.num_pages
            else:
                msg = "Page is not 'last', nor can it be converted to an int."
                raise Http404(_(msg))

        try:
            return paginator.page(page_number)
        except InvalidPage as exc:
            msg = "Invalid page (%s): %s"
            raise Http404(_(msg) % (page_number, str(exc)))

    # Response rendering

    def get_context_object_name(self, is_list: bool = False) -> Optional[str]:
        """
        Returns a descriptive name to use in the context in addition to the
        default 'object'/'object_list'.

        Args:
            is_list: Whether this is for a list view or detail view

        Returns:
            Context variable name or None
        """
        if self.context_object_name is not None:
            return self.context_object_name

        elif self.model is not None:
            fmt = "%s_list" if is_list else "%s"
            return fmt % self.model._meta.object_name.lower()

        return None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Returns a dictionary to use as the context of the response.

        Takes a set of keyword arguments to use as the base context,
        and adds the following keys:

        * ``view``: A reference to the view object itself.
        * The ``object_verbose_name`` and ``object_verbose_name_plural`` of the
          model.
        * ``object`` or ``object_list``: The object or list of objects being
          displayed, plus more user-friendly versions using the model, such as
          ``bookmark`` or ``bookmark_list``.
        * ``create_view_url``: The URL of the create view
        * ``list_view_url``: The URL of the list view

        Args:
            **kwargs: Base context dictionary

        Returns:
            Complete context dictionary for template rendering
        """
        kwargs["view"] = self
        kwargs["object_verbose_name"] = self.model._meta.verbose_name
        kwargs["object_verbose_name_plural"] = self.model._meta.verbose_name_plural
        kwargs["create_view_url"] = reverse(f"{self.model._meta.model_name}-create")
        kwargs["list_view_url"] = reverse(f"{self.model._meta.model_name}-list")

        if getattr(self, "object", None) is not None:
            kwargs["object"] = self.object
            context_object_name = self.get_context_object_name()
            if context_object_name:
                kwargs[context_object_name] = self.object

        if getattr(self, "object_list", None) is not None:
            kwargs["object_list"] = self.object_list
            context_object_name = self.get_context_object_name(is_list=True)
            if context_object_name:
                kwargs[context_object_name] = self.object_list

        # Allow plugins to filter context (especially for list views)
        kwargs = self.filter_hook('filter_context', kwargs)

        # Allow plugins to filter list context specifically
        if getattr(self, "object_list", None) is not None:
            kwargs = self.filter_hook('filter_list_context', kwargs)

        return kwargs

    def get_template_names(self) -> List[str]:
        """
        Returns a list of template names to use when rendering the response.

        If `.template_name` is not specified, uses the
        "{app_label}/{model_name}{template_name_suffix}.html" model template
        pattern, with the fallback to the
        "sundae/object{template_name_suffix}.html" default templates.

        Returns:
            List of template names to try in order

        Raises:
            ImproperlyConfigured: If template name cannot be determined
        """
        if self.template_name is not None:
            return [self.template_name]

        if self.model is not None and self.template_name_suffix is not None:
            return [
                (
                    f"{self.model._meta.app_label}/"
                    f"{self.model._meta.object_name.lower()}"
                    f"{self.template_name_suffix}.html"
                ),
                f"sundae/object{self.template_name_suffix}.html",
            ]
        msg = (
            "'%s' must either define 'template_name' or 'model' and "
            "'template_name_suffix', or override 'get_template_names()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_success_url(self) -> str:
        """
        Get the URL to redirect to after successful form submission.

        Returns:
            URL string

        Raises:
            AssertionError: If model is not defined
        """
        assert self.model is not None, (
            "'%s' must define 'model' or override 'get_success_url()'"
            % self.__class__.__name__
        )
        success_url = reverse(f"{self.model._meta.model_name}-list")
        return success_url

    def get_list_url(self) -> str:
        """
        Get the URL for the list view.

        Returns:
            URL string

        Raises:
            AssertionError: If model is not defined
        """
        assert self.model is not None, (
            "'%s' must define 'model' or override 'get_list_url()'"
            % self.__class__.__name__
        )
        success_url = reverse(f"{self.model._meta.model_name}-list")
        return success_url

    def get_bulk_action_registry(self) -> Dict[str, BulkActionConfig]:
        """
        Build registry of all available bulk actions by discovering decorated methods.

        Returns:
            Dict mapping action names to their BulkActionConfig
        """
        registry: Dict[str, BulkActionConfig] = {}

        # Auto-discover methods decorated with @bulk_action
        # We need to check the class methods, not instance methods, for the decorator attributes
        for attr_name in dir(self.__class__):
            # Get the unbound function from the class
            class_attr = getattr(self.__class__, attr_name, None)
            if class_attr is None:
                continue

            # Check if it has the bulk action marker
            if callable(class_attr) and hasattr(class_attr, "_sundae_bulk_action"):
                # Get the bound method from the instance for the handler
                bound_method = getattr(self, attr_name)

                config = BulkActionConfig(
                    name=class_attr._bulk_action_name,
                    display_name=class_attr._bulk_action_display,
                    handler=bound_method,  # Use bound method so it has access to self
                    confirmation_required=class_attr._bulk_action_confirmation,
                    permission_required=class_attr._bulk_action_permission,
                    use_transaction=getattr(
                        class_attr, "_bulk_action_use_transaction", False
                    ),
                )
                registry[class_attr._bulk_action_name] = config

        return registry

    def get_bulk_action_config(self, action_name: str) -> Optional[BulkActionConfig]:
        """
        Get the configuration for a specific bulk action.

        Args:
            action_name: Name of the bulk action

        Returns:
            BulkActionConfig if found, None otherwise
        """
        registry = self.get_bulk_action_registry()
        return registry.get(action_name)

    def execute_bulk_action(
        self,
        action_name: str,
        selected_ids: List[int],
        request: HttpRequest,
    ) -> BulkActionResult:
        """
        Execute a bulk action on selected objects.

        If the action is configured with use_transaction=True, the handler will be
        wrapped in a database transaction with automatic rollback on failure. This
        ensures all items succeed or all items fail together.

        Args:
            action_name: Name of the bulk action to execute
            selected_ids: List of object IDs to process
            request: The HTTP request

        Returns:
            BulkActionResult with success/failure counts and messages

        Raises:
            ValueError: If action is not found or invalid
        """
        config = self.get_bulk_action_config(action_name)
        if not config:
            raise ValueError(f"Bulk action '{action_name}' not found")

        # Check permissions
        if config.permission_required:
            perms = (
                config.permission_required
                if isinstance(config.permission_required, list)
                else [config.permission_required]
            )
            if not request.user.has_perms(perms):
                raise PermissionDenied(
                    f"You do not have permission to perform '{config.display_name}'"
                )

        # Get queryset of selected objects
        queryset = self.get_queryset().filter(pk__in=selected_ids)
        total_count = len(selected_ids)
        actual_count = queryset.count()

        # Log bulk action start
        self.logger.info(
            f"Starting bulk action '{action_name}' on"
            f" {total_count} {self.model._meta.verbose_name_plural} by user"
            f" {request.user}"
        )

        # Execute the handler (with transaction if configured)
        try:
            if config.use_transaction:
                # Wrap in transaction with automatic rollback on exception
                with transaction.atomic():
                    result = config.handler(request, queryset)
            else:
                # Execute without transaction (partial success possible)
                result = config.handler(request, queryset)

            # Handler can return different formats:
            # 1. BulkActionResult object (preferred)
            # 2. Tuple of (count, action_past_tense)
            # 3. Just count
            if isinstance(result, BulkActionResult):
                # Log completion
                self.logger.info(
                    f"Bulk action '{action_name}' completed:"
                    f" {result.success_count} succeeded, {result.failure_count} failed"
                )
                return result
            elif isinstance(result, tuple) and len(result) == 2:
                count, action_past_tense = result
                self.logger.info(
                    f"Bulk action '{action_name}' completed: {count} items"
                    f" {action_past_tense}"
                )
                return BulkActionResult(
                    success_count=count,
                    failure_count=total_count - count,
                    total_count=total_count,
                    action_past_tense=action_past_tense,
                )
            elif isinstance(result, int):
                self.logger.info(
                    f"Bulk action '{action_name}' completed: {result} items processed"
                )
                return BulkActionResult(
                    success_count=result,
                    failure_count=total_count - result,
                    total_count=total_count,
                    action_past_tense=action_name.replace("_", " "),
                )
            else:
                # Default: assume all succeeded
                self.logger.info(
                    f"Bulk action '{action_name}' completed: {actual_count} items"
                    " processed"
                )
                return BulkActionResult(
                    success_count=actual_count,
                    failure_count=total_count - actual_count,
                    total_count=total_count,
                    action_past_tense=action_name.replace("_", " "),
                )

        except IntegrityError as e:
            # Database integrity error (with helpful message)
            error_msg = self.get_user_friendly_error_message(e)
            self.logger.exception(
                f"IntegrityError in bulk action '{action_name}': {str(e)}"
            )
            return BulkActionResult(
                success_count=0,
                failure_count=total_count,
                total_count=total_count,
                errors=[error_msg],
                action_past_tense=action_name.replace("_", " "),
            )

        except OperationalError as e:
            # Database operational error
            error_msg = self.get_user_friendly_error_message(e)
            self.logger.exception(
                f"OperationalError in bulk action '{action_name}': {str(e)}"
            )
            return BulkActionResult(
                success_count=0,
                failure_count=total_count,
                total_count=total_count,
                errors=[error_msg],
                action_past_tense=action_name.replace("_", " "),
            )

        except PermissionDenied as e:
            # Permission error (re-raise to be handled by caller)
            self.logger.warning(
                f"Permission denied in bulk action '{action_name}' for user"
                f" {request.user}: {str(e)}"
            )
            raise

        except Exception as e:
            # Any other error
            error_msg = self.get_user_friendly_error_message(e)
            self.logger.exception(
                f"Unexpected error in bulk action '{action_name}': {str(e)}"
            )
            return BulkActionResult(
                success_count=0,
                failure_count=total_count,
                total_count=total_count,
                errors=[error_msg],
                action_past_tense=action_name.replace("_", " "),
            )

    def get_bulk_actions(self) -> List[Dict[str, str]]:
        """
        Get list of bulk actions available for this view.

        This method discovers bulk actions from both:
        1. Decorator-based bulk actions (@bulk_action)
        2. Legacy view_actions with type="bulk_edit"

        Returns:
            List of dicts with action id, url, and display_name
        """
        actions: List[Dict[str, str]] = []
        model_name = self.model._meta.model_name

        # Get decorator-based bulk actions
        registry = self.get_bulk_action_registry()
        for action_name, config in registry.items():
            # Check if this action is enabled in bulk_edit_actions
            if not self.bulk_edit_actions or action_name in self.bulk_edit_actions:
                actions.append({
                    "id": action_name,
                    "url": reverse(f"{model_name}-bulk_update"),
                    "display_name": config.display_name,
                })

        # Also support legacy view_actions with type="bulk_edit"
        for k, v in self.view_actions.items():
            if v["type"] == "bulk_edit" and k in self.bulk_edit_actions:
                # Only add if not already in registry
                if not any(a["id"] == k for a in actions):
                    actions.append({
                        "id": k,
                        "url": reverse(f"{model_name}-{k}"),
                        "display_name": f"{v['display_name'] or k}",
                    })

        return actions

    def get_actions(self, object: Optional[Model] = None) -> List[Dict[str, str]]:
        """
        Get list of actions available for an object or the list view.

        Args:
            object: Model instance to get actions for, or None for list actions

        Returns:
            List of dicts with action id, url, and display_name
        """
        actions: List[Dict[str, str]] = []
        model_name = self.model._meta.model_name

        for view_action in self.list_item_actions:
            view_action_conf = self.view_actions[view_action]
            if view_action == "list":
                actions.append({
                    "id": view_action,
                    "url": reverse(f"{model_name}-{view_action}"),
                    "display_name": (
                        f"{view_action_conf['display_name'] or view_action}"
                    ),
                })
            if object is not None and view_action != "list":
                actions.append({
                    "id": view_action,
                    "url": reverse(
                        f"{model_name}-{view_action}",
                        kwargs={
                            self.lookup_url_kwarg
                            or "pk": getattr(object, self.lookup_field)
                        },
                    ),
                    "display_name": (
                        f"{view_action_conf['display_name'] or view_action}"
                    ),
                })
        return actions

    def render_to_response(
        self, context: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> TemplateResponse:
        """
        Given a context dictionary, returns an HTTP response.

        Args:
            context: Template context dictionary
            headers: Optional HTTP headers to include in response

        Returns:
            TemplateResponse for rendering
        """
        return TemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            headers=headers,
        )

    def show_list(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> TemplateResponse:
        queryset = self.get_queryset()

        # Apply search filtering if search term present
        search_term = request.GET.get("q", "").strip()
        if search_term:
            queryset = self.get_search_queryset(queryset, search_term)

        # Apply filterset filtering
        filterset = self.get_filterset(queryset)
        if filterset is not None:
            queryset = filterset.qs

        if not self.allow_empty and not queryset.exists():
            raise Http404

        paginate_by = self.get_paginate_by()
        if paginate_by is None:
            # Unpaginated response
            self.object_list = queryset
            context = self.get_context_data(
                page_obj=None,
                is_paginated=False,
                paginator=None,
                filterset=filterset,
                search_term=search_term,
                active_filters=self.get_active_filters(filterset),
                filter_querystring=self.get_filter_querystring(),
            )
        else:
            # Paginated response
            page = self.paginate_queryset(queryset, paginate_by)
            self.object_list = page.object_list
            context = self.get_context_data(
                page_obj=page,
                is_paginated=page.has_other_pages(),
                paginator=page.paginator,
                filterset=filterset,
                search_term=search_term,
                active_filters=self.get_active_filters(filterset),
                filter_querystring=self.get_filter_querystring(),
            )

        # Support HTMX partial rendering
        # If HTMX request, return partial template with HX-Push-Url header
        if hasattr(request, "htmx") and request.htmx:
            # Build URL with current query parameters for history
            from django.http import QueryDict

            query_params = QueryDict(mutable=True)
            query_params.update(request.GET)
            push_url = (
                f"{request.path}?{query_params.urlencode()}"
                if query_params
                else request.path
            )

            response = self.render_to_response(context)
            response["HX-Push-Url"] = push_url
            return response

        return self.render_to_response(context)

    def process_update_list(self, request: HttpRequest) -> TemplateResponse:
        """Legacy method for updating list view."""
        return TemplateResponse(
            request,
            "search/saved_search_list.html",
            {
                "saved_searches": self.model.objects.all(),
            },
        )

    def show_detail(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> TemplateResponse:
        """Display a single object detail view."""
        self.object = self.get_object()

        # Transform object into iterable of (field_name, field_value) tuples for template
        fields_to_display = (
            self.detail_fields or
            self.fields or
            [f.name for f in self.model._meta.fields if f.editable]
        )

        object_fields = []
        for field_name in fields_to_display:
            try:
                field = self.model._meta.get_field(field_name)
                value = getattr(self.object, field_name)
                # Get display value for choice fields
                if hasattr(field, 'choices') and field.choices:
                    display_method = f'get_{field_name}_display'
                    if hasattr(self.object, display_method):
                        value = getattr(self.object, display_method)()
                object_fields.append((field.verbose_name or field_name, value))
            except Exception:
                # Skip fields that don't exist or can't be accessed
                continue

        context = self.get_context_data()
        # Store field tuples in context for the template to iterate over
        context['object_fields'] = object_fields
        return self.render_to_response(context)

    def show_create(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> TemplateResponse:
        """Display the create form."""
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def process_create(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[HttpResponse, TemplateResponse]:
        """
        Process create form submission with hooks and success messages.

        Hook execution order:
        1. Form validation
        2. clean_object() - Custom object validation
        3. before_save() - Unified pre-save hook
        4. before_create() - Create-specific pre-save hook
        5. form.save() - Database save
        6. after_create() - Create-specific post-save hook
        7. after_save(created=True) - Unified post-save hook
        8. Success message and redirect

        Error handling:
        - Form validation errors: logged and returned via form_invalid()
        - Database errors: caught, logged, user-friendly message added
        - Permission errors: caught, logged, user-friendly message added
        """
        form = self.get_form(
            data=request.POST,
            files=request.FILES,
            instance=self.object,
        )

        if form.is_valid():
            try:
                # Call clean_object validation hook
                self.clean_object(form.instance)

                # Call unified before_save hook
                self.before_save(form)

                # Call before_create hook
                self.before_create(form)

                # Save the object
                self.object = form.save()

                # Call after_create hook
                self.after_create(self.object)

                # Call unified after_save hook
                self.after_save(self.object, created=True)

                # Add success message
                self.add_success_message(self.get_success_message("create"))

                # Log successful creation
                self.logger.info(
                    f"Created {self.model._meta.verbose_name} (ID: {self.object.pk}) by"
                    f" user {request.user}"
                )

                # Handle HTMX requests
                if self.is_htmx_request():
                    headers = self.htmx_redirect(self.get_success_url())
                    return HttpResponse(status=204, headers=headers)

                return HttpResponseRedirect(self.get_success_url())

            except ValidationError as e:
                # Handle validation errors from clean_object()
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.warning(
                    f"Validation error creating {self.model._meta.verbose_name}:"
                    f" {str(e)}"
                )
                # Add errors to form for display
                if hasattr(e, "message_dict"):
                    for field, errors in e.message_dict.items():
                        form.add_error(field, errors)
                elif hasattr(e, "message"):
                    form.add_error(None, e.message)
                else:
                    form.add_error(None, str(e))
                return self.form_invalid(form)

            except IntegrityError as e:
                # Handle database integrity errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.exception(
                    f"IntegrityError creating {self.model._meta.verbose_name}: {str(e)}"
                )
                form.add_error(None, error_msg)
                return self.form_invalid(form)

            except OperationalError as e:
                # Handle database operational errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.exception(
                    f"OperationalError creating {self.model._meta.verbose_name}:"
                    f" {str(e)}"
                )
                form.add_error(None, error_msg)
                return self.form_invalid(form)

            except PermissionDenied as e:
                # Handle permission errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.warning(
                    f"Permission denied creating {self.model._meta.verbose_name} for"
                    f" user {request.user}: {str(e)}"
                )
                return self.form_invalid(form)

            except Exception as e:
                # Handle any other unexpected errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.exception(
                    f"Unexpected error creating {self.model._meta.verbose_name}:"
                    f" {str(e)}"
                )
                form.add_error(None, f"An unexpected error occurred: {str(e)}")
                return self.form_invalid(form)
        else:
            # Log form validation errors
            self.logger.warning(
                f"Form validation failed for {self.model._meta.verbose_name} create:"
                f" {form.errors.as_json()}"
            )

        return self.form_invalid(form)

    def show_update(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> TemplateResponse:
        """Display the update form for an object."""
        self.object = self.get_object()
        form = self.get_form(instance=self.object)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def process_update(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[HttpResponse, TemplateResponse]:
        """
        Process update form submission with hooks and success messages.

        Hook execution order:
        1. Fetch existing object
        2. Form validation
        3. clean_object() - Custom object validation
        4. before_save() - Unified pre-save hook
        5. before_update() - Update-specific pre-save hook
        6. form.save() - Database save
        7. after_update() - Update-specific post-save hook
        8. after_save(created=False) - Unified post-save hook
        9. Success message and redirect

        Error handling:
        - Form validation errors: logged and returned via form_invalid()
        - Database errors: caught, logged, user-friendly message added
        - Permission errors: caught, logged, user-friendly message added
        """
        self.object = self.get_object()
        form = self.get_form(
            data=request.POST,
            files=request.FILES,
            instance=self.object,
        )

        if form.is_valid():
            try:
                # Call clean_object validation hook
                self.clean_object(form.instance)

                # Call unified before_save hook
                self.before_save(form)

                # Call before_update hook
                self.before_update(form)

                # Save the object
                self.object = form.save()

                # Call after_update hook
                self.after_update(self.object)

                # Call unified after_save hook
                self.after_save(self.object, created=False)

                # Add success message
                self.add_success_message(self.get_success_message("update"))

                # Log successful update
                self.logger.info(
                    f"Updated {self.model._meta.verbose_name} (ID: {self.object.pk}) by"
                    f" user {request.user}"
                )

                # Handle HTMX requests
                if self.is_htmx_request():
                    headers = self.htmx_redirect(self.get_success_url())
                    return HttpResponse(status=204, headers=headers)

                return HttpResponseRedirect(self.get_success_url())

            except ValidationError as e:
                # Handle validation errors from clean_object()
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.warning(
                    f"Validation error updating {self.model._meta.verbose_name} (ID:"
                    f" {self.object.pk}): {str(e)}"
                )
                # Add errors to form for display
                if hasattr(e, "message_dict"):
                    for field, errors in e.message_dict.items():
                        form.add_error(field, errors)
                elif hasattr(e, "message"):
                    form.add_error(None, e.message)
                else:
                    form.add_error(None, str(e))
                return self.form_invalid(form)

            except IntegrityError as e:
                # Handle database integrity errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.exception(
                    f"IntegrityError updating {self.model._meta.verbose_name} (ID:"
                    f" {self.object.pk}): {str(e)}"
                )
                form.add_error(None, error_msg)
                return self.form_invalid(form)

            except OperationalError as e:
                # Handle database operational errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.exception(
                    f"OperationalError updating {self.model._meta.verbose_name} (ID:"
                    f" {self.object.pk}): {str(e)}"
                )
                form.add_error(None, error_msg)
                return self.form_invalid(form)

            except PermissionDenied as e:
                # Handle permission errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.warning(
                    f"Permission denied updating {self.model._meta.verbose_name} (ID:"
                    f" {self.object.pk}) for user {request.user}: {str(e)}"
                )
                return self.form_invalid(form)

            except Exception as e:
                # Handle any other unexpected errors
                error_msg = self.get_user_friendly_error_message(e)
                messages.error(request, error_msg)
                self.logger.exception(
                    f"Unexpected error updating {self.model._meta.verbose_name} (ID:"
                    f" {self.object.pk}): {str(e)}"
                )
                form.add_error(None, f"An unexpected error occurred: {str(e)}")
                return self.form_invalid(form)
        else:
            # Log form validation errors
            self.logger.warning(
                f"Form validation failed for {self.model._meta.verbose_name} update"
                f" (ID: {self.object.pk}): {form.errors.as_json()}"
            )

        return self.form_invalid(form)

    def show_bulk_update(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[HttpResponse, TemplateResponse]:
        """
        Handle bulk actions with improved registry-based dispatch.

        This method handles the bulk action workflow:
        1. Validate request and selection
        2. Check if confirmation is needed
        3. Show confirmation page (if needed and not confirmed)
        4. Execute action
        5. Handle results and show appropriate messages
        """
        if request.method != "POST":
            return HttpResponseRedirect(self.get_list_url())

        action_name = request.POST.get("action")
        selected_ids = request.POST.getlist("selected")
        is_confirmed = request.POST.get("confirm") == "1"

        # Handle cancel action
        if action_name == "cancel" or not action_name:
            return HttpResponseRedirect(self.get_list_url())

        # Validate selection
        if not selected_ids:
            messages.warning(request, "No items selected.")
            return HttpResponseRedirect(self.get_list_url())

        # Convert selected IDs to integers, filter out invalid ones
        try:
            selected_ids = [int(id) for id in selected_ids if id != "undefined"]
        except ValueError:
            messages.error(request, "Invalid selection.")
            return HttpResponseRedirect(self.get_list_url())

        if not selected_ids:
            messages.warning(request, "No valid items selected.")
            return HttpResponseRedirect(self.get_list_url())

        # Try to get bulk action config from registry
        config = self.get_bulk_action_config(action_name)

        # If not in registry, try legacy process_{action} method
        if not config:
            method = getattr(self, f"process_{action_name}", None)
            if method is None:
                messages.error(request, f"Unknown action: {action_name}")
                return HttpResponseRedirect(self.get_list_url())
            # Legacy method - just call it
            return method(request, *args, **kwargs)

        # Check if confirmation is required and not yet confirmed
        if config.confirmation_required and not is_confirmed:
            return self.show_bulk_action_confirmation(
                request, action_name, config, selected_ids
            )

        # Execute the bulk action
        try:
            result = self.execute_bulk_action(action_name, selected_ids, request)

            # Add appropriate success/error messages based on result
            if result.all_succeeded:
                messages.success(
                    request,
                    f"Successfully {result.action_past_tense} {result.success_count} "
                    f"{self.model._meta.verbose_name_plural}.",
                )
            elif result.all_failed:
                error_msg = f"Failed to {result.action_past_tense} any items."
                if result.errors:
                    error_msg += f" Errors: {', '.join(result.errors)}"
                messages.error(request, error_msg)
            elif result.partial_success:
                messages.warning(
                    request,
                    f"Partially completed: {result.success_count} succeeded, "
                    f"{result.failure_count} failed.",
                )
                if result.errors:
                    for error in result.errors[:5]:  # Show first 5 errors
                        messages.error(request, error)

        except PermissionDenied as e:
            messages.error(request, str(e))
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        # Handle HTMX requests
        if self.is_htmx_request():
            headers = self.htmx_refresh()
            return HttpResponse(status=204, headers=headers)

        return HttpResponseRedirect(self.get_success_url())

    def show_bulk_action_confirmation(
        self,
        request: HttpRequest,
        action_name: str,
        config: BulkActionConfig,
        selected_ids: List[int],
    ) -> TemplateResponse:
        """
        Show confirmation page for a bulk action.

        Args:
            request: The HTTP request
            action_name: Name of the bulk action
            config: Configuration for the bulk action
            selected_ids: List of selected object IDs

        Returns:
            TemplateResponse with confirmation page
        """
        # Get queryset to show preview if needed
        queryset = self.get_queryset().filter(pk__in=selected_ids)
        count = queryset.count()

        context = {
            "action_name": action_name,
            "action_display_name": config.display_name,
            "selected_ids": selected_ids,
            "count": count,
            "objects": queryset[:10],  # Show first 10 for preview
            "verbose_name": self.model._meta.verbose_name,
            "verbose_name_plural": self.model._meta.verbose_name_plural,
            "object_verbose_name": self.model._meta.model_name,  # For URL reversal
        }

        # Use custom template if specified, otherwise use default
        template_name = (
            config.confirmation_template or "sundae/object_bulk_action_confirm.html"
        )

        return TemplateResponse(
            request=request,
            template=template_name,
            context=context,
        )

    def process_bulk_update(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[HttpResponse, TemplateResponse]:
        """Process bulk update form submission."""
        context: Dict[str, Any] = {}
        form = self.get_form(
            data=request.POST,
            files=request.FILES,
            instance=self.object,
        )
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def handle_delete(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> TemplateResponse:
        """Display delete confirmation page."""
        self.object = self.get_object()
        context = self.get_context_data()
        return self.render_to_response(context)

    def process_delete(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """
        Process object deletion with hooks, error handling, and success messages.

        Hook execution order:
        1. Fetch existing object
        2. before_delete() - Pre-deletion hook
        3. object.delete() - Database deletion
        4. after_delete(obj_id) - Post-deletion hook
        5. Success message and redirect

        Error handling:
        - Database errors: caught, logged, user-friendly message added
        - Permission errors: caught, logged, user-friendly message added
        - Related object constraint errors: caught, logged, user-friendly message added
        """
        self.object = self.get_object()
        obj_id = self.object.pk
        obj_repr = str(self.object)

        try:
            # Call before_delete hook
            self.before_delete(self.object)

            # Delete the object
            self.object.delete()

            # Call after_delete hook
            self.after_delete(obj_id)

            # Add success message
            self.add_success_message(self.get_success_message("delete"))

            # Log successful deletion
            self.logger.info(
                f"Deleted {self.model._meta.verbose_name} '{obj_repr}' (ID: {obj_id})"
                f" by user {request.user}"
            )

            # Handle HTMX requests
            if self.is_htmx_request():
                headers = self.htmx_redirect(self.get_success_url())
                return HttpResponse(status=204, headers=headers)

            return HttpResponseRedirect(self.get_success_url())

        except IntegrityError as e:
            # Handle foreign key constraint errors (related objects exist)
            error_msg = self.get_user_friendly_error_message(e)
            messages.error(request, error_msg)
            self.logger.exception(
                f"IntegrityError deleting {self.model._meta.verbose_name} (ID:"
                f" {obj_id}): {str(e)}"
            )
            # Redirect back to detail or list page
            return HttpResponseRedirect(self.get_success_url())

        except OperationalError as e:
            # Handle database operational errors
            error_msg = self.get_user_friendly_error_message(e)
            messages.error(request, error_msg)
            self.logger.exception(
                f"OperationalError deleting {self.model._meta.verbose_name} (ID:"
                f" {obj_id}): {str(e)}"
            )
            return HttpResponseRedirect(self.get_success_url())

        except PermissionDenied as e:
            # Handle permission errors
            error_msg = self.get_user_friendly_error_message(e)
            messages.error(request, error_msg)
            self.logger.warning(
                f"Permission denied deleting {self.model._meta.verbose_name} (ID:"
                f" {obj_id}) for user {request.user}: {str(e)}"
            )
            return HttpResponseRedirect(self.get_success_url())

        except Exception as e:
            # Handle any other unexpected errors
            error_msg = self.get_user_friendly_error_message(e)
            messages.error(request, error_msg)
            self.logger.exception(
                f"Unexpected error deleting {self.model._meta.verbose_name} (ID:"
                f" {obj_id}): {str(e)}"
            )
            return HttpResponseRedirect(self.get_success_url())

    def process_delete_selected(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[HttpResponse, TemplateResponse]:
        """
        Process bulk deletion with success messages.

        Deletes multiple objects and shows a success message with count.
        """
        bulk_form = BulkActionConfirmationForm(request.POST)
        context = self.get_context_data()
        context["form"] = bulk_form

        if not bulk_form.is_valid():
            return self.render_to_response(context)

        selected = bulk_form.cleaned_data["selected"]
        action = bulk_form.cleaned_data["action"]
        confirm = bulk_form.cleaned_data["confirm"]

        if selected and action == "delete_selected" and confirm:
            queryset = self.get_queryset().filter(pk__in=selected)
            count = queryset.count()
            queryset.delete()

            # Add success message with count
            self.add_success_message(
                self.get_success_message("bulk_delete"), count=count
            )

            # Handle HTMX requests
            if self.is_htmx_request():
                headers = self.htmx_refresh()
                return HttpResponse(status=204, headers=headers)

            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(context)
