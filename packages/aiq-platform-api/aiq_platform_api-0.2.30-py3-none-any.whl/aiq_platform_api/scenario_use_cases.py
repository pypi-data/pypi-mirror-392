# Example use cases for Scenario endpoints
import os
import sys
import time
from enum import Enum
from typing import Optional, Dict, Any

from aiq_platform_api.common_utils import AttackIQRestClient, AttackIQLogger, ScenarioUtils, FileUploadUtils
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)

SCRIPT_EXECUTION_TEMPLATE_ID = "b7b0fa6d-5f3c-44b2-b393-3a83d3d32da3"
COMMAND_EXECUTION_TEMPLATE_ID = "9edec174-908e-4fea-b63d-5303c08fc1d6"

LANGUAGE_CONFIG = {
    "bash": {
        "interpreter": "/bin/bash",
        "ext": ".sh",
        "sample_body": "#!/bin/bash\necho 'Hello from bash scenario'",
        "allowed_templates": {"script_execution", "command_execution"},
    },
    "powershell": {
        "interpreter": "powershell.exe",
        "ext": ".ps1",
        "sample_body": "Write-Host 'Hello from PowerShell scenario'",
        "allowed_templates": {"script_execution", "command_execution"},
    },
    "python": {
        "interpreter": "python.exe",
        "ext": ".py",
        "sample_body": "print('Hello from Python scenario')",
        "allowed_templates": {"script_execution"},
    },
    "batch": {
        "interpreter": "cmd.exe",
        "ext": ".bat",
        "sample_body": "@echo off\necho Hello from Batch scenario",
        "allowed_templates": {"script_execution"},
    },
    "cmd": {
        "interpreter": "cmd.exe",
        "ext": ".bat",
        "sample_body": "@echo off\necho Hello from CMD scenario",
        "allowed_templates": {"command_execution"},
    },
}


class TestChoice(Enum):
    LIST_ALL = "list_all"
    LIST_MIMIKATZ = "list_mimikatz"
    SEARCH_SCENARIOS = "search_scenarios"
    GET_SCENARIO_DETAILS = "get_scenario_details"
    PAGINATION_WORKFLOW = "pagination_workflow"
    COPY_SCENARIO = "copy_scenario"
    DELETE_SCENARIO = "delete_scenario"
    COPY_AND_DELETE = "copy_and_delete"
    UPLOAD_AND_PATCH = "upload_and_patch"
    CREATE_SCRIPT_AND_DELETE = "create_script_and_delete"
    CREATE_COMMAND_AND_DELETE = "create_command_and_delete"
    UPDATE_SCRIPT_AND_DELETE = "update_script_and_delete"
    UPDATE_COMMAND_AND_DELETE = "update_command_and_delete"
    ALL = "all"


def _build_description_payload(summary: Optional[str]) -> Optional[Dict[str, Any]]:
    if not summary:
        return None
    return {
        "description_json": {
            "summary": summary,
            "prerequisites": "",
            "failure_criteria": "",
            "prevention_criteria": "",
            "additional_information": "",
        }
    }


def list_scenarios(
    client: AttackIQRestClient, limit: Optional[int] = 10, filter_params: Optional[Dict[str, Any]] = None
) -> int:
    filter_params = filter_params or {}
    logger.info(f"Listing up to {limit} scenarios with params: {filter_params}")
    count = 0
    for scenario in ScenarioUtils.list_scenarios(client, params=filter_params, limit=limit):
        count += 1
        logger.info(f"Scenario {count}: ID={scenario['id']}, Name={scenario['name']}")
    logger.info(f"Total scenarios listed: {count}")
    return count


