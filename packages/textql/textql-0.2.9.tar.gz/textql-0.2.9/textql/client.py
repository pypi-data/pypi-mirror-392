"""TextQL Client - Clean API wrapper around protocol buffers"""

from __future__ import annotations
from typing import Optional, Iterator
from dataclasses import dataclass, field
import grpc
from .platform import chat_pb2, chat_pb2_grpc
from .platform import connectors_pb2, connectors_pb2_grpc
from .platform import playbooks_pb2, playbooks_pb2_grpc
from .exceptions import handle_grpc_error


class _ClientCallDetails(
    grpc.ClientCallDetails,
):
    """Wrapper for client call details to modify method path"""

    def __init__(self, method, timeout, metadata, credentials, wait_for_ready, compression):
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression


class _PathPrefixInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
    """Interceptor to add /v1 prefix to gRPC method paths for ConnectRPC compatibility"""

    def __init__(self, prefix: str = "/v1"):
        self._prefix = prefix

    def intercept_unary_unary(self, continuation, client_call_details, request):
        new_details = self._update_path(client_call_details)
        return continuation(new_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        new_details = self._update_path(client_call_details)
        return continuation(new_details, request)

    def _update_path(self, client_call_details):
        new_method = self._prefix + client_call_details.method
        return _ClientCallDetails(
            new_method,
            client_call_details.timeout,
            client_call_details.metadata,
            client_call_details.credentials,
            client_call_details.wait_for_ready if hasattr(client_call_details, 'wait_for_ready') else None,
            client_call_details.compression if hasattr(client_call_details, 'compression') else None,
        )


@dataclass
class ChatTools:
    """Configuration for chat tools and capabilities

    Args:
        connector_ids: List of database connector IDs to enable
        web_search_enabled: Enable web search capability
        sql_enabled: Enable SQL query execution
        ontology_enabled: Enable ontology queries
        experimental_enabled: Enable experimental features
        tableau_enabled: Enable Tableau integration
        auto_approve_enabled: Auto-approve certain operations
        python_enabled: Enable Python code execution
        streamlit_enabled: Enable Streamlit apps
        google_drive_enabled: Enable Google Drive access
        powerbi_enabled: Enable PowerBI integration

    Example:
        >>> tools = ChatTools(
        ...     connector_ids=[513, 514],
        ...     web_search_enabled=True,
        ...     python_enabled=True
        ... )
    """
    connector_ids: list[int] = field(default_factory=list)
    web_search_enabled: bool = True
    sql_enabled: bool = True
    ontology_enabled: bool = False
    experimental_enabled: bool = False
    tableau_enabled: bool = False
    auto_approve_enabled: bool = False
    python_enabled: bool = True
    streamlit_enabled: bool = False
    google_drive_enabled: bool = False
    powerbi_enabled: bool = False

    def to_proto(self) -> chat_pb2.ChatTools:
        """Convert to protobuf message"""
        return chat_pb2.ChatTools(
            connector_ids=self.connector_ids,
            web_search_enabled=self.web_search_enabled,
            sql_enabled=self.sql_enabled,
            ontology_enabled=self.ontology_enabled,
            experimental_enabled=self.experimental_enabled,
            tableau_enabled=self.tableau_enabled,
            auto_approve_enabled=self.auto_approve_enabled,
            python_enabled=self.python_enabled,
            streamlit_enabled=self.streamlit_enabled,
            google_drive_enabled=self.google_drive_enabled,
            powerbi_enabled=self.powerbi_enabled,
        )


class ChatClient:
    """Client for TextQL chat operations"""

    def __init__(self, channel: grpc.Channel, api_key: str):
        self._stub = chat_pb2_grpc.ChatServiceStub(channel)
        self._api_key = api_key

    def stream(
        self,
        question: str,
        chat_id: Optional[str] = None,
        tools: Optional[ChatTools] = None,
    ) -> Iterator[chat_pb2.StreamResponse]:
        """
        Stream a chat conversation

        Args:
            question: The question to ask
            chat_id: Optional existing chat ID to continue
            tools: ChatTools configuration for enabling various capabilities

        Yields:
            Stream response chunks

        Example:
            tools = ChatTools(
                connector_ids=[513],
                web_search_enabled=True,
                sql_enabled=True,
                python_enabled=True
            )
            stream = client.chat.stream(
                question="Tell me about the connected datasource",
                chat_id="b165f422-3097-46e0-bf22-244c3efed9ff",
                tools=tools
            )
            for response in stream:
                if response.HasField('text'):
                    print(response.text, end='', flush=True)
        """
        request = chat_pb2.StreamRequest(
            question=question,
            chat_id=chat_id,
            tools=tools.to_proto() if tools else None,
        )

        metadata = [("authorization", f"Bearer {self._api_key}")]
        yield from self._stub.Stream(request, metadata=metadata)

    def chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        tools: Optional[ChatTools] = None,
    ) -> chat_pb2.ChatResponse:
        """
        Send a chat message (non-streaming)

        Args:
            question: The question to ask
            chat_id: Optional existing chat ID to continue
            tools: ChatTools configuration

        Returns:
            ChatResponse with the complete answer

        Example:
            tools = ChatTools(connector_ids=[513])
            response = client.chat.chat(
                question="What is the total revenue?",
                tools=tools
            )
            print(response.response)
        """
        request = chat_pb2.ChatRequest(
            question=question,
            chat_id=chat_id,
            tools=tools.to_proto() if tools else None,
        )

        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.Chat(request, metadata=metadata)

    def get(self, chat_id: str):
        """
        Get a chat by ID with full history and messages

        Args:
            chat_id: The ID of the chat to retrieve

        Returns:
            GetChatResponse with chat details, messages, and assets

        Example:
            response = client.chat.get("b165f422-3097-46e0-bf22-244c3efed9ff")
            print(f"Chat: {response.chat.id}")
            for message in response.messages:
                print(f"{message.role}: {message.content}")
        """
        # Import the public chat proto for GetChatRequest
        from .platform import chat_pb2 as platform_chat_pb2
        from .public import chat_pb2 as public_chat_pb2

        request = public_chat_pb2.GetChatRequest(chat_id=chat_id)
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.GetChat(request, metadata=metadata)

    def cancel(self, chat_id: str):
        """
        Cancel an ongoing chat stream

        Args:
            chat_id: The ID of the chat stream to cancel

        Returns:
            CancelStreamResponse indicating if the stream existed and was cancelled

        Example:
            response = client.chat.cancel("b165f422-3097-46e0-bf22-244c3efed9ff")
            if response.exists:
                print("Stream cancelled successfully")
            else:
                print("No active stream found")
        """
        from .public import chat_pb2 as public_chat_pb2

        request = public_chat_pb2.CancelStreamRequest(chat_id=chat_id)
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.CancelStream(request, metadata=metadata)


