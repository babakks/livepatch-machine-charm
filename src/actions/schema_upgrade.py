# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Schema upgrade action."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ops.charm import ActionEvent
from ops.model import MaintenanceStatus

from util.schema_tool import run_schema_upgrade

if TYPE_CHECKING:
    from charm import OperatorMachineCharm


def on_schema_upgrade_action(self: OperatorMachineCharm, event: ActionEvent) -> None:
    """Run schema upgrade action."""
    event.log("Running schema upgrade action...")
    if self.unit.is_leader():
        run_schema_upgrade(self._state.db_uri)
        upgrade_required, version = self._check_schema_upgrade_ran()

        if upgrade_required:
            failure_reason = "Schema upgrade failed."
            self.unit.status = MaintenanceStatus(failure_reason)
            event.log(failure_reason)
            event.set_results(
                {
                    "schema-upgrade-required": upgrade_required,
                    "schema-version": version,
                }
            )
            event.fail(failure_reason)
        else:
            event.log("Schema upgrade was successful.")
            event.set_results(
                {
                    "schema-upgrade-required": upgrade_required,
                    "schema-version": version,
                }
            )

            # We can just send a None event to the method, because `event` here
            # is an action event, and they're not deferrable by definition, and
            # they raise a runtime exception. We don't want to end up passing
            # such an event to the `_config_changed` method (where we normally
            # use `event.defer`).
            self._config_changed(None)