def save_scenario_copy(
    client: AttackIQRestClient,
    scenario_id: str,
    new_name: str,
    model_json: Optional[Dict[str, Any]] = None,
    fork_template: bool = True,
) -> Dict[str, Any]:
    logger.info(f"Creating a copy of scenario {scenario_id} with name '{new_name}'")
    copy_data = {"name": new_name, "fork_template": fork_template}
    if model_json:
        copy_data["model_json"] = model_json
    new_scenario = ScenarioUtils.save_copy(client, scenario_id, copy_data)
    if not new_scenario:
        raise ValueError("Failed to create scenario copy")
    logger.info(f"Successfully created scenario copy with ID: {new_scenario['id']}")
    return new_scenario


def delete_scenario_use_case(client: AttackIQRestClient, scenario_id: str):
    logger.info(f"--- Attempting to delete scenario: {scenario_id} ---")
    success = ScenarioUtils.delete_scenario(client, scenario_id)
    if success:
        logger.info(f"Successfully initiated deletion of scenario: {scenario_id}")
    else:
        logger.error(f"Failed to initiate deletion of scenario: {scenario_id}")


def test_list_scenarios(client: AttackIQRestClient, search_term: Optional[str] = None):
    logger.info("--- Testing Scenario Listing ---")
    filter_params = {"search": search_term} if search_term else {}
    list_scenarios(client, limit=5, filter_params=filter_params)


def test_list_mimikatz_scenarios(client: AttackIQRestClient):
    logger.info("--- Testing Scenario Listing with Mimikatz filter ---")
    test_list_scenarios(client, "Mimikatz")


def test_copy_scenario(client: AttackIQRestClient, scenario_id: Optional[str] = None):
    logger.info("--- Testing Scenario Copy ---")

    if not scenario_id:
        scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID", "5417db5e-569f-4660-86ae-9ea7b73452c5")

    scenario = ScenarioUtils.get_scenario(client, scenario_id)
    old_name = scenario["name"]
    old_model_json = scenario["model_json"]
    if old_model_json:
        old_model_json["domain"] = "example.com"

    timestamp = int(time.time())
    new_scenario_name = f"aiq_platform_api created {old_name} - {timestamp}"
    new_scenario = save_scenario_copy(
        client,
        scenario_id=scenario_id,
        new_name=new_scenario_name,
        model_json=old_model_json,
    )

    logger.info(f"New scenario created: {new_scenario['name']} ({new_scenario['id']})")
    return new_scenario["id"]


def test_upload_and_patch_script_scenario(
    client: AttackIQRestClient,
    script_body: Optional[str] = None,
    file_name: Optional[str] = None,
):
    """Upload a script file and patch an existing script-execution scenario to reference it."""
    logger.info("--- Testing Script Upload + Patch Scenario ---")
    scenario = ScenarioUtils.get_scenario(client, SCRIPT_EXECUTION_TEMPLATE_ID)

    model_json = scenario["model_json"]
    scripts = model_json["scripts"]

    body = script_body or os.environ.get("ATTACKIQ_SCRIPT_BODY") or "#!/bin/bash\necho hello from aiq-platform-api"
    name = file_name or f"uploaded_script_{int(time.time())}.sh"

    upload = FileUploadUtils.upload_script_file(
        client=client,
        file_name=name,
        file_content=body.encode(),
        content_type="text/plain",
    )
    scripts[0]["script_files"] = upload["file_path"]
    scripts[0]["success_type"] = "with_exit_code"
    scripts[0]["interpreter"] = "/bin/bash"

    template_instance = ScenarioUtils.save_copy(
        client,
        SCRIPT_EXECUTION_TEMPLATE_ID,
        {"name": f"SDK Script Upload {int(time.time())}", "model_json": model_json, "fork_template": False},
    )
    scenario_id = template_instance["id"]
    updated = ScenarioUtils.update_scenario(client, scenario_id, {"model_json": model_json})
    if updated:
        logger.info(f"Patched scenario {scenario_id} with uploaded file {upload['file_path']}")


