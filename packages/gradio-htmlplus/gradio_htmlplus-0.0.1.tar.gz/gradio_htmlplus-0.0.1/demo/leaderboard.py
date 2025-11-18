import pandas as pd
from typing import Optional

# Mock Helper Functions 
def get_rank_badge(rank):
    colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
    color = colors.get(rank, "#64748B")
    return f'<span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; border-radius: 50%; background-color: {color}; color: white; font-weight: bold;">{rank}</span>'


def get_success_rate_bar(rate):
    if pd.isna(rate):
        return "N/A"
    color = "#10B981" if rate >= 75 else "#F59E0B" if rate >= 50 else "#EF4444"
    return f"""
    <div style="background-color: #E2E8F0; border-radius: 6px; overflow: hidden; height: 20px; position: relative;">
        <div style="width: {rate}%; background-color: {color}; height: 100%;"></div>
        <span style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); color: #0F172A; font-weight: 600; font-size: 12px;">{rate:.1f}%</span>
    </div>
    """


def get_gpu_utilization_bar(util):
    return get_success_rate_bar(util)


def get_provider_badge(provider):
    color = "#4F46E5" if provider == "litellm" else "#14B8A6"
    return f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">{provider}</span>'


def get_agent_type_badge(agent_type):
    color = "#0EA5E9"
    return f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">{agent_type}</span>'


def get_hardware_badge(has_gpu):
    label = "GPU" if has_gpu else "CPU"
    color = "#10B981" if has_gpu else "#F59E0B"
    return f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">{label}</span>'


def format_cost(cost):
    if pd.isna(cost):
        return "N/A"
    return f"${cost:.4f}"


def format_duration(ms):
    if pd.isna(ms):
        return "N/A"
    return f"{ms / 1000:.2f}s"


