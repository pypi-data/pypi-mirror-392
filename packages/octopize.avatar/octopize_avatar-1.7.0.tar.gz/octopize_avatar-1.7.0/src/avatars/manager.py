import warnings
from uuid import UUID

from avatars import __version__
from avatars.client import ApiClient
from avatars.config import config
from avatars.models import CompatibilityStatus, JobWithDisplayNameResponse
from avatars.runner import Runner


class Manager:
    """High-level convenience facade for interacting with the Avatar API.

    The ``Manager`` wraps an authenticated :class:`avatars.client.ApiClient` instance
    and exposes a small, task‑oriented surface area so end users can:

    * authenticate once (``authenticate``) or use API key authentication
    * spin up a :class:`avatars.runner.Runner` (``create_runner`` / ``create_runner_from_yaml``)
    * quickly inspect recent jobs & results (``get_last_jobs`` / ``get_last_results``)
    * perform simple platform health checks (``get_health``)
    * handle password reset flows (``forgotten_password`` / ``reset_password``)

    It deliberately hides the lower-level resource clients (``jobs``, ``results``, ``datasets`` …)
    unless you access the underlying ``auth_client`` directly. This keeps common workflows
    succinct while preserving an escape hatch for advanced usage. The ``Runner`` objects created
    through the manager inherit the authenticated context, so you rarely have to pass tokens or
    low-level clients around manually.

    Attributes
    ----------
    auth_client:
        The underlying :class:`avatars.client.ApiClient` used to perform all HTTP requests.
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_client: ApiClient | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the manager with a base url.

        For on-premise deployment without dedicated SSL certificates, you can disable SSL
        verification:
        `manager = Manager(api_client=ApiClient(base_url=url, should_verify_ssl=False))`

        For API key authentication:
        `manager = Manager(base_url=url, api_key="your-api-key")`

        Args:
        -----
            base_url: The url of your actual server endpoint,
                e.g. base_url="https://avatar.company.co.
            api_client: Optional pre-configured ApiClient instance.
                Mutually exclusive with api_key.
            api_key: Optional API key for authentication using api-key-v1 scheme.
                When provided, authenticate() should not be called.
                Mutually exclusive with api_client.
        """
        # Mutual exclusivity check
        if api_client and api_key:
            raise ValueError(
                "Cannot provide both 'api_client' and 'api_key'. "
                "Either pass a pre-configured ApiClient or an api_key, not both."
            )

        if api_client:
            self.auth_client = api_client
        elif api_key:
            self.auth_client = ApiClient(base_url=base_url, api_key=api_key)
        else:
            self.auth_client = ApiClient(base_url=base_url)

    def authenticate(
        self, username: str, password: str, should_verify_compatibility: bool | None = None
    ) -> None:
        """Authenticate the user with the given username and password.

        Note: This method should not be called if the Manager was initialized with an api_key.
        API key authentication is already active and doesn't require calling authenticate().
        """
        # Guard against calling authenticate when API key is already set
        if hasattr(self.auth_client, "_api_key") and self.auth_client._api_key:
            raise ValueError(
                "Cannot call authenticate() when Manager was initialized with api_key. "
                "API key authentication is already active. "
                "To use username/password authentication, create a new Manager without api_key."
            )

        # If the caller didn't provide a value, consult the config; otherwise respect caller.
        if should_verify_compatibility is None:
            should_verify_compatibility = config.AVATAR_VERIFY_COMPATIBILITY

        if should_verify_compatibility:
            response = self.auth_client.compatibility.is_client_compatible()

            incompatible_statuses = [
                CompatibilityStatus.incompatible,
                CompatibilityStatus.unknown,
            ]
            if response.status in incompatible_statuses:
                compat_error_message = "Client is not compatible with the server.\n"
                compat_error_message += f"Server message: {response.message}.\n"
                compat_error_message += f"Client version: {__version__}.\n"

                compat_error_message += "Most recent compatible client version: "
                compat_error_message += f"{response.most_recent_compatible_client}.\n"

                compat_error_message += "To update your client, you can run "
                compat_error_message += "`pip install --upgrade octopize.avatar`.\n"

                compat_error_message += "To ignore, you can set "
                compat_error_message += (
                    "`authenticate(username, password, should_verify_compatibility=False)`."
                )
                warnings.warn(compat_error_message, DeprecationWarning)
                raise DeprecationWarning(compat_error_message)

        self.auth_client.authenticate(username, password)

    def forgotten_password(self, email: str) -> None:
        """Send a forgotten password email to the user."""
        self.auth_client.forgotten_password(email)

    def reset_password(
        self, email: str, new_password: str, new_password_repeated: str, token: str | UUID
    ) -> None:
        """Reset the password of the user."""
        if isinstance(token, str):
            token = UUID(token)
        self.auth_client.reset_password(email, new_password, new_password_repeated, token)

    def create_runner(self, set_name: str, seed: int | None = None) -> Runner:
        """Create a new runner."""
        return Runner(api_client=self.auth_client, display_name=set_name, seed=seed)

    def get_last_results(self, count: int = 1) -> list[dict[str, str]]:
        """Get the last n results."""
        all_jobs = self.auth_client.jobs.get_jobs().jobs

        last_jobs = all_jobs[-count:]
        results = []
        for job in last_jobs:
            result = self.auth_client.results.get_results(job.name)
            results.append(result)

        return results

    def get_last_jobs(self, count: int = 1) -> dict[str, JobWithDisplayNameResponse]:
        """Get the last n results."""
        all_jobs = self.auth_client.jobs.get_jobs().jobs

        last_jobs = all_jobs[-count:]
        results = {}
        for job in last_jobs:
            results[job.name] = job
        return results

    def get_health(self) -> dict[str, str]:
        """Get the health of the server."""
        return self.auth_client.health.get_health()

    def create_runner_from_yaml(self, yaml_path: str, set_name: str) -> Runner:
        """Create a new runner from a yaml file.
        Parameters
        ----------
            yaml_path: The path to the yaml file.
            set_name: Name of the set of resources.
        """
        runner = self.create_runner(set_name=set_name)
        runner.from_yaml(yaml_path)
        return runner