def create_script_execution_scenario(
    client: AttackIQRestClient,
    scenario_name: str,
    script_body: str,
    language: str = "bash",
) -> Dict[str, Any]:
    language_key = language.lower()
    if language_key not in LANGUAGE_CONFIG:
        raise ValueError(f"Unsupported language: {language}")
    config = LANGUAGE_CONFIG[language_key]
    if "script_execution" not in config["allowed_templates"]:
        raise ValueError(f"Language {language} not allowed for script execution template")
    template = ScenarioUtils.get_scenario(client, SCRIPT_EXECUTION_TEMPLATE_ID)
    model_json = template["model_json"]
    scripts = model_json["scripts"]
    file_name = f"{scenario_name.lower().replace(' ', '_')}{config['ext']}"
    upload = FileUploadUtils.upload_script_file(
        client=client,
        file_name=file_name,
        file_content=script_body.encode(),
        content_type="text/plain",
    )
    scripts[0]["script_files"] = upload["file_path"]
    scripts[0]["success_type"] = "with_exit_code"
    scripts[0]["interpreter"] = config["interpreter"]
    created = ScenarioUtils.save_copy(
        client,
        SCRIPT_EXECUTION_TEMPLATE_ID,
        {
            "name": scenario_name,
            "model_json": model_json,
            "fork_template": False,
        },
    )
    if not created:
        raise ValueError("Failed to create script execution scenario")
    return created


def create_command_execution_scenario(
    client: AttackIQRestClient,
    scenario_name: str,
    command: str,
) -> Dict[str, Any]:
    template = ScenarioUtils.get_scenario(client, COMMAND_EXECUTION_TEMPLATE_ID)
    model_json = template["model_json"]
    commands = model_json["commands"]
    commands[0]["command"] = command
    commands[0]["success_type"] = "with_exit_code"
    created = ScenarioUtils.save_copy(
        client,
        COMMAND_EXECUTION_TEMPLATE_ID,
        {
            "name": scenario_name,
            "model_json": model_json,
            "fork_template": False,
        },
    )
    if not created:
        raise ValueError("Failed to create command execution scenario")
    return created


def update_script_execution_scenario(
    client: AttackIQRestClient,
    scenario_id: str,
    new_script_body: Optional[str] = None,
    language: Optional[str] = None,
    summary: Optional[str] = None,
) -> Dict[str, Any]:
    scenario = ScenarioUtils.get_scenario(client, scenario_id)
    model_json = scenario["model_json"]
    scripts = model_json["scripts"]
    payload: Dict[str, Any] = {}
    extras = scenario.get("extras") or {}

    if new_script_body:
        if not language:
            raise ValueError("language is required when uploading a new script")
        language_key = language.lower()
        if language_key not in LANGUAGE_CONFIG:
            raise ValueError(f"Unsupported language: {language}")
        config = LANGUAGE_CONFIG[language_key]
        upload = FileUploadUtils.upload_script_file(
            client=client,
            file_name=f"{scenario['name'].lower().replace(' ', '_')}{config['ext']}",
            file_content=new_script_body.encode(),
            content_type="text/plain",
        )
        scripts[0]["script_files"] = upload["file_path"]
        scripts[0]["success_type"] = "with_exit_code"
        scripts[0]["interpreter"] = config["interpreter"]
        payload["model_json"] = model_json
        extras = {**extras, "language": language}

    description_payload = _build_description_payload(summary)
    if description_payload:
        payload.update(description_payload)
    if extras:
        payload["extras"] = extras
    if not payload:
        raise ValueError("No updates specified for script execution scenario")
    return ScenarioUtils.update_scenario(client, scenario_id, payload)


def update_command_execution_scenario(
    client: AttackIQRestClient,
    scenario_id: str,
    command: Optional[str] = None,
    summary: Optional[str] = None,
) -> Dict[str, Any]:
    scenario = ScenarioUtils.get_scenario(client, scenario_id)
    model_json = scenario["model_json"]
    commands = model_json["commands"]
    payload: Dict[str, Any] = {}

    if command:
        commands[0]["command"] = command
        commands[0]["success_type"] = "with_exit_code"
        payload["model_json"] = model_json

    description_payload = _build_description_payload(summary)
    if description_payload:
        payload.update(description_payload)
    if not payload:
        raise ValueError("No updates specified for command execution scenario")
    return ScenarioUtils.update_scenario(client, scenario_id, payload)