def generate_leaderboard_html(
    df: pd.DataFrame, sort_by: str = "success_rate", ascending: bool = False
) -> str:
    """
    Generates a styled HTML table for the leaderboard.

    Args:
        df: The leaderboard DataFrame.
        sort_by: The column to sort the DataFrame by.
        ascending: The sort order.

    Returns:
        A string containing the complete HTML for the table.
    """
    df_sorted = df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)

    html = """
    <style>
        /* Leaderboard Table Styles */
         .tm-action-button {
            background-color: #EF4444; /* Red color for delete/action */
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        .tm-action-button:hover {
            background-color: #DC2626; /* Darker red on hover */
        }
        .tm-leaderboard-container { background: #F8FAFC; border-radius: 16px; overflow-x: auto; overflow-y: visible; border: 1px solid rgba(203, 213, 225, 0.8); margin: 20px 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); max-width: 100%; }
        .tm-leaderboard-container::-webkit-scrollbar { height: 8px; }
        .tm-leaderboard-container::-webkit-scrollbar-track { background: #E2E8F0; border-radius: 4px; }
        .tm-leaderboard-container::-webkit-scrollbar-thumb { background: #94A3B8; border-radius: 4px; }
        .tm-leaderboard-container::-webkit-scrollbar-thumb:hover { background: #64748B; }
        .tm-leaderboard-table { width: 100%; min-width: 1650px; border-collapse: collapse; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #FFFFFF; color: #0F172A; }
        .tm-leaderboard-table thead { background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); position: sticky; top: 0; z-index: 10; backdrop-filter: blur(10px); }
        .tm-leaderboard-table th { padding: 16px 12px; text-align: left; font-weight: 600; color: #FFFFFF; border-bottom: 2px solid #4338CA; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; }
        .tm-leaderboard-table td { padding: 14px 12px; border-bottom: 1px solid rgba(226, 232, 240, 0.8); color: #1E293B; font-size: 14px; vertical-align: middle; }
        .tm-leaderboard-table tbody tr { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; }
        .tm-leaderboard-table tbody tr:hover { background: rgba(99, 102, 241, 0.08) !important; box-shadow: 0 0 15px rgba(99, 102, 241, 0.15), inset 0 0 15px rgba(99, 102, 241, 0.05); transform: scale(1.002); }
        .tm-leaderboard-table tbody tr:nth-child(even) { background: rgba(241, 245, 249, 0.6); }
        .tm-model-name { font-weight: 600; color: #000000 !important; font-size: 15px; transition: color 0.2s ease; }
        .tm-leaderboard-table tr:hover .tm-model-name { color: #4F46E5 !important; }
        .tm-numeric-cell { font-family: 'Monaco', 'Menlo', monospace; font-size: 13px; text-align: center; color: #000000 !important; }
        .tm-badge-cell { text-align: center; }
        .tm-run-id { font-family: 'Monaco', 'Menlo', monospace; font-size: 12px; color: #000000 !important; cursor: pointer; text-decoration: none; font-weight: 500; transition: all 0.2s ease; }
        .tm-run-id:hover { color: #4F46E5 !important; text-decoration: underline; }
        .tm-text-cell { color: #000000 !important; font-size: 0.9em; }
        @media (max-width: 1024px) { .tm-leaderboard-table th, .tm-leaderboard-table td { padding: 10px 8px; font-size: 12px; } .tm-hide-mobile { display: none !important; } }
        @media (max-width: 768px) { .tm-leaderboard-table th:nth-child(n+7), .tm-leaderboard-table td:nth-child(n+7) { display: none !important; } .tm-model-name { font-size: 13px; } }
        @media (max-width: 480px) { .tm-leaderboard-table th:nth-child(n+4), .tm-leaderboard-table td:nth-child(n+4) { display: none !important; } .tm-leaderboard-table th:nth-child(3), .tm-leaderboard-table td:nth-child(3) { display: table-cell !important; } }
    </style>

    <div class="tm-leaderboard-container">
        <table class="tm-leaderboard-table">
            <thead>
                <tr>
                    <th style="width: 60px;">Rank</th>
                    <th style="width: 110px;" title="Run ID">Run ID</th>
                    <th style="min-width: 160px;">Model</th>
                    <th style="width: 80px;">Type</th>
                    <th style="width: 90px;">Provider</th>
                    <th style="width: 85px;" title="Hardware used for evaluation: GPU or CPU">Hardware</th>
                    <th style="width: 150px;" title="Percentage of test cases that passed (0-100%). Higher is better.">Success Rate</th>
                    <th style="width: 140px;" class="tm-numeric-cell" title="Tests: Total / Pass / Fail">Tests (P/F)</th>
                    <th style="width: 70px;" class="tm-numeric-cell" title="Average number of steps per test case.">Steps</th>
                    <th style="width: 100px;" class="tm-numeric-cell" title="Average time per test case. Lower is better.">Duration</th>
                    <th style="width: 90px;" class="tm-numeric-cell" title="Total tokens used across all tests.">Tokens</th>
                    <th style="width: 90px;" class="tm-numeric-cell" title="Total API + power costs in USD. Lower is better.">Cost</th>
                    <th style="width: 80px;" class="tm-numeric-cell tm-hide-mobile" title="Carbon footprint in grams of CO2 equivalent.">CO2</th>
                    <th style="width: 100px;" class="tm-hide-mobile" title="Average GPU usage during evaluation (0-100%).">GPU Util</th>
                    <th style="width: 140px;" class="tm-hide-mobile">Timestamp</th>
                    <th style="width: 110px;" class="tm-hide-mobile">Submitted By</th>
                    <th style="width: 100px;">Actions</th> 
                </tr>
            </thead>
            <tbody>
    """

    for idx, row in df_sorted.iterrows():
        rank = idx + 1
        model = row.get("model", "Unknown")
        agent_type = row.get("agent_type", "unknown")
        provider = row.get("provider", "unknown")
        success_rate = row.get("success_rate", 0.0)
        total_tests = row.get("total_tests", 0)
        successful_tests = row.get("successful_tests", 0)
        failed_tests = row.get("failed_tests", 0)
        avg_steps = row.get("avg_steps", 0.0)
        avg_duration_ms = row.get("avg_duration_ms", 0.0)
        total_tokens = row.get("total_tokens", 0)
        total_cost_usd = row.get("total_cost_usd", 0.0)
        co2_emissions_g = row.get("co2_emissions_g", 0.0)
        gpu_utilization_avg = row.get("gpu_utilization_avg", None)
        timestamp = row.get("timestamp", "")
        submitted_by = row.get("submitted_by", "Unknown")
        run_id = row.get("run_id", "N/A")

        has_gpu = pd.notna(gpu_utilization_avg) and gpu_utilization_avg > 0
        gpu_display = (
            get_gpu_utilization_bar(gpu_utilization_avg)
            if has_gpu
            else '<span style="color: #94A3B8; font-size: 0.85em;">N/A</span>'
        )
        co2_display = (
            f"{co2_emissions_g:.2f}g"
            if pd.notna(co2_emissions_g) and co2_emissions_g > 0
            else '<span style="color: #94A3B8; font-size: 0.85em;">N/A</span>'
        )
        timestamp_display = str(timestamp)[:16] if pd.notna(timestamp) else "N/A"
        run_id_short = run_id[:8] + "..." if len(run_id) > 8 else run_id
       
        data_attrs_dict = {
            f"data-{key.replace('_', '-')}": value
            for key, value in row.to_dict().items()
        }
        data_attrs = " ".join(
            [f'{key}="{value}"' for key, value in data_attrs_dict.items()]
        )

        html += f"""
            <tr {data_attrs}>
                <td>{get_rank_badge(rank)}</td>
                <td class="tm-run-id" title="{run_id}">{run_id_short}</td>
                <td class="tm-model-name">{model}</td>
                <td class="tm-badge-cell">{get_agent_type_badge(agent_type)}</td>
                <td class="tm-badge-cell">{get_provider_badge(provider)}</td>
                <td class="tm-badge-cell">{get_hardware_badge(has_gpu)}</td>
                <td>{get_success_rate_bar(success_rate)}</td>
                <td class="tm-numeric-cell">
                    <strong>{total_tests}</strong> / <span style="color: #10B981;">{successful_tests}</span> / <span style="color: #EF4444;">{failed_tests}</span>
                </td>
                <td class="tm-numeric-cell">{avg_steps:.1f}</td>
                <td class="tm-numeric-cell">{format_duration(avg_duration_ms)}</td>
                <td class="tm-numeric-cell">{total_tokens:,}</td>
                <td class="tm-numeric-cell">{format_cost(total_cost_usd)}</td>
                <td class="tm-numeric-cell tm-hide-mobile">{co2_display}</td>
                <td class="tm-hide-mobile">{gpu_display}</td>
                <td class="tm-hide-mobile tm-text-cell">{timestamp_display}</td>
                <td class="tm-hide-mobile tm-text-cell">{submitted_by}</td>
                <td>
                    <button class="tm-action-button" data-action="delete" data-run-id="{run_id}">
                        Delete
                    </button>
                </td>
            </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
    """
    return html
