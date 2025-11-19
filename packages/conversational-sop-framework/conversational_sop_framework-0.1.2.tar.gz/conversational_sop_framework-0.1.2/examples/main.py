from conversational_sop import WorkflowTool

config = {
    "model_config": {
        "base_url_mapping": {"gpt-oss-safeguard-20b-mlx": "http://192.168.1.73:1234/v1"},
        "model": "gpt-oss-safeguard-20b-mlx",
        "api_key": lambda : "test"
    }
}

tool = WorkflowTool(
    yaml_path="./greeting_workflow.yaml",
    name="test",
    description="test",
    checkpointer=None,
    config=config
)

if __name__ == "__main__" :
    while True :
        query = input("Enter: ")

        result = tool.execute(
            thread_id="test_thread_1",
            user_message=query,
            initial_context=None
        )

        print(result)