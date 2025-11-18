# Copyright 2019 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the game-specific functions for interstate."""

from absl.testing import absltest
from absl.testing import parameterized

import pyspiel
import json


class GamesInterstateTest(parameterized.TestCase):

    def test_can_create_game(self):
        """Test that the game can be created."""
        game = pyspiel.load_game("interstate")
        self.assertIsNotNone(game)

    def test_default_parameters(self):
        """Test default parameter values."""
        game = pyspiel.load_game("interstate")
        params = game.get_parameters()
        self.assertEqual(params["num_faceup_resource_cards"], 5)

    def test_custom_parameter(self):
        """Test setting a custom parameter value."""
        game = pyspiel.load_game("interstate(num_faceup_resource_cards=7)")
        params = game.get_parameters()
        self.assertEqual(params["num_faceup_resource_cards"], 7)

    @parameterized.parameters(0, 1, 5, 10)
    def test_valid_parameter_values(self, num_cards):
        """Test that valid parameter values are accepted."""
        game = pyspiel.load_game(f"interstate(num_faceup_resource_cards={num_cards})")
        params = game.get_parameters()
        self.assertEqual(params["num_faceup_resource_cards"], num_cards)

    @parameterized.parameters(-1, 11, 100)
    def test_invalid_parameter_values(self, num_cards):
        """Test that invalid parameter values are rejected."""
        with self.assertRaises(RuntimeError) as context:
            pyspiel.load_game(f"interstate(num_faceup_resource_cards={num_cards})")
        self.assertIn(
            "num_faceup_resource_cards must be between 0 and 10", str(context.exception)
        )

    def test_game_starts(self):
        """Test that a game can be started and has initial state."""
        game = pyspiel.load_game("interstate")
        state = game.new_initial_state()
        self.assertIsNotNone(state)
        self.assertFalse(state.is_terminal())

    def test_parameter_affects_game_instances(self):
        """Test that different parameter values create different game configs."""
        game1 = pyspiel.load_game("interstate(num_faceup_resource_cards=3)")
        game2 = pyspiel.load_game("interstate(num_faceup_resource_cards=8)")

        params1 = game1.get_parameters()
        params2 = game2.get_parameters()

        self.assertEqual(params1["num_faceup_resource_cards"], 3)
        self.assertEqual(params2["num_faceup_resource_cards"], 8)
        self.assertNotEqual(params1["num_faceup_resource_cards"], params2["num_faceup_resource_cards"])

    def test_num_nodes_parameter(self):
        """Test the num_nodes parameter."""
        # Test default num_nodes
        game_default = pyspiel.load_game("interstate")
        params_default = game_default.get_parameters()
        self.assertEqual(params_default["num_nodes"], 14)

        # Test custom num_nodes
        game_custom = pyspiel.load_game("interstate(num_nodes=20)")
        params_custom = game_custom.get_parameters()
        self.assertEqual(params_custom["num_nodes"], 20)

    def test_multiple_parameters(self):
        """Test setting multiple parameters at once."""
        game = pyspiel.load_game("interstate(num_nodes=20,num_faceup_resource_cards=3)")
        params = game.get_parameters()
        self.assertEqual(params["num_nodes"], 20)
        self.assertEqual(params["num_faceup_resource_cards"], 3)

    def test_edges_parameter_with_json_string(self):
        """Test edges parameter with JSON string."""
        edges_data = [
            {
                "nodes": [0, 5],
                "paths": [
                    {
                        "score": 10,
                        "segments": [
                            {"resource": None},
                            {"resource": None},
                        ],
                    }
                ],
            },
            {
                "nodes": [3, 7],
                "paths": [
                    {
                        "score": 20,
                        "segments": [{"resource": 3}] * 6,
                    },
                    {
                        "score": 15,
                        "segments": [{"resource": 2}] * 6,
                    },
                ],
            },
        ]
        edges_json = json.dumps(edges_data)
        goals_data = [
            {"nodes": [1, 2], "score": 10},
            {"nodes": [4, 5], "score": 15},
        ]
        goals_json = json.dumps(goals_data)
        resource_deck = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
        ]
        resource_deck_json = json.dumps(resource_deck)
        game = pyspiel.load_game(
            "interstate",
            {
                "num_faceup_resource_cards": 3,
                "num_nodes": 30,
                "num_resources": 4,
                "edges": edges_json,
                "resource_deck": resource_deck_json,
                "wild_resources": "[2,3]",
                "goals": goals_json,
                "num_player_pieces": 30,
            },
        )
        self.assertIsNotNone(game)
        state = game.new_initial_state()
        self.assertIsNotNone(state)


if __name__ == "__main__":
    absltest.main()