class ConnectorsClient:
    """Client for TextQL connector operations"""

    def __init__(self, channel: grpc.Channel, api_key: str):
        self._stub = connectors_pb2_grpc.ConnectorServiceStub(channel)
        self._api_key = api_key

    def list(self) -> connectors_pb2.ListConnectorsResponse:
        """
        List all connectors

        Returns:
            ListConnectorsResponse with all available connectors

        Example:
            connectors = client.connectors.list()
            for connector in connectors.connectors:
                print(f"{connector.id}: {connector.name}")
        """
        request = connectors_pb2.ListConnectorsRequest()
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.ListConnectors(request, metadata=metadata)


class PlaybooksClient:
    """Client for TextQL playbook operations"""

    def __init__(self, channel: grpc.Channel, api_key: str):
        self._stub = playbooks_pb2_grpc.PlaybookServiceStub(channel)
        self._api_key = api_key

    def create(self) -> playbooks_pb2.CreatePlaybookResponse:
        """
        Create a new playbook

        Returns:
            CreatePlaybookResponse with the created playbook

        Example:
            response = client.playbooks.create()
            print(f"Created playbook: {response.playbook.id}")
        """
        request = playbooks_pb2.CreatePlaybookRequest()
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.CreatePlaybook(request, metadata=metadata)

    def get(
        self,
        playbook_id: str,
        limit: int = 0,
        offset: int = 0,
    ) -> playbooks_pb2.GetPlaybookResponse:
        """
        Get a specific playbook with its reports

        Args:
            playbook_id: The ID of the playbook to retrieve
            limit: Maximum number of reports to return (default: 0 = all)
            offset: Number of reports to skip (default: 0)

        Returns:
            GetPlaybookResponse with playbook details and reports

        Example:
            response = client.playbooks.get("playbook-123", limit=10)
            print(f"Playbook: {response.playbook.name}")
            print(f"Reports: {len(response.reports)}")
        """
        request = playbooks_pb2.GetPlaybookRequest(
            playbook_id=playbook_id,
            limit=limit,
            offset=offset,
        )
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.GetPlaybook(request, metadata=metadata)

    def list(
        self,
        member_only: bool = False,
        limit: int = 0,
        offset: int = 0,
        search_term: Optional[str] = None,
        status_filter: Optional[int] = None,
        creator_member_id: Optional[str] = None,
        sort_by: int = 0,
        sort_direction: int = 0,
        subscribed_first: Optional[bool] = None,
    ) -> playbooks_pb2.ListPlaybooksResponse:
        """
        List playbooks with filtering and pagination

        Args:
            member_only: Only return playbooks for current member
            limit: Maximum number of playbooks to return (0-100, default: 0 = all)
            offset: Number of playbooks to skip (default: 0)
            search_term: Optional search term to filter playbooks
            status_filter: Optional status filter
            creator_member_id: Optional filter by creator
            sort_by: Sort field
            sort_direction: Sort direction
            subscribed_first: Show subscribed playbooks first

        Returns:
            ListPlaybooksResponse with playbooks and total count

        Example:
            response = client.playbooks.list(limit=10, search_term="revenue")
            for playbook in response.playbooks:
                print(f"{playbook.id}: {playbook.name}")
        """
        request = playbooks_pb2.ListPlaybooksRequest(
            member_only=member_only,
            limit=limit,
            offset=offset,
            search_term=search_term,
            status_filter=status_filter,
            creator_member_id=creator_member_id,
            sort_by=sort_by,
            sort_direction=sort_direction,
            subscribed_first=subscribed_first,
        )
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.ListPlaybooks(request, metadata=metadata)

    def update(
        self,
        playbook_id: str,
        name: Optional[str] = None,
        prompt: Optional[str] = None,
        status: Optional[int] = None,
        trigger_type: Optional[int] = None,
        cron_string: Optional[str] = None,
        dataset_ids: Optional[list[str]] = None,
        connector_id: Optional[int] = None,
        reference_report_id: Optional[str] = None,
        paradigm_options: Optional[any] = None,
        paradigm_type: Optional[int] = None,
        email_addresses: Optional[list[str]] = None,
        slack_channel_id: Optional[str] = None,
        tagged_slack_user_ids: Optional[list[str]] = None,
        report_output_style: Optional[int] = None,
        template_header_id: Optional[str] = None,
        selected_template_data_ids: Optional[list[str]] = None,
        max_concurrent_templates: Optional[int] = None,
        auto_optimize_concurrency: Optional[bool] = None,
        connector_ids: Optional[list[int]] = None,
    ) -> playbooks_pb2.UpdatePlaybookResponse:
        """
        Update a playbook (partial update - only provided fields are updated)

        Args:
            playbook_id: The ID of the playbook to update
            name: Optional new name
            prompt: Optional new prompt
            status: Optional new status
            trigger_type: Optional new trigger type
            cron_string: Optional cron schedule string
            dataset_ids: Optional list of dataset IDs
            connector_id: Optional connector ID
            reference_report_id: Optional reference report ID
            paradigm_options: Optional paradigm options
            paradigm_type: Optional paradigm type
            email_addresses: Optional list of email addresses
            slack_channel_id: Optional Slack channel ID
            tagged_slack_user_ids: Optional list of Slack user IDs
            report_output_style: Optional report output style
            template_header_id: Optional template header ID
            selected_template_data_ids: Optional list of template data IDs
            max_concurrent_templates: Optional max concurrent templates
            auto_optimize_concurrency: Optional auto-optimize concurrency flag
            connector_ids: Optional list of connector IDs

        Returns:
            UpdatePlaybookResponse with updated playbook

        Example:
            response = client.playbooks.update(
                playbook_id="playbook-123",
                name="Updated Name",
                prompt="New prompt"
            )
            print(f"Updated: {response.updated_fields}")
        """
        request = playbooks_pb2.UpdatePlaybookRequest(
            playbook_id=playbook_id,
            name=name,
            prompt=prompt,
            status=status,
            trigger_type=trigger_type,
            cron_string=cron_string,
            dataset_ids=dataset_ids or [],
            connector_id=connector_id,
            reference_report_id=reference_report_id,
            paradigm_options=paradigm_options,
            paradigm_type=paradigm_type,
            email_addresses=email_addresses or [],
            slack_channel_id=slack_channel_id,
            tagged_slack_user_ids=tagged_slack_user_ids or [],
            report_output_style=report_output_style,
            template_header_id=template_header_id,
            selected_template_data_ids=selected_template_data_ids or [],
            max_concurrent_templates=max_concurrent_templates,
            auto_optimize_concurrency=auto_optimize_concurrency,
            connector_ids=connector_ids or [],
        )
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.UpdatePlaybook(request, metadata=metadata)

    def deploy(self, playbook_id: str) -> playbooks_pb2.DeployPlaybookResponse:
        """
        Deploy a playbook

        Args:
            playbook_id: The ID of the playbook to deploy

        Returns:
            DeployPlaybookResponse with deployment info

        Example:
            response = client.playbooks.deploy("playbook-123")
            print(f"Deployed at: {response.deployed_at}")
        """
        request = playbooks_pb2.DeployPlaybookRequest(playbook_id=playbook_id)
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.DeployPlaybook(request, metadata=metadata)

    def delete(self, playbook_id: str) -> playbooks_pb2.DeletePlaybookResponse:
        """
        Delete a playbook

        Args:
            playbook_id: The ID of the playbook to delete

        Returns:
            DeletePlaybookResponse with deletion info

        Example:
            response = client.playbooks.delete("playbook-123")
            print(f"Deleted at: {response.deleted_at}")
        """
        request = playbooks_pb2.DeletePlaybookRequest(playbook_id=playbook_id)
        metadata = [("authorization", f"Bearer {self._api_key}")]
        return self._stub.DeletePlaybook(request, metadata=metadata)


