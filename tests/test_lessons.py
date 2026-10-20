"""Offline regressions for lesson execution boundaries and chat history."""

import importlib
import unittest
from unittest.mock import Mock, patch

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage


class LessonTests(unittest.TestCase):
    """Keep CLI demos runnable and graph imports free of model requests."""

    def test_cli_imports_do_not_construct_models_or_prompt(self):
        """Importing CLI modules must not start an interactive session."""
        with (
            patch("lessons.shared.get_llm") as get_llm,
            patch("builtins.input") as user_input,
        ):
            for name in ("l01_model_only", "l01_model_only_loop"):
                module = importlib.import_module(f"lessons.{name}")
                importlib.reload(module)
        get_llm.assert_not_called()
        user_input.assert_not_called()

    def test_model_only_sends_one_user_request(self):
        """The first demo must invoke the model, without duplicating the user."""
        from lessons.l01_model_only import main

        model = Mock()
        model.invoke.return_value = AIMessage(content="Bake a cake.")
        with (
            patch("lessons.l01_model_only.get_llm", return_value=model),
            patch("builtins.print") as output,
        ):
            main()
        model.invoke.assert_called_once()
        messages = model.invoke.call_args.args[0]
        self.assertEqual([m["role"] for m in messages], ["system", "user"])
        output.assert_called_once_with("Bake a cake.")

    def test_chat_preserves_assistant_messages(self):
        """Later turns retain the original assistant message and its metadata."""
        from lessons.l01_model_only_loop import main

        reply = AIMessage(content="Hello.", response_metadata={"demo": True})
        snapshots = []
        model = Mock()

        def respond(messages):
            snapshots.append(list(messages))
            return reply

        model.invoke.side_effect = respond
        with (
            patch("lessons.l01_model_only_loop.get_llm", return_value=model),
            patch("builtins.input", side_effect=[" ", "Hello", "Again", " EXIT "]),
            patch("builtins.print"),
        ):
            main()
        self.assertEqual(model.invoke.call_count, 2)
        self.assertEqual(len(snapshots[0]), 2)
        self.assertIs(snapshots[1][2], reply)

    def test_chat_handles_closed_input(self):
        """An exhausted input stream exits without requesting a model response."""
        from lessons.l01_model_only_loop import main

        with (
            patch("lessons.l01_model_only_loop.get_llm") as get_llm,
            patch("builtins.input", side_effect=EOFError),
            patch("builtins.print"),
        ):
            main()
        get_llm.return_value.invoke.assert_not_called()

    def test_structured_graph_import_does_not_invoke_model(self):
        """Server graph discovery must not generate an unsolicited report."""
        model = FakeListChatModel(responses=["unused"])
        with (
            patch("lessons.shared.get_llm", return_value=model),
            patch.object(FakeListChatModel, "invoke") as invoke,
            patch("builtins.print") as output,
        ):
            module = importlib.import_module("lessons.l04_structured_output")
            importlib.reload(module)
        invoke.assert_not_called()
        output.assert_not_called()
        self.assertIs(module.graph, module.agent)
