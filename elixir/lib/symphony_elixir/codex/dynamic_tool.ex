defmodule SymphonyElixir.Codex.DynamicTool do
  @moduledoc """
  Dispatches client-side tool calls to the configured tracker adapter.
  """

  alias SymphonyElixir.{Codex.FactoryContext, Tracker}

  @spec execute(String.t() | nil, term(), map(), keyword()) :: map()
  def execute(tool, arguments, binding, opts \\ []) do
    if tool == "factory_context" and factory?(binding) do
      FactoryContext.execute(arguments, opts)
    else
      Tracker.execute_bound_agent_tool(binding, tool, arguments, opts)
    end
  end

  @spec bind() :: map()
  def bind do
    binding = Tracker.bind_agent_tools()

    if factory?(binding) do
      Map.update!(binding, :tool_specs, &(&1 ++ [FactoryContext.spec()]))
    else
      binding
    end
  end

  defp factory?(binding) do
    Map.get(binding.tracker_settings.provider, "agent_policy") == "agoge-factory-v1"
  end
end
