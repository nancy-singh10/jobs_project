"""
Controlled Task Handler Registry for FlowOps Phase 2.
Only pre-registered task handlers can be executed by workers.
Arbitrary code execution or unregistered task types are strictly prohibited.
"""
import time
import uuid
from typing import Dict, Any, Callable
from apps.common.exceptions import ApplicationError


class TaskExecutionError(ApplicationError):
    """Raised when a task handler encounters a processing failure."""
    def __init__(self, message, details=None):
        super().__init__(message=message, code="TASK_EXECUTION_FAILED", details=details)


def handle_invoice_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for 'invoice.generate'.
    Simulates calculating line items, tax, and PDF rendering.
    """
    if payload.get("simulate_error") is True:
        raise TaskExecutionError(
            message="Invoice calculation failed: tax engine service unreachable (simulated).",
            details={"invoice_id": payload.get("invoice_id")},
        )

    invoice_id = payload.get("invoice_id", 1001)
    customer_email = payload.get("customer_email", "customer@example.com")
    total_usd = float(payload.get("total_usd", 149.50))
    tax = round(total_usd * 0.08, 2)
    grand_total = round(total_usd + tax, 2)

    # Simulated micro-delay for realistic worker processing
    time.sleep(0.05)

    return {
        "invoice_number": f"INV-2026-{invoice_id}",
        "customer_email": customer_email,
        "subtotal_usd": total_usd,
        "tax_usd": tax,
        "grand_total_usd": grand_total,
        "pdf_download_url": f"https://cdn.flowops.internal/invoices/INV-2026-{invoice_id}.pdf",
        "processed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def handle_email_send(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for 'email.send'.
    Simulates SMTP mail dispatch.
    """
    if payload.get("simulate_error") is True:
        raise TaskExecutionError(
            message="SMTP Delivery failed: Mailbox quota exceeded (simulated).",
            details={"recipient": payload.get("recipient")},
        )

    recipient = payload.get("recipient") or payload.get("customer_email") or "user@example.com"
    template = payload.get("template", "default_notification")

    time.sleep(0.04)

    return {
        "message_id": f"<msg-{uuid.uuid4().hex[:12]}@flowops.internal>",
        "recipient": recipient,
        "template": template,
        "delivery_status": "DELIVERED",
        "gateway_response": "250 2.0.0 OK: queued as 48A109",
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def handle_report_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for 'report.generate' / 'report.create'.
    Simulates database aggregation and file export.
    """
    if payload.get("simulate_error") is True:
        raise TaskExecutionError(
            message="Report generation failed: Query memory limit exceeded (simulated).",
            details={"period": payload.get("report_period")},
        )

    report_period = payload.get("report_period", "2026-Q3")
    fmt = payload.get("format", "csv").lower()

    time.sleep(0.06)

    return {
        "report_id": f"RPT-{uuid.uuid4().hex[:8].upper()}",
        "report_period": report_period,
        "format": fmt,
        "records_aggregated": 4820,
        "export_size_bytes": 1048576,
        "download_url": f"https://cdn.flowops.internal/reports/quarterly-{report_period}.{fmt}",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# Handler Registry Map
TASK_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "invoice.generate": handle_invoice_generate,
    "email.send": handle_email_send,
    "report.generate": handle_report_generate,
    "report.create": handle_report_generate,
}


def is_task_type_supported(task_type: str) -> bool:
    """Checks whether the requested task type is registered."""
    return task_type.strip() in TASK_REGISTRY


def get_task_handler(task_type: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Resolves handler function for task_type or raises TaskExecutionError.
    """
    cleaned_type = task_type.strip()
    handler = TASK_REGISTRY.get(cleaned_type)
    if not handler:
        raise TaskExecutionError(
            message=f"Unsupported task type '{task_type}'. Task is not registered in worker registry.",
            details={"supported_types": list(TASK_REGISTRY.keys())},
        )
    return handler

