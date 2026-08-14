"""Generate a deterministic, privacy-safe ticket dataset for the portfolio classifier."""

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "tickets.csv"
random.seed(42)

CATEGORIES = {
    "Access & Identity": {
        "group": "Identity Operations",
        "subjects": [
            "MFA prompt loop",
            "Account locked after password reset",
            "New starter cannot access portal",
            "Admin role assignment missing",
            "SSO redirects back to login",
            "Conditional Access block",
        ],
        "symptoms": [
            "sign-in fails with an access policy message",
            "the account remains locked after self-service recovery",
            "MFA registration never completes",
            "the application reports insufficient permissions",
            "the identity provider returns an authentication error",
            "privileged access activation is unavailable",
        ],
        "resolutions": [
            "reviewed sign-in logs and corrected policy targeting",
            "restored the account and verified MFA",
            "reapplied the approved role and tested least-privilege access",
        ],
    },
    "Cloud & Infrastructure": {
        "group": "Cloud Platform Engineering",
        "subjects": [
            "Virtual machine health check failed",
            "Container deployment is unavailable",
            "Storage account latency",
            "Resource group deployment error",
            "Cloud function timing out",
            "Autoscaling did not trigger",
        ],
        "symptoms": [
            "the workload stopped responding after deployment",
            "health probes report an unhealthy backend",
            "resource provisioning fails during validation",
            "latency increased across the hosted service",
            "the instance is running but the application is unreachable",
            "capacity remains exhausted during peak demand",
        ],
        "resolutions": [
            "rolled back the release and validated health probes",
            "corrected resource configuration and redeployed",
            "restored capacity and verified platform telemetry",
        ],
    },
    "Data & Database": {
        "group": "Data Services",
        "subjects": [
            "Database connections exhausted",
            "Report contains stale records",
            "Query performance degraded",
            "Replication delay detected",
            "Schema migration failed",
            "Nightly import rejected rows",
        ],
        "symptoms": [
            "the application cannot obtain a database connection",
            "reports are missing recently committed records",
            "queries time out during normal usage",
            "the replica is behind the primary",
            "a migration stopped before completion",
            "the data load reports validation failures",
        ],
        "resolutions": [
            "cleared the connection leak and verified pool health",
            "repaired the pipeline and reconciled record counts",
            "optimized the query and validated data correctness",
        ],
    },
    "Email & Collaboration": {
        "group": "Collaboration Services",
        "subjects": [
            "Outbound messages delayed",
            "Shared calendar unavailable",
            "Video meeting has no audio",
            "Mailbox quota warning",
            "Shared drive permission error",
            "Distribution list rejects sender",
        ],
        "symptoms": [
            "messages remain queued and are not delivered",
            "the shared calendar cannot be opened",
            "meeting participants cannot hear audio",
            "the mailbox rejects new messages",
            "a team folder reports access denied",
            "mail to the group returns a delivery error",
        ],
        "resolutions": [
            "corrected the transport rule and verified mail flow",
            "restored sharing permissions and tested collaboration",
            "updated the client configuration and verified a meeting",
        ],
    },
    "Hardware & Devices": {
        "group": "Endpoint Engineering",
        "subjects": [
            "Laptop will not power on",
            "External monitor not detected",
            "Disk encryption recovery screen",
            "Printer repeatedly jams",
            "Battery drains rapidly",
            "Docking station disconnects",
        ],
        "symptoms": [
            "the device shows no power or charging indicator",
            "the display remains blank after reconnecting",
            "the endpoint requests an encryption recovery key",
            "printing stops with a hardware alert",
            "the battery loses charge within one hour",
            "USB and network connections drop through the dock",
        ],
        "resolutions": [
            "completed hardware diagnostics and replaced the failed component",
            "updated firmware and verified peripheral stability",
            "recovered the device and confirmed encryption compliance",
        ],
    },
    "Network & Connectivity": {
        "group": "Network Operations",
        "subjects": [
            "VPN disconnects every few minutes",
            "Office Wi-Fi cannot obtain address",
            "Internal hostname does not resolve",
            "Remote site packet loss",
            "Wired network has no connectivity",
            "Application route is unreachable",
        ],
        "symptoms": [
            "the secure tunnel drops during active sessions",
            "the device cannot obtain an IP address",
            "DNS returns no record for an internal service",
            "users experience packet loss and high latency",
            "the network adapter has link but no reachability",
            "traffic stops at an unexpected route",
        ],
        "resolutions": [
            "corrected the network policy and verified stable VPN",
            "repaired DHCP or DNS configuration and retested",
            "restored the route and confirmed end-to-end reachability",
        ],
    },
    "Security & Compliance": {
        "group": "Security Operations Center",
        "subjects": [
            "Suspicious sign-in alert",
            "Endpoint malware detection",
            "Sensitive file shared externally",
            "Unexpected administrator account",
            "Phishing message reported",
            "Compliance scan failed",
        ],
        "symptoms": [
            "a login originated from an unusual location",
            "endpoint protection quarantined a suspicious file",
            "a confidential document has a public sharing link",
            "an unapproved privileged identity was created",
            "a user entered credentials into a suspicious page",
            "the device no longer meets the security baseline",
        ],
        "resolutions": [
            "contained the identity and completed security review",
            "isolated the endpoint and preserved investigation evidence",
            "removed exposure and validated the compliance control",
        ],
    },
    "Software & Applications": {
        "group": "Application Support",
        "subjects": [
            "Finance application crashes at launch",
            "API returns server error",
            "Desktop client cannot update",
            "Form submission loses data",
            "Browser page remains blank",
            "Integration job fails authentication",
        ],
        "symptoms": [
            "the application closes before the login screen",
            "the service returns an internal server error",
            "the client update repeatedly rolls back",
            "submitted fields are not saved",
            "the page loads without application content",
            "the integration cannot authenticate to its dependency",
        ],
        "resolutions": [
            "repaired the application configuration and verified launch",
            "fixed the API dependency and tested the user path",
            "deployed a corrected release and validated telemetry",
        ],
    },
}

