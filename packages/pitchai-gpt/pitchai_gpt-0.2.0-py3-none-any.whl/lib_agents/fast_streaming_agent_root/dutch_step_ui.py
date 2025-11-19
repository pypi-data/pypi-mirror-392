import html
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader

from .step_describer import describe_step_in_dutch

if TYPE_CHECKING:
    from .step_state import StepContainerState


PROJECT_ROOT = Path(__file__).resolve().parents[5]
TEMPLATE_DIR = PROJECT_ROOT / "apps" / "web_app" / "src" / "web_app" / "web" / "templates"
JINJA_ENV = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


async def generate_and_display_dutch_step_ui(
    agent: Any,
    step_number: int,
    state: "StepContainerState",
    code: str,
    language: str
) -> None:
    if not state.step_ids_set:
        state.step_id = f"step-{step_number}"
        state.title_dutch_id = f"{state.step_id}-dutch"
        state.badge_id = f"{state.step_id}-badge"
        state.reasoning_id = f"{state.step_id}-reasoning"
        state.code_id = f"{state.step_id}-code"
        state.output_id = f"{state.step_id}-output"
        state.reasoning_container_id = f"content-{state.step_id}-reasoning-container"
        state.code_container_id = f"content-{state.step_id}-code-container"
        state.output_container_id = f"content-{state.step_id}-output-container"
        state.step_ids_set = True

        if not state.step_container_sent:
            template = JINJA_ENV.get_template("components/agent_step_container.html")
            template_html = template.render(state=state, loading_emoji="⏳")
            await agent.shared_ui_msg.set_content_instantly(
                template_html,
                property="content",
                overwrite=False,
                to_main_process=True,
                pipeline_id=getattr(agent, "conversation_id", None),
                requester_id=agent.agent_id
            )
            state.step_container_sent = True

    if state.step_ids_set and state.step_reasoning_buffer:
        current_reasoning = state.step_reasoning_buffer.strip()
    else:
        current_reasoning = re.sub(r"```.*?```", "", state.assistant_content, flags=re.DOTALL).strip()
        current_reasoning = re.sub(r"<output>.*?</output>", "", current_reasoning, flags=re.DOTALL).strip()

    dutch_description = await describe_step_in_dutch(
        original_question=agent.original_user_query,
        step_reasoning=current_reasoning,
        step_code="",
        step_output="",
        model=agent.config.dutch_step_descriptions.model
    )

    if dutch_description:
        agent._schedule_task(
            agent.shared_ui_msg.stream_into(
                dutch_description + "\n",
                property="content",
                stream_insert_id=state.title_dutch_id,
                overwrite=True,
                speed=0.01,
                skip_grpc=True,
                requester_id=agent.agent_id,
            ),
            track=True,
        )

        await agent.shared_ui_msg.broadcast_update_badge(
            element_id=f"content-{state.badge_id}",
            status="writing",
            html='<i class="fa-solid fa-pencil mr-1.5"></i> Schrijven'
        )

        await agent.shared_ui_msg.broadcast_show_element(f"{state.code_container_id}")

        escaped_code = html.escape(code)
        await agent.shared_ui_msg.msg_mngr.broadcast_event(agent.conversation_id, {
            "event": f"content-{state.code_id}",
            "data": f'<pre><code class="language-python">{escaped_code}</code></pre>'
        })

    if dutch_description and not (hasattr(agent, "waiting_for_final_answer") and agent.waiting_for_final_answer):
        from .ui_helpers import push_action_to_panel
        await push_action_to_panel(
            agent=agent,
            dutch_description=dutch_description,
            shared_ui_msg=agent.shared_ui_msg,
            agent_id=agent.agent_id,
            conversation_id=getattr(agent, "conversation_id", None)
        )
