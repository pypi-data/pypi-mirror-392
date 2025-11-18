// Copyright 2019 DeepMind Technologies Limited
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

#ifndef OPEN_SPIEL_GAMES_INTERSTATE_H_
#define OPEN_SPIEL_GAMES_INTERSTATE_H_

#include <array>
#include <memory>
#include <string>
#include <tuple>
#include <vector>

#include "open_spiel/abseil-cpp/absl/types/optional.h"
#include "open_spiel/abseil-cpp/absl/types/span.h"
#include "open_spiel/json/include/nlohmann/json.hpp"
#include "open_spiel/spiel_utils.h"
#include "open_spiel/spiel.h"

// Simple game of Noughts and Crosses:
// https://en.wikipedia.org/wiki/Tic-tac-toe
//
// Parameters: none

namespace open_spiel
{
    namespace interstate
    {

        // Constants.
        inline constexpr int kNumPlayers = 2;
        inline constexpr int kNumRows = 3;
        inline constexpr int kNumCols = 3;
        inline constexpr int kNumCells = kNumRows * kNumCols;
        inline constexpr int kCellStates = 1 + kNumPlayers; // empty, 'x', and 'o'.

        // https://math.stackexchange.com/questions/485752/tictactoe-state-space-choose-calculation/485852
        inline constexpr int kNumberStates = 5478;

        // State of a cell.
        enum class CellState
        {
            kEmpty,
            kNought, // O
            kCross,  // X
        };

        // Card structure
        struct Card
        {
            int idx;
            int deck_idx;
            absl::optional<int> resource_idx;
            absl::optional<int> goal_idx;

            Card() = default;
            Card(int idx_, int deck_idx_, absl::optional<int> resource_idx_,
                 absl::optional<int> goal_idx_ = absl::nullopt)
                : idx(idx_), deck_idx(deck_idx_), resource_idx(resource_idx_), goal_idx(goal_idx_) {}
        };

        // Deck structure
        struct Deck
        {
            int idx;
            std::vector<Card> cards;

            Deck() : idx(0), cards() {}

            // Constructor that takes a vector of resource indices
            Deck(const std::vector<int>& resource_indices, int deck_idx = 0)
                : idx(deck_idx), cards()
            {
                cards.reserve(resource_indices.size());
                for (size_t i = 0; i < resource_indices.size(); ++i) {
                    cards.emplace_back(i, deck_idx, resource_indices[i], absl::nullopt);
                }
            }
        };

        // Resource structure
        struct Resource
        {
            int idx;
            bool is_wild;
        };

        // Goal structure
        struct Goal
        {
            int idx;
            std::vector<int> node_idxs;
            int score;
        };

        // Node structure
        struct Node
        {
            int idx;
        };

        // Segment structure
        struct Segment
        {
            int idx;
            absl::optional<int> resource_idx;
            absl::optional<std::tuple<int, int>> piece;

            Segment(int idx_, absl::optional<int> resource_idx_ = absl::nullopt,
                   absl::optional<std::tuple<int, int>> piece_ = absl::nullopt)
                : idx(idx_), resource_idx(resource_idx_), piece(piece_) {}

            std::string ToString() const;
        };

        // Path structure
        struct Path
        {
            int idx;
            std::vector<Segment> segments;
            int score;

            Path(int idx_, std::vector<Segment> segments_, int score_ = 0)
                : idx(idx_), segments(std::move(segments_)), score(score_) {}

            std::string ToString() const;
        };

        // Edge structure
        struct Edge
        {
            int idx;
            int node_1_idx;
            int node_2_idx;
            std::vector<Path> paths;

            Edge() = default;
            Edge(int idx_, int node_1_idx_, int node_2_idx_, std::vector<Path> paths_)
                : idx(idx_), node_1_idx(node_1_idx_), node_2_idx(node_2_idx_), paths(std::move(paths_)) {}

            std::string ToString() const;
        };

        // Faceup card stack structure
        struct FaceupCardStack
        {
            std::vector<std::tuple<int, int>> cards;
        };

        // Faceup card spread structure
        struct FaceupCardSpread
        {
            std::vector<absl::optional<std::tuple<int, int>>> spots;
        };

        // Facedown card stack structure
        struct FacedownCardStack
        {
            std::vector<std::tuple<int, int>> cards;
        };

        // Facedown card spread structure
        struct FacedownCardSpread
        {
            std::vector<absl::optional<std::tuple<int, int>>> spots;
        };

        // Deck status structure
        struct DeckStatus
        {
            int idx;
            FaceupCardStack faceup_stack;
            FaceupCardSpread faceup_spread;
            FacedownCardStack facedown_stack;
            FacedownCardSpread facedown_spread;
            FaceupCardStack discard_faceup_stack;
            FacedownCardStack discard_facedown_stack;
        };

        // Player info structure
        struct PlayerInfo
        {
            int idx;
            std::vector<std::tuple<int, int>> pieces;
            std::vector<std::tuple<int, int>> cards;
            std::vector<std::tuple<int, int>> discard_tray;
        };

        struct InterstateStateStruct : StateStruct
        {
            std::string current_player;
            std::vector<std::string> board;

            InterstateStateStruct() = default;
            explicit InterstateStateStruct(const std::string &json_str)
            {
                nlohmann::json::parse(json_str).get_to(*this);
            }

            nlohmann::json to_json_base() const override
            {
                return *this;
            }
            NLOHMANN_DEFINE_TYPE_INTRUSIVE(InterstateStateStruct, current_player, board);
        };

        // State of an in-play game.
        class InterstateState : public State
        {
        public:
            InterstateState(std::shared_ptr<const Game> game);

            InterstateState(const InterstateState &) = default;
            InterstateState &operator=(const InterstateState &) = default;

