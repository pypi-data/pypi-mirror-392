// Copyright 2021 DeepMind Technologies Limited
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <memory>

#include "open_spiel/abseil-cpp/absl/flags/flag.h"
#include "open_spiel/abseil-cpp/absl/flags/parse.h"
#include "open_spiel/spiel.h"
#include "open_spiel/tests/console_play_test.h"

ABSL_FLAG(std::string, game, "tic_tac_toe", "The name of the game to play.");
ABSL_FLAG(int, players, 0, "How many players in this game, 0 for default.");

int main(int argc, char** argv) {
  absl::ParseCommandLine(argc, argv);

  std::string game_name = absl::GetFlag(FLAGS_game);
  auto players = absl::GetFlag(FLAGS_players);

  // Print out registered games.
  std::cout << "Registered games:" << std::endl;
  std::vector<std::string> names = open_spiel::RegisteredGames();
  for (const std::string& name : names) {
    std::cout << name << std::endl;
  }
  std::cout << std::endl;

  // Create the game.
  std::cout << "Creating game: " << game_name << std::endl << std::endl;

  // Add any specified parameters to override the defaults.
  open_spiel::GameParameters params;
  if (players > 0) {
    params["players"] = open_spiel::GameParameter(players);
  }
  std::shared_ptr<const open_spiel::Game> game =
      open_spiel::LoadGame(game_name, params);

  if (!game) {
    std::cerr << "Problem with loading game, exiting..." << std::endl;
    return -1;
  }

  std::cout << "Starting console playthrough..." << std::endl;
  std::cout << "Type a move number or action string to make a move." << std::endl;
  std::cout << "Press enter for help menu." << std::endl << std::endl;

  // Start the console playthrough with human player
  open_spiel::testing::ConsolePlayTest(*game);

  return 0;
}
