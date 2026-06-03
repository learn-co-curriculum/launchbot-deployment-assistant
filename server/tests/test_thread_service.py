from app.services.thread_service import add_message, create_thread, get_thread, list_threads


def test_create_thread_and_add_messages(tmp_path):
    database_path = str(tmp_path / "launchbot.sqlite")

    thread = create_thread(database_path)
    add_message(
        database_path,
        thread_id=thread["id"],
        role="user",
        content="Why does localhost not work for my friend?",
    )
    assistant = add_message(
        database_path,
        thread_id=thread["id"],
        role="assistant",
        content="localhost points to the computer making the request.",
        metadata={"sources": [{"source_id": "DEP-101"}]},
    )

    stored = get_thread(database_path, thread["id"])

    assert stored["thread"]["title"].startswith("Why does localhost")
    assert len(stored["messages"]) == 2
    assert assistant["metadata"]["sources"][0]["source_id"] == "DEP-101"


def test_list_threads_orders_by_updated_at(tmp_path):
    database_path = str(tmp_path / "launchbot.sqlite")

    first = create_thread(database_path, title="First")
    second = create_thread(database_path, title="Second")

    add_message(database_path, thread_id=first["id"], role="user", content="Update first")

    threads = list_threads(database_path)

    assert threads[0]["id"] == first["id"]
    assert {thread["id"] for thread in threads} == {first["id"], second["id"]}