            Player CurrentPlayer() const override
            {
                if (IsTerminal()) return kTerminalPlayerId;
                if (num_moves_ == 0) return kChancePlayerId;
                return current_player_;
            }
            std::string ActionToString(Player player, Action action_id) const override;
            std::string ToString() const override;
            bool IsTerminal() const override;
            bool IsChanceNode() const override;
            std::vector<double> Returns() const override;
            std::string InformationStateString(Player player) const override;
            std::string ObservationString(Player player) const override;
            void ObservationTensor(Player player,
                                   absl::Span<float> values) const override;
            std::unique_ptr<State> Clone() const override;
            void UndoAction(Player player, Action move) override;
            std::vector<Action> LegalActions() const override;
            ActionsAndProbs ChanceOutcomes() const override;
            std::vector<CellState> Board() const;
            CellState BoardAt(int cell) const { return board_[cell]; }
            CellState BoardAt(int row, int column) const
            {
                return board_[row * kNumCols + column];
            }
            Player outcome() const { return outcome_; }
            void ChangePlayer() { current_player_ = current_player_ == 0 ? 1 : 0; }
            bool is_terminal() const { return terminal_; }

            // Only used by Ultimate Tic-Tac-Toe.
            void SetCurrentPlayer(Player player) { current_player_ = player; }

            std::unique_ptr<StateStruct> ToStruct() const override;

        protected:
            std::array<CellState, kNumCells> board_;
            void DoApplyAction(Action move) override;

        private:
            bool HasLine(Player player) const; // Does this player have a line?
            bool IsFull() const;               // Is the board full?
            Player current_player_ = 0;        // Player zero goes first
            Player outcome_ = kInvalidPlayer;
            int num_moves_ = 0;
            bool terminal_ = false;
            std::vector<DeckStatus> deck_statuses_;
            std::vector<Node> nodes_;
            std::vector<Edge> edges_;
            std::vector<PlayerInfo> player_infos_;
            std::vector<std::tuple<int, int>> drawn_cards_;
        };

        // Game object.
        class InterstateGame : public Game
        {
        public:
            explicit InterstateGame(const GameParameters &params);
            int NumDistinctActions() const override { return kNumCells; }
            std::unique_ptr<State> NewInitialState() const override
            {
                return std::unique_ptr<State>(new InterstateState(shared_from_this()));
            }
            int MaxChanceOutcomes() const override { 
                return 2;
                // // The chance actions correspond to: a player drawing a resource type or a goal card
                // return GetNumResources() + GetNumGoals();
             }
            int NumPlayers() const override { return num_players_; }
            double MinUtility() const override { return -1; }
            absl::optional<double> UtilitySum() const override { return 0; }
            double MaxUtility() const override { return 1; }
            std::vector<int> ObservationTensorShape() const override
            {
                return {kCellStates, kNumRows, kNumCols};
            }
            int MaxGameLength() const override { return kNumCells; }
            std::string ActionToString(Player player, Action action_id) const override;

            // Getters for game configuration structures
            const std::vector<Node>& GetNodes() const { return nodes_; }
            const std::vector<Edge>& GetEdges() const { return edges_; }
            const std::vector<Goal>& GetGoals() const { return goals_; }
            int GetNumGoals() const { return static_cast<int>(goals_.size()); }
            const Deck& GetResourceDeck() const { return resource_deck_; }
            const Deck& GetGoalDeck() const { return goal_deck_; }
            int GetNumFaceupCards() const { return num_faceup_resource_cards_; }
            int GetNumNodes() const { return num_nodes_; }
            int GetNumResources() const { return num_resources_; }
            int GetNumInitialDrawGoals() const { return num_initial_player_goal_cards_; }
            int GetMinInitialKeepGoals() const { return keep_min_initial_goal_cards_; }
            int GetNumDrawGoals() const { return num_draw_goal_cards_; }
            int GetMinKeepGoals() const { return keep_min_goal_cards_; }
            int GetNumInitialResourceCards() const { return num_initial_resource_cards_; }
            int GetNumPlayerPieces() const { return num_player_pieces_; }
            const std::vector<int>& GetWildResources() const { return wild_resources_; }

        private:
            // Game configuration structures (shared across all states of this game)
            std::vector<Node> nodes_;
            std::vector<Edge> edges_;
            std::vector<Goal> goals_;
            Deck resource_deck_;
            Deck goal_deck_;
            int num_players_;
            int num_faceup_resource_cards_;
            int num_nodes_;
            int num_resources_;
            int num_initial_player_goal_cards_;
            int keep_min_initial_goal_cards_;
            int num_draw_goal_cards_;
            int keep_min_goal_cards_;
            int num_initial_resource_cards_;
            int num_player_pieces_;
            std::vector<int> wild_resources_;

            // Helper functions to initialize game structures based on parameters
            std::vector<Node> InitializeNodes(const GameParameters &params) const;
            std::vector<Edge> InitializeEdges(const GameParameters &params) const;
            std::vector<Goal> InitializeGoals(const GameParameters &params) const;
            Deck InitializeResourceDeck(const GameParameters &params) const;
            Deck InitializeGoalDeck(const std::vector<Goal>& goals) const;
            std::vector<int> InitializeWildResources(const GameParameters &params) const;
        };

        CellState PlayerToState(Player player);
        std::string StateToString(CellState state);

        // Does this player have a line?
        bool BoardHasLine(const std::array<CellState, kNumCells> &board,
                          const Player player);

        inline std::ostream &operator<<(std::ostream &stream, const CellState &state)
        {
            return stream << StateToString(state);
        }

    } // namespace interstate
} // namespace open_spiel

#endif // OPEN_SPIEL_GAMES_INTERSTATE_H_
