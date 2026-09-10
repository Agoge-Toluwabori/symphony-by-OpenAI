defmodule SymphonyElixir.Codex.FactoryContext do
  @moduledoc "Host dispatch attestation combined with IDs from the live App Server protocol."
  require Logger

  @spec spec() :: map()
  def spec do
    %{
      "name" => "factory_context",
      "description" => "Verify service dispatch, approved batch, workspace, preflight and actual App Server session before claiming work. No arguments or host access required.",
      "inputSchema" => %{"type" => "object", "properties" => %{}, "additionalProperties" => false}
    }
  end

  @spec execute(term(), keyword()) :: map()
  def execute(arguments, opts) do
    path = System.get_env("AGOGE_FACTORY_ATTESTATION") || ""
    decoded = with {:ok, bytes} <- File.read(path), {:ok, value} <- Jason.decode(bytes), do: value
    context = if is_map(decoded), do: decoded, else: %{}
    issue = Keyword.fetch!(opts, :issue)
    session = Keyword.fetch!(opts, :session)
    invocation = System.get_env("INVOCATION_ID")

    fields = %{
      "arguments" => status(arguments == %{}, false),
      "issue_id" => status(context["issue_id"] == issue.id, is_nil(context["issue_id"])),
      "workspace" => status(context["workspace"] == session.workspace, is_nil(context["workspace"])),
      "service_identity" => status(context["service"] == "symphony-agoge.service", is_nil(context["service"])),
      "dispatch_invocation" => status(is_binary(invocation) and context["invocation_id"] == invocation, is_nil(context["invocation_id"])),
      "approved_batch" =>
        status(
          ({context["batch"], issue.id} in [{"factory-v1-containment-canary", "236"}, {"factory-v1-publication-guard", "235"}] or continuous?(context)) and
            context["authority"] == "Autonomous Development",
          is_nil(context["batch"])
        ),
      "concurrency" => status(context["max_concurrency"] == 1, is_nil(context["max_concurrency"])),
      "native_preflight" =>
        status(is_map(context["preflight"]) and map_size(context["preflight"]) > 0 and Enum.all?(context["preflight"], fn {_, value} -> value == "verified" end), is_nil(context["preflight"])),
      "session_id" => status(is_binary(session.thread_id) and is_binary(session.turn_id), false)
    }

    Enum.each(fields, fn {field, state} ->
      Logger.info("Factory preflight issue_id=#{issue.id} session_id=#{session.thread_id}-#{session.turn_id} field=#{field} status=#{state}")
    end)

    success = Enum.all?(fields, fn {_, state} -> state == "verified" end)

    result = %{
      "verified" => success,
      "fields" => fields,
      "dispatch" => context,
      "thread_id" => session.thread_id,
      "turn_id" => session.turn_id,
      "session_id" => "#{session.thread_id}-#{session.turn_id}",
      "post_run_verification" => "Host supervisor verifies batch stop after completion; not a pre-claim dependency"
    }

    text = Jason.encode!(result)
    %{"success" => success, "output" => text, "contentItems" => [%{"type" => "inputText", "text" => text}]}
  end

  defp continuous?(context),
    do: context["mode"] == "continuous" and context["batch"] == "continuous-project-authority" and is_binary(context["lease_nonce"])

  defp status(true, _missing), do: "verified"
  defp status(false, true), do: "missing"
  defp status(false, false), do: "invalid"
end
