
from KeycloakFastAPI.Dependencies import ProtectedRole
from SharedInterfaces.DataStoreAPI import *
from fastapi import APIRouter, Depends
from config import get_settings, Config
from dependencies.dependencies import read_write_user_protected_role_dependency, email_dependency
from helpers.registry_api_helpers import *
from helpers.release_helpers import get_all_reviewers, perform_action_of_approval_request, perform_approval_request
from helpers.auth_helpers import get_user_link
from interfaces.EmailClient import EmailClient

router = APIRouter()


@router.get("/sys-reviewers/list", operation_id="list_reviewers")
async def list_reviewers(
    protected_roles: ProtectedRole = Depends(
        read_write_user_protected_role_dependency),
    config: Config = Depends(get_settings)
) -> Set[IdentifiedResource]:
    """
    List all of the system's dataset reviewers
    """
    # TODO output model.
    return get_all_reviewers(config)


@router.post("/approval-request", operation_id="approval_request")
async def approval_request(
    release_approval_request: ReleaseApprovalRequest,
    protected_roles: ProtectedRole = Depends(
        read_write_user_protected_role_dependency),
    config: Config = Depends(get_settings),
    email_client: EmailClient = Depends(email_dependency)
) -> ReleaseApprovalRequestResponse:
    # data store URL prefix for handles
    def datastore_url_resolver(id: str) -> str:
        return f"https://data.{config.domain_base}/dataset/{id}?view=approvals"

    # The user must be associated with a linked Person
    linked_person = get_user_link(
        user=protected_roles.user,
        config=config
    )

    if linked_person is None:
        raise HTTPException(
            status_code=400,
            detail=f"You cannot request a review without having a linked Person in the registry."
        )

    await perform_approval_request(
        release_approval_request=release_approval_request,
        email_client=email_client,
        datastore_url_resolver=datastore_url_resolver,
        requester_id=linked_person,
        config=config,
        protected_roles=protected_roles
    )

    # here without a http exception, success.
    return ReleaseApprovalRequestResponse(
        dataset_id=release_approval_request.dataset_id,
        approver_id=release_approval_request.approver_id,
        details="Successfully sent request to approve dataset release to approver. Email notification included."
    )


@router.put("/action-approval-request", operation_id="action_approval_request")
async def action_approval_request(
    action_approval_request: ActionApprovalRequest,
    protected_roles: ProtectedRole = Depends(
        read_write_user_protected_role_dependency),
    config: Config = Depends(get_settings),
    email_client: EmailClient = Depends(email_dependency)
) -> ActionApprovalRequestResponse:
    # data store URL prefix for handles
    def datastore_url_resolver(id: str) -> str:
        return f"https://data.{config.domain_base}/dataset/{id}?view=approvals"
    await perform_action_of_approval_request(
        config=config,
        email_client=email_client,
        datastore_url_resolver=datastore_url_resolver,
        protected_roles=protected_roles,
        action_approval_request=action_approval_request,
    )

    # here without http exception, success.
    return ActionApprovalRequestResponse(
        dataset_id=action_approval_request.dataset_id,
        approved=action_approval_request.approve,
        details="Succesfully responded to dataset release approval request."
    )
