"""Helpers for generating forked suggestions for the FastStreamingAgent."""

import copy
import re
from typing import Iterable, Optional


def _extract_tag_values(response: str, tag_names: Iterable[str]) -> list[str]:
    """Return contents for any of the provided tag names (case-insensitive)."""
    values: list[str] = []
    for tag in tag_names:
        if not tag:
            continue
        pattern = rf"<{tag}>(.*?)</{tag}>"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        if matches:
            values.extend(matches)
    return values


async def generate_and_stream_suggestions(
    agent_instance,
    conversation_id: str,
    user_question: str = "",
    analysis_result: str = ""
) -> None:
    """Generate suggestions and stream them to the UI."""

    print("🔧 SUGGESTIONS: Starting suggestion generation")

    response_text: Optional[str] = None
    if hasattr(agent_instance, "fork_manager"):
        fork_result = await agent_instance.fork_manager.generate("suggestions")
        if fork_result and fork_result.generated_text.strip():
            response_text = fork_result.generated_text
            print("🔧 SUGGESTIONS: Generated response via forked prompt")

    if response_text is None:
        print("🔧 SUGGESTIONS: Using legacy suggestion prompt.")
        response_text = await _legacy_generate_suggestions(agent_instance)

    response = response_text.strip()
    if not response:
        raise ValueError("Suggestion generation returned empty output.")

    questions = _extract_tag_values(response, ("vraag", "question"))
    plots = _extract_tag_values(response, ("grafiek", "chart"))

    print(f"🔧 SUGGESTIONS: Found {len(questions)} questions and {len(plots)} plots")
    print(f"🔧 SUGGESTIONS: conversation_id = {conversation_id}")
    print(f"🔧 SUGGESTIONS: has shared_ui_msg = {hasattr(agent_instance, 'shared_ui_msg')}")
    if hasattr(agent_instance, 'shared_ui_msg') and agent_instance.shared_ui_msg:
        print(f"🔧 SUGGESTIONS: shared_ui_msg.id = {getattr(agent_instance.shared_ui_msg, 'id', 'NO ID')}")

    if conversation_id and hasattr(agent_instance, 'shared_ui_msg') and agent_instance.shared_ui_msg:
        await stream_suggestions_to_ui(agent_instance.shared_ui_msg, questions, plots)
    else:
        print("🔧 SUGGESTIONS: No shared_ui_msg available for streaming - suggestions will not appear in UI")

    if questions:
        print("🔧 SUGGESTIONS: Questions generated:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q.strip()}")

    if plots:
        print("🔧 SUGGESTIONS: Plots generated:")
        for i, p in enumerate(plots, 1):
            print(f"  {i}. {p.strip()}")


async def _legacy_generate_suggestions(agent_instance) -> str:
    """Fallback behaviour using the historical suggestion prompts."""
    try:
        system_prompt = """Je bent een expert die contextuele suggesties genereert na data-analyse.

Je taak is om gebaseerd op de vorige conversatie:
1. **Genereer 3 vervolgvragen** die logisch voortvloeien uit de analyse
2. **Stel 2-3 relevante grafiektypes** voor die de data kunnen visualiseren

**Output Format - gebruik dit EXACTE XML formaat:**

<vervolgvragen>
<vraag>Eerste vervolgvraag</vraag>
<vraag>Tweede vervolgvraag</vraag>
<vraag>Derde vervolgvraag</vraag>
</vervolgvragen>

<grafieken>
<grafiek>Eerste grafiektype</grafiek>
<grafiek>Tweede grafiektype</grafiek>
</grafieken>

Houd de suggesties relevant voor de GZB context (donaties, relaties, financiële data).
Wees beknopt en direct."""

        user_prompt = "Genereer beknopte suggesties voor vervolgvragen en grafiektypes gebaseerd op de analyse."

        messages_copy = []
        for original in copy.deepcopy(agent_instance.messages):
            role = original.get("role")
            content = original.get("content")
            if role == "tool":
                messages_copy.append({"role": "user", "content": content})
                continue

            sanitized = {"role": role}
            if content is not None:
                sanitized["content"] = content
            messages_copy.append(sanitized)
        messages_copy.append({"role": "system", "content": system_prompt})
        messages_copy.append({"role": "user", "content": user_prompt})

        from gpt.gpt import GPT

        gpt = GPT(model=agent_instance.config.suggestions_model)
        response = await gpt.get_text_response(
            msg_list=messages_copy,
            silent=True,
            return_raw_stream=False,
        )
        return response
    except Exception as exc:  # pragma: no cover - defensive
        print(f"🔧 SUGGESTIONS: Legacy generation error: {exc}")
        import traceback

        traceback.print_exc()
        raise


