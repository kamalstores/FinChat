from langchain.tools import tool, ToolRuntime
from sqlalchemy import or_
from app.agent.constants import ALLOWED_METRICS
from app.model.financial_data import FinancialData
from app.agent.utils import normalize_company, validate_metrics


@tool
def sql_query(
    companies: list[str],
    metrics: list[str],
    start_year: int,
    end_year: int,
    runtime: ToolRuntime,
):
    """Query financial metrics (revenue, profit, income) for companies over a year range."""
    db = runtime.context["db"]

    companies = [normalize_company(c) for c in companies]
    valid_metrics, invalid_metrics = validate_metrics(metrics)

    if invalid_metrics or not valid_metrics or start_year > end_year:
        return {
            "found": False,
            "error": "invalid parameters",
            "invalid_metrics": invalid_metrics,
            "allowed_metrics": list(ALLOWED_METRICS),
        }

    stmt = (
        db.query(FinancialData)
        .filter(
            or_(
                FinancialData.company.in_(companies),
                FinancialData.ticker.in_(companies),
            ),
            FinancialData.year.between(start_year, end_year),
        )
        .with_entities(
            FinancialData.company,
            FinancialData.ticker,
            FinancialData.year,
            *[getattr(FinancialData, m) for m in valid_metrics],
        )
    )

    compiled_query = str(stmt.statement.compile(compile_kwargs={"literal_binds": True}))

    rows = stmt.all()

    if not rows:
        return {"found": False, "query": compiled_query, "results": []}

    return {
        "found": True,
        "query": compiled_query,
        "results": [
            {
                "company": r.company,
                "year": r.year,
                **{m: getattr(r, m) for m in valid_metrics},
            }
            for r in rows
        ],
    }