def test_create_and_delete_script_execution(
    client: AttackIQRestClient,
    languages: Optional[list[str]] = None,
    script_body: Optional[str] = None,
):
    if languages is None:
        env_value = os.environ.get("ATTACKIQ_SCRIPT_LANGUAGES")
        if env_value:
            languages = [lang.strip() for lang in env_value.split(",") if lang.strip()]
        else:
            languages = ["bash"]

    for language in languages:
        scenario_name = f"SDK Script {language} {int(time.time())}"
        config = LANGUAGE_CONFIG[language.lower()]
        body = script_body or config["sample_body"]
        created = create_script_execution_scenario(client, scenario_name, body, language)
        scenario_id = created["id"]
        logger.info(f"Created script execution scenario {scenario_id} ({language})")
        ScenarioUtils.delete_scenario(client, scenario_id)
        logger.info(f"Deleted script execution scenario {scenario_id} ({language})")


def test_create_and_delete_command_execution(
    client: AttackIQRestClient,
    command: Optional[str] = None,
):
    scenario_name = f"SDK Command {int(time.time())}"
    command_text = command or os.environ.get("ATTACKIQ_COMMAND_TEXT", "whoami && hostname && date")
    created = create_command_execution_scenario(client, scenario_name, command_text)
    scenario_id = created["id"]
    logger.info(f"Created command execution scenario {scenario_id}")
    ScenarioUtils.delete_scenario(client, scenario_id)
    logger.info(f"Deleted command execution scenario {scenario_id}")


def test_update_script_execution(
    client: AttackIQRestClient,
    language: str = "bash",
):
    language_key = language.lower()
    created = create_script_execution_scenario(
        client,
        scenario_name=f"SDK Script Update {int(time.time())}",
        script_body=LANGUAGE_CONFIG[language_key]["sample_body"],
        language=language,
    )
    scenario_id = created["id"]
    try:
        updated = update_script_execution_scenario(
            client,
            scenario_id=scenario_id,
            new_script_body=f"#!/bin/bash\necho 'updated {time.time()}'",
            language=language,
            summary="Updated via scenario_use_cases",
        )
        logger.info(f"Updated script scenario: {updated}")
    finally:
        ScenarioUtils.delete_scenario(client, scenario_id)
        logger.info(f"Deleted script scenario {scenario_id}")


def test_update_command_execution(
    client: AttackIQRestClient,
):
    created = create_command_execution_scenario(
        client,
        scenario_name=f"SDK Command Update {int(time.time())}",
        command="whoami",
    )
    scenario_id = created["id"]
    try:
        updated = update_command_execution_scenario(
            client,
            scenario_id=scenario_id,
            command="hostname && date",
            summary="Updated via scenario_use_cases",
        )
        logger.info(f"Updated command scenario: {updated}")
    finally:
        ScenarioUtils.delete_scenario(client, scenario_id)
        logger.info(f"Deleted command scenario {scenario_id}")


def test_delete_scenario(client: AttackIQRestClient, scenario_id: str):
    logger.info("--- Testing Scenario Deletion ---")
    if not scenario_id:
        logger.warning("No scenario ID provided for deletion")
        return
    delete_scenario_use_case(client, scenario_id)


def search_scenarios_use_case(
    client: AttackIQRestClient,
    query: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    ordering: Optional[str] = "-modified",
) -> dict:
    logger.info(
        f"--- Searching scenarios with query: '{query}', limit: {limit}, offset: {offset}, ordering: {ordering} ---"
    )
    try:
        result = ScenarioUtils.search_scenarios(client, query, limit, offset, ordering)
        logger.info(f"Found {result['count']} total, returning {len(result['results'])}")
        for idx, scenario in enumerate(result["results"], 1):
            logger.info(f"{idx}. {scenario['name']} (ID: {scenario['id']})")
        return result
    except Exception as e:
        logger.error(f"Failed to search scenarios: {e}")
        raise


