from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from backend.vectorstore.retriever import get_retriever
from backend.tools.preference_tool import get_preference_tool
from backend.tools.anime_search import get_anime_search_tool
from config.settings import settings
from config.logging import get_logger
from config.customException import CustomException

logger = get_logger(__name__)

_llm = ChatGroq(
    model=settings.groq_llm_model,
    api_key=settings.groq_api_key,
    temperature=0.3,
)

_prompt = hub.pull("hwchase17/react-chat")


def build_agent(content_type: str | None = None) -> AgentExecutor:
    """Build recommendation agent scoped to content_type."""
    try:
        tools = [
            get_preference_tool(),
            get_anime_search_tool(content_type=content_type),
        ]

        agent = create_react_agent(
            llm=_llm,
            tools=tools,
            prompt=_prompt,
        )

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )

    except Exception as e:
        logger.error("Failed to build agent: %s", e)
        raise CustomException("Failed to build anime agent", e)


def run_agent(
    user_input: str,
    chat_history: str = "",
    content_type: str | None = None,
) -> dict:
    """
    Execute recommendation agent.

    Returns:
        {
            "answer": "...",
            "sources": [...]
        }
    """
    try:
        logger.info(
            "Running agent | content_type=%s | input=%s",
            content_type,
            user_input,
        )

        executor = build_agent(content_type=content_type)

        agent_input = (
            f"Chat History:\n{chat_history}\n\n"
            f"User Request:\n{user_input}\n\n"
            "Instructions:\n"
            "1. Use preference_extractor to understand user preferences.\n"
            "2. Use anime_search to find relevant titles.\n"
            "3. Recommend the best matches with reasoning."
        )

        result = executor.invoke({"input": agent_input})
        answer = result.get("output", "")

        retriever = get_retriever(content_type=content_type, k=5)
        docs = retriever.invoke(user_input)
        sources = [doc.metadata for doc in docs]

        logger.info("Agent completed successfully")

        return {
            "answer": answer,
            "sources": sources,
        }

    except Exception as e:
        logger.error("Agent execution failed: %s", e)
        raise CustomException("Failed to run recommendation agent", e)