PRIORITIES = {
    "P1": [("company-wide", 850), ("all customer-facing teams", 420)],
    "P2": [("multiple departments", 95), ("an entire office", 140)],
    "P3": [("a small team", 8), ("several employees", 5)],
    "P4": [("one employee", 1), ("a new starter", 1)],
}


def main() -> None:
    rows = []
    ticket_number = 1000
    for category, details in CATEGORIES.items():
        for priority, scopes in PRIORITIES.items():
            for variant in range(12):
                scope, users = scopes[variant % len(scopes)]
                subject = details["subjects"][variant % len(details["subjects"])]
                symptom = details["symptoms"][(variant * 2 + 1) % len(details["symptoms"])]
                urgency = {
                    "P1": "Production work is stopped and no workaround exists.",
                    "P2": "Critical business activity is degraded and the workaround is limited.",
                    "P3": "Normal work is affected, but a temporary workaround is available.",
                    "P4": "This is a low-impact request with a flexible completion time.",
                }[priority]
                context = random.choice(
                    [
                        "The issue began after a scheduled change.",
                        "The requester reproduced the issue twice.",
                        "No recent local changes are known.",
                        "Initial restart and retry steps did not resolve it.",
                    ]
                )
                rows.append(
                    {
                        "ticket_id": f"SYN-{ticket_number}",
                        "subject": subject,
                        "description": f"{scope.capitalize()} report that {symptom}. {urgency} {context}",
                        "affected_users": users,
                        "category": category,
                        "priority": priority,
                        "assignment_group": details["group"],
                        "resolution": details["resolutions"][variant % len(details["resolutions"])],
                    }
                )
                ticket_number += 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic tickets to {OUTPUT}")


if __name__ == "__main__":
    main()