async def stream_suggestions_to_ui(shared_ui_msg, questions: list, plots: list):
    """
    Stream subtle suggestions HTML to the plot-suggestions section of the message.
    
    Args:
        shared_ui_msg: The shared UI message object from FastStreamingAgent
        questions: List of follow-up questions
        plots: List of plot suggestions
    """
    try:
        print(f"🔧 SUGGESTIONS: Starting to stream to UI")
        print(f"🔧 SUGGESTIONS: shared_ui_msg.id = {getattr(shared_ui_msg, 'id', 'NO ID')}")
        print(f"🔧 SUGGESTIONS: Questions to stream: {len(questions)}")
        print(f"🔧 SUGGESTIONS: Plots to stream: {len(plots)}")
        
        # Build subtle HTML for suggestions (similar to instant mode buttons style)
        template_name = getattr(shared_ui_msg, "template_name", "") or ""
        is_mini_mode = "chat_msg_mini" in template_name
        chat_config = getattr(shared_ui_msg, "chat_config", {}) or {}
        if isinstance(chat_config, dict):
            chat_config_id = chat_config.get("id") or chat_config.get("chatconfig_id") or ""
        else:
            chat_config_id = getattr(chat_config, "id", "") or getattr(chat_config, "chatconfig_id", "")

        escaped_chat_config_id = str(chat_config_id or "").replace('"', '&quot;').replace("'", '&#39;')

        def build_instant_hx_vals(escaped_content: str) -> str:
            return (
                "js:{{content: \"{content}\", lastEventId: getLastEventId(), "
                "chatconfig_id: \"\", is_enter_submit: true}}"
            ).format(content=escaped_content)

        def build_mini_hx_vals(escaped_content: str, template_value: str) -> str:
            return (
                "js:{{content: \"{content}\", lastEventId: getLastEventId(), "
                "chatconfig_id: \"{chatconfig}\", template_name: \"{template}\", "
                "chat_mode: \"thinking\", is_enter_submit: true}}"
            ).format(
                content=escaped_content,
                chatconfig=escaped_chat_config_id,
                template=template_value,
            )

        suggestions_html = """
<div class="w-full mt-4 space-y-3">
  <!-- Subtle header -->
  <div class="flex items-center gap-2 text-xs text-gray-500">
    <i class="fas fa-lightbulb"></i>
    <span>Suggesties voor vervolganalyse</span>
  </div>
  
  <!-- Questions section -->
  <div class="flex flex-wrap gap-2">
"""
        
        # Add question buttons - auto-send on click using HTMX
        for i, question in enumerate(questions):
            clean_question = question.strip()
            # Escape for HTML attributes (replace quotes and newlines)
            escaped_question = clean_question.replace('"', '&quot;').replace("'", '&#39;').replace('\n', ' ')
            truncated = clean_question[:50] + ('...' if len(clean_question) > 50 else '')
            # Get conversation_id from shared_ui_msg if available
            conversation_id = getattr(shared_ui_msg, 'conversation_id', 'unknown')
            if is_mini_mode:
                hx_post = f"/send_msg_mini/{conversation_id}"
                hx_target = "#msg-container"
                template_value = (template_name or "").replace('"', '&quot;').replace("'", '&#39;') or "components/chat_msgs/chat_msg_mini.html"
                hx_vals = build_mini_hx_vals(escaped_question, template_value)
            else:
                hx_post = f"/instant_send_message/{conversation_id}"
                hx_target = "#init-ui-container"
                hx_vals = build_instant_hx_vals(escaped_question)
            suggestions_html += f"""
    <button
      type="button"
      class="btn btn-xs bg-gray-50 hover:bg-gray-100 text-gray-600 hover:text-gray-800 border border-gray-200 hover:border-gray-300 transition-all"
      style="box-shadow: none; --btn-shadow: none;"
      hx-post="{hx_post}"
      hx-vals='{hx_vals}'
      hx-target="{hx_target}"
      hx-swap="beforeend"
      title="Klik om deze vraag direct te stellen"
    >
      <i class="fas fa-question-circle text-xs mr-1"></i>
      {truncated}
    </button>
"""
        
        # Add plot buttons - auto-send with hidden prompt
        for i, plot in enumerate(plots):
            clean_plot = plot.strip()
            # Visible prompt for UI
            visible_prompt = f"Maak een {clean_plot.lower()}"
            # Hidden prompt with additional instructions for better plot generation
            hidden_instructions = (" You can create plots using matplotlib (plt) or plotly. "
                                  "Store your figure in a variable (e.g., fig, chart, sales_plot). "
                                  "Then embed it using <embed>{variable_name}</embed> in your final answer. "
                                  "For matplotlib: import matplotlib.pyplot as plt, create figure with plt.subplots(), do NOT call plt.show(). "
                                  "For plotly: import plotly.express as px, create with px.bar/line/scatter etc. "
                                  "The plots will be interactive with zoom/pan capabilities. "
                                  "Verify your data before plotting by checking shapes and ranges.")
            # Full prompt = visible + hidden
            full_plot_request = visible_prompt + hidden_instructions
            # Escape for HTML attributes
            escaped_request = full_plot_request.replace('"', '&quot;').replace("'", '&#39;').replace('\n', ' ')
            # Get conversation_id from shared_ui_msg if available
            conversation_id = getattr(shared_ui_msg, 'conversation_id', 'unknown')
            if is_mini_mode:
                hx_post = f"/send_msg_mini/{conversation_id}"
                hx_target = "#msg-container"
                template_value = (template_name or "").replace('"', '&quot;').replace("'", '&#39;') or "components/chat_msgs/chat_msg_mini.html"
                hx_vals = build_mini_hx_vals(escaped_request, template_value)
            else:
                hx_post = f"/instant_send_message/{conversation_id}"
                hx_target = "#init-ui-container"
                hx_vals = build_instant_hx_vals(escaped_request)
            suggestions_html += f"""
    <button
      type="button"
      class="btn btn-xs bg-green-50 hover:bg-green-100 text-green-600 hover:text-green-700 border border-green-200 hover:border-green-300 transition-all"
      style="box-shadow: none; --btn-shadow: none;"
      hx-post="{hx_post}"
      hx-vals='{hx_vals}'
      hx-target="{hx_target}"
      hx-swap="beforeend"
      title="Klik om deze grafiek direct te maken"
    >
      <i class="fas fa-chart-bar text-xs mr-1"></i>
      {clean_plot}
    </button>
"""
        
        suggestions_html += """
  </div>
</div>
"""
        
        conversation_id = getattr(shared_ui_msg, "conversation_id", None)
        if not conversation_id:
            raise ValueError("Shared UI message is missing conversation_id; cannot stream suggestions.")

        event_name = f"suggestions-panel-{conversation_id}-overwrite"
        await shared_ui_msg.msg_mngr.broadcast_event(
            conversation_id,
            {
                "event": event_name,
                "data": suggestions_html,
            },
        )
        print(f"🔧 SUGGESTIONS: Broadcast suggestions event {event_name}")

    except Exception as e:
        print(f"🔧 SUGGESTIONS: Error streaming to UI: {e}")
        import traceback
        traceback.print_exc()
