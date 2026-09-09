defmodule SymphonyElixir.FactoryContextTest do
  use SymphonyElixir.TestSupport
  alias SymphonyElixir.Codex.{DynamicTool, FactoryContext}

  test "missing evidence reproduces the pre-claim failure; actual protocol IDs repair it" do
    path = Path.join(System.tmp_dir!(), "factory-context-#{System.unique_integer([:positive])}.json")
    old_path = System.get_env("AGOGE_FACTORY_ATTESTATION")
    old_invocation = System.get_env("INVOCATION_ID")
    System.put_env("AGOGE_FACTORY_ATTESTATION", path)
    System.put_env("INVOCATION_ID", "service-invocation")

    on_exit(fn ->
      if old_path, do: System.put_env("AGOGE_FACTORY_ATTESTATION", old_path), else: System.delete_env("AGOGE_FACTORY_ATTESTATION")
      if old_invocation, do: System.put_env("INVOCATION_ID", old_invocation), else: System.delete_env("INVOCATION_ID")
      File.rm(path)
    end)

    opts = [issue: %{id: "236"}, session: %{workspace: "/workspaces/GH-236", thread_id: "real-thread", turn_id: "real-turn"}]
    assert %{"success" => false, "output" => output} = FactoryContext.execute(%{}, opts)
    assert Jason.decode!(output)["fields"]["service_identity"] == "missing"

    context = %{
      "issue_id" => "236",
      "workspace" => "/workspaces/GH-236",
      "service" => "symphony-agoge.service",
      "invocation_id" => "service-invocation",
      "batch" => "factory-v1-containment-canary",
      "authority" => "Autonomous Development",
      "max_concurrency" => 1,
      "preflight" => %{"native_policy" => "verified"}
    }

    File.write!(path, Jason.encode!(context))
    binding = %{tracker_settings: %{provider: %{"agent_policy" => "agoge-factory-v1"}}}
    assert %{"success" => true, "output" => output} = DynamicTool.execute("factory_context", %{}, binding, opts)
    result = Jason.decode!(output)
    assert result["session_id"] == "real-thread-real-turn"
    assert result["fields"]["session_id"] == "verified"
    refute Map.has_key?(result["fields"], "batch_already_stopped")
    assert %{"success" => false} = FactoryContext.execute(%{"issue_id" => "235"}, opts)
    File.write!(path, Jason.encode!(Map.put(context, "issue_id", "235")))
    assert %{"success" => false, "output" => output} = FactoryContext.execute(%{}, opts)
    assert Jason.decode!(output)["fields"]["issue_id"] == "invalid"
    root = path <> "-workspace"
    workspace = Path.join(root, "GH-236")
    File.mkdir_p!(workspace)
    on_exit(fn -> File.rm_rf(root) end)
    executable = Path.join(root, "fake-app-server.py")
    response_path = Path.join(root, "response.json")

    File.write!(executable, """
    import json,sys
    for line in sys.stdin:
      message=json.loads(line)
      method=message.get('method')
      if method=='initialize':
        print(json.dumps({'id':message['id'],'result':{}}),flush=True)
      elif method=='thread/start':
        assert any(t['name']=='factory_context' for t in message['params']['dynamicTools'])
        print(json.dumps({'id':message['id'],'result':{'thread':{'id':'protocol-thread'}}}),flush=True)
      elif method=='turn/start':
        print(json.dumps({'id':message['id'],'result':{'turn':{'id':'protocol-turn'}}}),flush=True)
        print(json.dumps({'id':900,'method':'item/tool/call','params':{'tool':'factory_context','callId':'context-call','arguments':{}}}),flush=True)
      elif message.get('id')==900:
        with open(#{inspect(response_path)},'w') as output: json.dump(message,output)
        print(json.dumps({'method':'turn/completed'}),flush=True)
        break
    """)

    File.write!(path, Jason.encode!(Map.put(context, "workspace", workspace)))

    write_workflow_file!(Workflow.workflow_file_path(),
      workspace_root: root,
      tracker_kind: "github",
      tracker_active_states: ["open"],
      tracker_terminal_states: ["closed"],
      codex_command: "python3 #{executable}"
    )

    workflow = File.read!(Workflow.workflow_file_path())

    File.write!(
      Workflow.workflow_file_path(),
      String.replace(workflow, "tracker:\n", "tracker:\n  provider:\n    repo: Agoge-Toluwabori/Agoge-Business-Systems\n    token: fixture-token\n    agent_policy: agoge-factory-v1\n")
    )

    assert :ok = SymphonyElixir.WorkflowStore.force_reload()
    issue = %Issue{id: "236", identifier: "GH-236", title: "Context regression", state: "open"}
    assert {:ok, %{session_id: "protocol-thread-protocol-turn"}} = AppServer.run(workspace, "Verify context", issue)
    response = response_path |> File.read!() |> Jason.decode!()
    assert response["result"]["success"]
    evidence = Jason.decode!(response["result"]["output"])
    assert evidence["session_id"] == "protocol-thread-protocol-turn"
    assert FactoryContext.spec()["name"] == "factory_context"
  end
end