def get_scenario_details_use_case(
    client: AttackIQRestClient,
    scenario_id: str,
) -> Optional[Dict[str, Any]]:
    logger.info(f"--- Getting details for scenario: {scenario_id} ---")
    details = ScenarioUtils.get_scenario_details(client, scenario_id)
    if details:
        logger.info(f"Scenario: {details['name']}")
        logger.info(f"Description: {details.get('description', 'N/A')}")
        logger.info(f"Created: {details.get('created_at', 'N/A')}")
        return details
    logger.warning(f"No details found for scenario: {scenario_id}")
    return None


def test_search_scenarios(client: AttackIQRestClient):
    logger.info("--- Testing Scenario Search ---")

    # Search by keyword
    logger.info("\n1. Searching by keyword 'LSASS':")
    search_scenarios_use_case(client, "LSASS", limit=5)

    # Search by MITRE technique
    logger.info("\n2. Searching by MITRE technique 'T1003':")
    search_scenarios_use_case(client, "T1003", limit=5)

    # Search by tag
    logger.info("\n3. Searching by tag 'ransomware':")
    search_scenarios_use_case(client, "ransomware", limit=5)

    # List all scenarios
    logger.info("\n4. Listing all scenarios (no query):")
    search_scenarios_use_case(client, query=None, limit=5)


def test_get_scenario_details(client: AttackIQRestClient, scenario_id: Optional[str] = None):
    logger.info("--- Testing Get Scenario Details ---")

    if not scenario_id:
        # First search for a scenario, then get its details
        scenarios = search_scenarios_use_case(client, "Mimikatz", limit=1)
        if not scenarios["results"]:
            logger.warning("No scenarios found to get details for")
            return
        scenario_id = scenarios["results"][0]["id"]

    get_scenario_details_use_case(client, scenario_id)


def test_copy_and_delete(client: AttackIQRestClient, scenario_id: Optional[str] = None):
    logger.info("--- Testing Scenario Copy and Delete Workflow ---")

    if not scenario_id:
        scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID", "5417db5e-569f-4660-86ae-9ea7b73452c5")

    new_scenario_id = test_copy_scenario(client, scenario_id)
    if new_scenario_id:
        logger.info(f"--- Proceeding to delete the created scenario: {new_scenario_id} ---")
        test_delete_scenario(client, new_scenario_id)
    else:
        logger.warning("Could not get ID of newly created scenario, skipping deletion.")


def test_pagination_workflow(client: AttackIQRestClient):
    """
    Test pagination with offset to demonstrate fetching batches.

    This validates:
    1. minimal=true reduces fields (23 -> 7)
    2. offset pagination works correctly
    3. No duplicate scenarios across batches

    Use this pattern for other endpoints (assets, assessments, attack graphs).
    """
    logger.info("--- Testing Pagination Workflow ---")

    batch_size = 5
    max_batches = 3
    all_ids = []

    for batch_num in range(1, max_batches + 1):
        offset = (batch_num - 1) * batch_size
        logger.info(f"\n--- Batch {batch_num}: offset={offset}, limit={batch_size} ---")

        scenarios = list(
            ScenarioUtils.list_scenarios(client, params={"search": "powershell"}, limit=batch_size, offset=offset)
        )

        if not scenarios:
            logger.info("No more scenarios. Stopping.")
            break

        logger.info(f"Retrieved {len(scenarios)} scenarios:")
        for idx, scenario in enumerate(scenarios, 1):
            scenario_id = scenario["id"]
            scenario_name = scenario["name"]
            logger.info(f"  {idx}. {scenario_name}")
            all_ids.append(scenario_id)

        logger.info(f"Fields in scenario: {list(scenarios[0].keys())}")
        logger.info(f"Field count: {len(scenarios[0].keys())} (7 with minimal=true)")

    logger.info("\n--- Summary ---")
    logger.info(f"Total fetched: {len(all_ids)}")
    logger.info(f"Unique: {len(set(all_ids))}")
    logger.info(f"Duplicates: {len(all_ids) - len(set(all_ids))}")

    if len(all_ids) == len(set(all_ids)):
        logger.info("✅ SUCCESS: No duplicates, pagination working correctly!")
    else:
        logger.error("⚠️  FAILED: Duplicates detected!")