class TextQLClient:
    """
    Main TextQL client

    Usage:
        from textql import TextQLClient, ChatTools

        client = TextQLClient(
            api_key='your-api-key',
            base_url='https://staging.textql.com'
        )

        # Stream a chat
        tools = ChatTools(
            connector_ids=[513],
            web_search_enabled=True,
            sql_enabled=True,
            python_enabled=True
        )

        stream = client.chat.stream(
            question="Tell me about the connected datasource",
            chat_id="b165f422-3097-46e0-bf22-244c3efed9ff",
            tools=tools
        )

        for response in stream:
            if response.HasField('text'):
                print(response.text, end='', flush=True)
            elif response.HasField('metadata'):
                print(f"\\nChat ID: {response.metadata.chat_id}")

        # List connectors
        connectors = client.connectors.list()
        for conn in connectors.connectors:
            print(f"{conn.id}: {conn.name}")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.textql.com",
        secure: bool = True,
    ):
        """
        Initialize TextQL client

        Args:
            api_key: Your TextQL API key (base64 encoded)
            base_url: Base URL for the API (default: https://api.textql.com)
            secure: Use secure channel (default: True)
        """
        self._api_key = api_key
        self._base_url = base_url.replace("https://", "").replace("http://", "")

        # Create interceptor for ConnectRPC path prefix
        interceptor = _PathPrefixInterceptor(prefix="/v1")

        if secure:
            base_channel = grpc.secure_channel(
                self._base_url, grpc.ssl_channel_credentials()
            )
        else:
            base_channel = grpc.insecure_channel(self._base_url)

        # Wrap channel with interceptor
        self._channel = grpc.intercept_channel(base_channel, interceptor)

        # Initialize service clients
        self.chat = ChatClient(self._channel, api_key)
        self.connectors = ConnectorsClient(self._channel, api_key)
        self.playbooks = PlaybooksClient(self._channel, api_key)

    def close(self):
        """Close the gRPC channel"""
        self._channel.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