def test_all(client: AttackIQRestClient):
    # Test listing without filter
    test_list_scenarios(client)

    # Test listing with filter
    test_list_mimikatz_scenarios(client)

    # Test search scenarios
    test_search_scenarios(client)

    # Test get scenario details
    test_get_scenario_details(client)

    # Test pagination workflow
    test_pagination_workflow(client)

    # Test copy and delete workflow
    scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID")
    if scenario_id:
        test_copy_and_delete(client, scenario_id)
    else:
        logger.warning("ATTACKIQ_SCENARIO_ID not set. Skipping copy/delete tests.")

    # Test upload + patch workflow (requires separate scenario id)
    test_upload_and_patch_script_scenario(client)
    test_create_and_delete_script_execution(client)
    test_create_and_delete_command_execution(client)
    test_update_script_execution(client)
    test_update_command_execution(client)


def run_test(choice: "TestChoice", client: AttackIQRestClient, scenario_id: Optional[str] = None):
    test_functions = {
        TestChoice.LIST_ALL: lambda: test_list_scenarios(client),
        TestChoice.LIST_MIMIKATZ: lambda: test_list_mimikatz_scenarios(client),
        TestChoice.SEARCH_SCENARIOS: lambda: test_search_scenarios(client),
        TestChoice.GET_SCENARIO_DETAILS: lambda: test_get_scenario_details(client, scenario_id),
        TestChoice.PAGINATION_WORKFLOW: lambda: test_pagination_workflow(client),
        TestChoice.COPY_SCENARIO: lambda: test_copy_scenario(client, scenario_id),
        TestChoice.DELETE_SCENARIO: lambda: (
            test_delete_scenario(client, scenario_id)
            if scenario_id
            else logger.error("Scenario ID required for delete test")
        ),
        TestChoice.COPY_AND_DELETE: lambda: test_copy_and_delete(client, scenario_id),
        TestChoice.UPLOAD_AND_PATCH: lambda: test_upload_and_patch_script_scenario(client, scenario_id=scenario_id),
        TestChoice.CREATE_SCRIPT_AND_DELETE: lambda: test_create_and_delete_script_execution(client),
        TestChoice.CREATE_COMMAND_AND_DELETE: lambda: test_create_and_delete_command_execution(client),
        TestChoice.UPDATE_SCRIPT_AND_DELETE: lambda: test_update_script_execution(client),
        TestChoice.UPDATE_COMMAND_AND_DELETE: lambda: test_update_command_execution(client),
        TestChoice.ALL: lambda: test_all(client),
    }
    test_functions[choice]()


if __name__ == "__main__":
    if not ATTACKIQ_PLATFORM_URL or not ATTACKIQ_PLATFORM_API_TOKEN:
        logger.error("Missing ATTACKIQ_PLATFORM_URL or ATTACKIQ_PLATFORM_API_TOKEN")
        sys.exit(1)

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)
    scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID", "5417db5e-569f-4660-86ae-9ea7b73452c5")

    choice = TestChoice.PAGINATION_WORKFLOW
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        try:
            choice = TestChoice[arg.upper()]
        except KeyError:
            try:
                choice = TestChoice(arg.lower())
            except Exception:
                logger.error(f"Unknown test choice argument: {arg}")
                sys.exit(1)

    run_test(choice, client, scenario_id)
