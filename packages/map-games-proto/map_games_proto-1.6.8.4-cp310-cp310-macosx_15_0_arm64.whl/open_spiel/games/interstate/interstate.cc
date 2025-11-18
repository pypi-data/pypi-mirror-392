#include "open_spiel/games/interstate/interstate.h"

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "open_spiel/abseil-cpp/absl/strings/str_cat.h"
#include "open_spiel/abseil-cpp/absl/types/span.h"
#include "open_spiel/game_parameters.h"
#include "open_spiel/observer.h"
#include "open_spiel/spiel.h"
#include "open_spiel/spiel_globals.h"
#include "open_spiel/spiel_utils.h"
#include "open_spiel/utils/tensor_view.h"

namespace open_spiel
{
    namespace interstate
    {
        constexpr const int kDefaultNumPlayers = 2;

        namespace
        {

            // Facts about the game.
            const GameType kGameType{
                /*short_name=*/"interstate",
                /*long_name=*/"Interstate",
                GameType::Dynamics::kSequential,
                GameType::ChanceMode::kExplicitStochastic,
                GameType::Information::kImperfectInformation,
                GameType::Utility::kGeneralSum,
                GameType::RewardModel::kRewards,
                /*max_num_players=*/8,
                /*min_num_players=*/2,
                /*provides_information_state_string=*/true,
                /*provides_information_state_tensor=*/false,
                /*provides_observation_string=*/true,
                /*provides_observation_tensor=*/true,
                /*parameter_specification=*/{
                    {"players", GameParameter(kDefaultNumPlayers)},
                    {"num_player_pieces", GameParameter(45)},  // default: 45, min: 10, max: 100
                    {"num_faceup_resource_cards", GameParameter(3)},  // default: 3, min: 0, max: 10
                    {"num_nodes", GameParameter(14)},         // default: 14, min: 1, max: 100
                    {"num_resources", GameParameter(5)},      // default: 5, min: 1, max: 20
                    {"num_initial_player_goal_cards", GameParameter(2)},  // default: 2, min: 0
                    {"keep_min_initial_goal_cards", GameParameter(1)},  // default: 1, min: 0, max: num_initial_player_goal_cards
                    {"num_draw_goal_cards", GameParameter(2)},  // default: 2, min: 1
                    {"keep_min_goal_cards", GameParameter(1)},  // default: 1, min: 0, max: num_draw_goal_cards
                    {"num_initial_resource_cards", GameParameter(3)},  // default: 3, min: 0, max: 10
                    {"edges", GameParameter(std::string(""))},  // JSON string for edge configuration
                    {"resource_deck", GameParameter(std::string(""))},  // JSON string for resource deck configuration
                    {"wild_resources", GameParameter(std::string("[4]"))},  // JSON string array of wild resource indices
                    {"goals", GameParameter(std::string(""))},  // JSON string for goals configuration
                },
                /*default_loadable=*/true,
                /*provides_factored_observation_string=*/true,
            };

            std::shared_ptr<const Game> Factory(const GameParameters &params)
            {
                return std::shared_ptr<const Game>(new InterstateGame(params));
            }

            REGISTER_SPIEL_GAME(kGameType, Factory);

            RegisterSingleTensorObserver single_tensor(kGameType.short_name);

        } // namespace

        // USA constant string for the map
        const std::string usa_map = R"(
(0)          d d d d d d          (1)                                             (3)
     -                                 c                  (2)                    a
        -                                 c            a        -              a
           -                                 c      a                -       a
              (4)         - - - - - -          (5)      c c c c c        (6)
 b
 b                d
 b                  d                          b                       -
 b                    d                        b                      -
 b                      (7)                    b                     -
                  c           -                b                    -
             c                     -
        c              a                -
 (8)                  a                      (9)     d d d d    (10)
                     a
      -             a                         -
         -         a                          -                   -
            -                                 -                   -
                                                                  -
               (11)       c c c c c c        (12)                 -
                                                     -            -
                                                        -
                                                           -
                                                              -
                                                                 (13)
)";

        CellState PlayerToState(Player player)
        {
            switch (player)
            {
            case 0:
                return CellState::kCross;
            case 1:
                return CellState::kNought;
            default:
                SpielFatalError(absl::StrCat("Invalid player id ", player));
                return CellState::kEmpty;
            }
        }

        std::string PlayerToString(Player player)
        {
            switch (player)
            {
            case 0:
                return "0";
            case 1:
                return "1";
            default:
                return DefaultPlayerString(player);
            }
        }

        std::string StateToString(CellState state)
        {
            switch (state)
            {
            case CellState::kEmpty:
                return ".";
            case CellState::kNought:
                return "1";
            case CellState::kCross:
                return "0";
            default:
                SpielFatalError("Unknown state.");
            }
        }

        bool BoardHasLine(const std::array<CellState, kNumCells> &board,
                          const Player player)
        {
            CellState c = PlayerToState(player);
            return (board[0] == c && board[1] == c && board[2] == c) ||
                   (board[3] == c && board[4] == c && board[5] == c) ||
                   (board[6] == c && board[7] == c && board[8] == c) ||
                   (board[0] == c && board[3] == c && board[6] == c) ||
                   (board[1] == c && board[4] == c && board[7] == c) ||
                   (board[2] == c && board[5] == c && board[8] == c) ||
                   (board[0] == c && board[4] == c && board[8] == c) ||
                   (board[2] == c && board[4] == c && board[6] == c);
        }

        std::vector<CellState> InterstateState::Board() const
        {
            std::vector<CellState> board(board_.begin(), board_.end());
            return board;
        }

        void InterstateState::DoApplyAction(Action move)
        {
            const auto &game = static_cast<const InterstateGame &>(*game_);

            if (IsChanceNode()) {
                if (move == 0) {
                    // Pop the top card from deck_statuses_[0].facedown_stack
                    // and add to drawn_cards_
                    if (!deck_statuses_.empty() &&
                        !deck_statuses_[0].facedown_stack.cards.empty()) {
                        drawn_cards_.push_back(deck_statuses_[0].facedown_stack.cards.back());
                        deck_statuses_[0].facedown_stack.cards.pop_back();
                    }
                } else if (move == 1) {
                    // Pop the top card from deck_statuses_[1].facedown_stack
                    // and add to drawn_cards_
                    if (deck_statuses_.size() > 1 &&
                        !deck_statuses_[1].facedown_stack.cards.empty()) {
                        drawn_cards_.push_back(deck_statuses_[1].facedown_stack.cards.back());
                        deck_statuses_[1].facedown_stack.cards.pop_back();
                    }
                }
                // if (move < game.GetNumResources()) {
                //     // Find the first card in deck_statuses_[0].facedown_stack
                //     // with a resource_idx of {move} and append to "drawn_cards_"
                //     for (const auto &card : deck_statuses_[0].facedown_stack.cards) {
                //         if (card.resource_idx == move) {
                //             drawn_cards_.push_back(card);
                //             break;
                //         }
                //     }
                // }
            }
            
        }

        std::vector<Action> InterstateState::LegalActions() const
        {
            if (IsTerminal())
                return {};
            
            const auto &game = static_cast<const InterstateGame &>(*game_);

            if (IsChanceNode()) {
                std::vector<Action> chance_actions;
                return {0, 1};
                // for (int i = 0; i < game.MaxChanceOutcomes(); ++i) {
                //     chance_actions.push_back(i);
                // }
                // return chance_actions;
            }

            std::vector<Action> moves;
            // The first set of moves correspond to the
            // non-empty spots of deck_statuses_[0].faceup_spread
            
            // Iterate through "deck_statuses_[0].faceup_spread.spots"
            // and add actions for non-empty spots
            if (!deck_statuses_.empty()) {
                const auto &faceup_spread = deck_statuses_[0].faceup_spread;
                for (size_t i = 0; i < game.GetNumFaceupCards(); ++i) {
                    if (faceup_spread.spots[i].has_value()) {
                        moves.push_back(static_cast<Action>(i));
                    }
                }
            }
            // If "deck_statuses_[0].facedown_stack" has cards,
            // add an action to draw from it
            if (!deck_statuses_.empty() &&
                !deck_statuses_[0].facedown_stack.cards.empty()) {
                moves.push_back(static_cast<Action>(game.GetNumFaceupCards()));
            }
            // If "deck_statuses_[1].facedown_stack" has cards,
            // add an action to draw from it
            if (deck_statuses_.size() > 1 &&
                !deck_statuses_[1].facedown_stack.cards.empty()) {
                moves.push_back(static_cast<Action>(game.GetNumFaceupCards() + 1));
            }
            return moves;
        }

        ActionsAndProbs InterstateState::ChanceOutcomes() const
        {
            SPIEL_CHECK_TRUE(IsChanceNode());

            // At the start of the game (num_moves_ == 0), draw the first card
            // from DeckStatus 0's facedown_stack
            if (num_moves_ == 0 && !deck_statuses_.empty() &&
                !deck_statuses_[0].facedown_stack.cards.empty()) {
                // Only one outcome: draw the top card (card at index 0)
                // Action represents which card index to draw
                ActionsAndProbs outcomes;
                outcomes.push_back({0, 1.0});  // Action 0 = draw first card, probability 1.0
                return outcomes;
            }
            return {};
        }

        std::string InterstateState::ActionToString(Player player,
                                                    Action action_id) const
        {
            return game_->ActionToString(player, action_id);
        }

        bool InterstateState::HasLine(Player player) const
        {
            return BoardHasLine(board_, player);
        }

        bool InterstateState::IsFull() const { return num_moves_ == kNumCells; }

        std::vector<Node> InterstateGame::InitializeNodes(const GameParameters &params) const {
            int num_nodes = ParameterValue<int>("num_nodes", 14);
            std::vector<Node> nodes(num_nodes);
            for (int i = 0; i < num_nodes; ++i) {
                nodes[i].idx = i;
            }
            return nodes;
        }

        std::vector<Goal> InterstateGame::InitializeGoals(const GameParameters &params) const {
            // Check if goals parameter is provided
            std::string goals_json = ParameterValue<std::string>("goals", "");

            if (!goals_json.empty()) {
                // Parse JSON from the goals parameter
                try {
                    nlohmann::json j = nlohmann::json::parse(goals_json);
                    std::vector<Goal> goals;
                    goals.reserve(j.size());

                    for (size_t goal_idx = 0; goal_idx < j.size(); ++goal_idx) {
                        const auto& goal_json = j[goal_idx];

                        Goal goal;
                        goal.idx = goal_idx;
                        goal.score = goal_json["score"].get<int>();

                        // Parse nodes array
                        const auto& nodes_json = goal_json["nodes"];
                        goal.node_idxs.reserve(nodes_json.size());
                        for (const auto& node : nodes_json) {
                            goal.node_idxs.push_back(node.get<int>());
                        }

                        goals.push_back(goal);
                    }

                    return goals;
                } catch (const nlohmann::json::exception& e) {
                    SpielFatalError(absl::StrCat("Failed to parse goals JSON: ", e.what()));
                }
            }

            // Default goals configuration if no parameter provided
            std::vector<Goal> goals(20);

            // Goal 0: Connect nodes 0 and 3, score 20
            goals[0].idx = 0;
            goals[0].node_idxs = {0, 3};
            goals[0].score = 20;

            // Goal 1: Connect nodes 13 and 3, score 10
            goals[1].idx = 1;
            goals[1].node_idxs = {13, 3};
            goals[1].score = 10;

            goals[2].idx = 2;
            goals[2].node_idxs = {11, 2};
            goals[2].score = 8;

            goals[3].idx = 3;
            goals[3].node_idxs = {8, 6};
            goals[3].score = 12;

            goals[4].idx = 4;
            goals[4].node_idxs = {9, 2};
            goals[4].score = 6;

            goals[5].idx = 5;
            goals[5].node_idxs = {10, 5};
            goals[5].score = 4;

            goals[6].idx = 6;
            goals[6].node_idxs = {12, 5};
            goals[6].score = 7;

            goals[7].idx = 7;
            goals[7].node_idxs = {12, 6};
            goals[7].score = 5;

            goals[8].idx = 8;
            goals[8].node_idxs = {11, 0};
            goals[8].score = 9;

            goals[9].idx = 9;
            goals[9].node_idxs = {11, 1};
            goals[9].score = 12;

            goals[10].idx = 10;
            goals[10].node_idxs = {9, 4};
            goals[10].score = 6;

            goals[11].idx = 11;
            goals[11].node_idxs = {10, 5};
            goals[11].score = 7;

            goals[12].idx = 12;
            goals[12].node_idxs = {8, 6};
            goals[12].score = 13;

            goals[13].idx = 13;
            goals[13].node_idxs = {13, 0};
            goals[13].score = 18;

            goals[14].idx = 14;
            goals[14].node_idxs = {13, 4};
            goals[14].score = 15;

            goals[15].idx = 15;
            goals[15].node_idxs = {7, 1};
            goals[15].score = 11;

            goals[16].idx = 16;
            goals[16].node_idxs = {4, 6};
            goals[16].score = 8;

            goals[17].idx = 17;
            goals[17].node_idxs = {13, 3};
            goals[17].score = 12;

            goals[18].idx = 18;
            goals[18].node_idxs = {13, 5};
            goals[18].score = 10;

            goals[19].idx = 19;
            goals[19].node_idxs = {0, 10};
            goals[19].score = 12;

            return goals;
        }

        Deck InterstateGame::InitializeResourceDeck(const GameParameters &params) const {
            // Check if resource_deck parameter is provided
            std::string resource_deck_json = ParameterValue<std::string>("resource_deck", "");

            if (!resource_deck_json.empty()) {
                // Parse JSON from the resource_deck parameter
                try {
                    nlohmann::json j = nlohmann::json::parse(resource_deck_json);

                    // Expect JSON array of resource indices
                    if (j.is_array()) {
                        std::vector<int> resource_indices;
                        resource_indices.reserve(j.size());

                        for (const auto& item : j) {
                            resource_indices.push_back(item.get<int>());
                        }

                        return Deck(resource_indices);
                    } else {
                        SpielFatalError("resource_deck JSON must be an array of integers");
                    }
                } catch (const nlohmann::json::exception& e) {
                    SpielFatalError(absl::StrCat("Failed to parse resource_deck JSON: ", e.what()));
                }
            }

            // Default resource deck configuration if no parameter provided
            return Deck({
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
                4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4
            });
        }

        Deck InterstateGame::InitializeGoalDeck(const std::vector<Goal>& goals) const {
            // Create a deck with one card for each goal
            Deck goal_deck;
            goal_deck.idx = 1;  // Different deck index from resource_deck
            goal_deck.cards.reserve(goals.size());

            for (size_t i = 0; i < goals.size(); ++i) {
                // Create a card with resource_idx as null and goal_idx set to the goal's index
                Card goal_card;
                goal_card.idx = i;
                goal_card.deck_idx = 1;
                goal_card.resource_idx = absl::nullopt;  // No resource
                goal_card.goal_idx = goals[i].idx;
                goal_deck.cards.push_back(goal_card);
            }

            return goal_deck;
        }

        std::vector<int> InterstateGame::InitializeWildResources(const GameParameters &params) const {
            // Check if wild_resources parameter is provided
            std::string wild_resources_json = ParameterValue<std::string>("wild_resources", "[4]");

            try {
                nlohmann::json j = nlohmann::json::parse(wild_resources_json);

                // Expect JSON array of resource indices
                if (j.is_array()) {
                    std::vector<int> wild_resources;
                    wild_resources.reserve(j.size());

                    for (const auto& item : j) {
                        wild_resources.push_back(item.get<int>());
                    }

                    return wild_resources;
                } else {
                    SpielFatalError("wild_resources JSON must be an array of integers");
                }
            } catch (const nlohmann::json::exception& e) {
                SpielFatalError(absl::StrCat("Failed to parse wild_resources JSON: ", e.what()));
            }
        }

        std::vector<Edge> InterstateGame::InitializeEdges(const GameParameters &params) const {
            // Check if edges parameter is provided
            std::string edges_json = ParameterValue<std::string>("edges", "");

            if (!edges_json.empty()) {
                // Parse JSON from the edges parameter
                try {
                    nlohmann::json j = nlohmann::json::parse(edges_json);
                    std::vector<Edge> edges;
                    edges.reserve(j.size());

                    for (size_t edge_idx = 0; edge_idx < j.size(); ++edge_idx) {
                        const auto& edge_json = j[edge_idx];

                        // Parse nodes tuple
                        auto nodes = edge_json["nodes"];
                        int node_1_idx = nodes[0].get<int>();
                        int node_2_idx = nodes[1].get<int>();

                        // Parse paths array
                        std::vector<Path> paths;
                        const auto& paths_json = edge_json["paths"];
                        paths.reserve(paths_json.size());

                        for (size_t path_idx = 0; path_idx < paths_json.size(); ++path_idx) {
                            const auto& path_json = paths_json[path_idx];
                            int score = path_json["score"].get<int>();

                            // Parse segments array
                            std::vector<Segment> segments;
                            const auto& segments_json = path_json["segments"];
                            segments.reserve(segments_json.size());

                            for (size_t seg_idx = 0; seg_idx < segments_json.size(); ++seg_idx) {
                                const auto& seg_json = segments_json[seg_idx];
                                absl::optional<int> resource_idx = absl::nullopt;

                                if (!seg_json["resource"].is_null()) {
                                    resource_idx = seg_json["resource"].get<int>();
                                }

                                segments.emplace_back(seg_idx, resource_idx);
                            }

                            paths.emplace_back(path_idx, std::move(segments), score);
                        }

                        edges.emplace_back(edge_idx, node_1_idx, node_2_idx, std::move(paths));
                    }

                    return edges;
                } catch (const nlohmann::json::exception& e) {
                    SpielFatalError(absl::StrCat("Failed to parse edges JSON: ", e.what()));
                }
            }

            // Default edges configuration if no parameter provided
            std::vector<Edge> edges(19);

            // Edge 0: Node 0 → Node 1 (6 segments, resource 'd'/3)
            edges[0] = Edge(0, 0, 1, {
                Path(0, {Segment(0, 3), Segment(1, 3), Segment(2, 3), Segment(3, 3), Segment(4, 3), Segment(5, 3)}, 0)
            });

            // Edge 1: Node 0 → Node 4 (3 segments, no resource)
            edges[1] = Edge(1, 0, 4, {
                Path(0, {Segment(0), Segment(1), Segment(2)}, 0)
            });

            // Edge 2: Node 0 → Node 8 (5 segments, resource 'b'/1)
            edges[2] = Edge(2, 0, 8, {
                Path(0, {Segment(0, 1), Segment(1, 1), Segment(2, 1), Segment(3, 1), Segment(4, 1)}, 0)
            });

            // Edge 3: Node 1 → Node 5 (3 segments, resource 'c'/2)
            edges[3] = Edge(3, 1, 5, {
                Path(0, {Segment(0, 2), Segment(1, 2), Segment(2, 2)}, 0)
            });

            // Edge 4: Node 2 → Node 5 (2 segments, resource 'a'/0)
            edges[4] = Edge(4, 2, 5, {
                Path(0, {Segment(0, 0), Segment(1, 0)}, 0)
            });

            // Edge 5: Node 3 → Node 6 (3 segments, resource 'a'/0)
            edges[5] = Edge(5, 3, 6, {
                Path(0, {Segment(0, 0), Segment(1, 0), Segment(2, 0)}, 0)
            });

            // Edge 6: Node 4 → Node 5 (6 segments, no resource)
            edges[6] = Edge(6, 4, 5, {
                Path(0, {Segment(0), Segment(1), Segment(2), Segment(3), Segment(4), Segment(5)}, 0)
            });

            // Edge 7: Node 5 → Node 6 (5 segments, resource 'c'/2)
            edges[7] = Edge(7, 5, 6, {
                Path(0, {Segment(0, 2), Segment(1, 2), Segment(2, 2), Segment(3, 2), Segment(4, 2)}, 0)
            });

            // Edge 8: Node 4 → Node 7 (3 segments, resource 'd'/3)
            edges[8] = Edge(8, 4, 7, {
                Path(0, {Segment(0, 3), Segment(1, 3), Segment(2, 3)}, 0)
            });

            // Edge 9: Node 5 → Node 9 (4 segments, resource 'b'/1)
            edges[9] = Edge(9, 5, 9, {
                Path(0, {Segment(0, 1), Segment(1, 1), Segment(2, 1), Segment(3, 1)}, 0)
            });

            // Edge 10: Node 6 → Node 10 (4 segments, no resource)
            edges[10] = Edge(10, 6, 10, {
                Path(0, {Segment(0), Segment(1), Segment(2), Segment(3)}, 0)
            });

            // Edge 11: Node 7 → Node 4 (3 segments, resource 'd'/3)
            edges[11] = Edge(11, 7, 4, {
                Path(0, {Segment(0, 3), Segment(1, 3), Segment(2, 3)}, 0)
            });

            // Edge 12: Node 7 → Node 9 (3 segments, no resource)
            edges[12] = Edge(12, 7, 9, {
                Path(0, {Segment(0), Segment(1), Segment(2)}, 0)
            });

            // Edge 13: Node 8 → Node 7 (3 segments, resource 'c'/2)
            edges[13] = Edge(13, 8, 7, {
                Path(0, {Segment(0, 2), Segment(1, 2), Segment(2, 2)}, 0)
            });

            // Edge 14: Node 8 → Node 11 (3 segments, no resource)
            edges[14] = Edge(14, 8, 11, {
                Path(0, {Segment(0), Segment(1), Segment(2)}, 0)
            });

            // Edge 15: Node 9 → Node 10 (4 segments, resource 'd'/3)
            edges[15] = Edge(15, 9, 10, {
                Path(0, {Segment(0, 3), Segment(1, 3), Segment(2, 3), Segment(3, 3)}, 0)
            });

            // Edge 16: Node 10 → Node 13 (5 segments, no resource)
            edges[16] = Edge(16, 10, 13, {
                Path(0, {Segment(0), Segment(1), Segment(2), Segment(3), Segment(4)}, 0)
            });

            // Edge 17: Node 11 → Node 12 (6 segments, resource 'c'/2)
            edges[17] = Edge(17, 11, 12, {
                Path(0, {Segment(0, 2), Segment(1, 2), Segment(2, 2), Segment(3, 2), Segment(4, 2), Segment(5, 2)}, 0)
            });

            // Edge 18: Node 12 → Node 13 (4 segments, no resource)
            edges[18] = Edge(18, 12, 13, {
                Path(0, {Segment(0), Segment(1), Segment(2), Segment(3)}, 0)
            });

            return edges;
        }

        std::string Segment::ToString() const {
            std::string result = "{";
            absl::StrAppend(&result, "\"idx\": ", idx, ",");

            if (resource_idx.has_value()) {
                absl::StrAppend(&result, "\"resource_idx\": ", resource_idx.value(), ",");
            } else {
                absl::StrAppend(&result, "\"resource_idx\": null,");
            }

            absl::StrAppend(&result, "\"piece\": ");
            if (piece.has_value()) {
                absl::StrAppend(&result, "[", std::get<0>(piece.value()), ", ",
                              std::get<1>(piece.value()), "]");
            } else {
                absl::StrAppend(&result, "null");
            }
            absl::StrAppend(&result, "}");
            return result;
        }

        std::string Path::ToString() const {
            std::string result = "{";
            absl::StrAppend(&result, "\"idx\": ", idx, ",");
            absl::StrAppend(&result, "\"score\": ", score, ",");
            absl::StrAppend(&result, "\"segments\": [");

            for (size_t i = 0; i < segments.size(); ++i) {
                absl::StrAppend(&result, segments[i].ToString());
                if (i < segments.size() - 1) absl::StrAppend(&result, ",");
            }

            absl::StrAppend(&result, "]");
            absl::StrAppend(&result, "}");
            return result;
        }

        std::string Edge::ToString() const {
            std::string result = "";
            // Left-pad idx to 2 digits for alignment
            if (idx < 10) {
                absl::StrAppend(&result, " ", idx, ": (", node_1_idx, ") ");
            } else {
                absl::StrAppend(&result, idx, ": (", node_1_idx, ") ");
            }

            // Assume single path for now, display segments as resource characters
            if (!paths.empty() && !paths[0].segments.empty()) {
                for (const auto& segment : paths[0].segments) {
                    if (segment.resource_idx.has_value()) {
                        // Map resource_idx to character: 0='a', 1='b', 2='c', 3='d'
                        char resource_char = 'a' + segment.resource_idx.value();
                        absl::StrAppend(&result, std::string(1, resource_char));
                    } else {
                        absl::StrAppend(&result, "-");
                    }
                }
            }

            absl::StrAppend(&result, " (", node_2_idx, ")");
            return result;
        }

        InterstateState::InterstateState(std::shared_ptr<const Game> game) : State(game)
        {
            std::fill(begin(board_), end(board_), CellState::kEmpty);

            // Initialize deck_statuses_ as a length-2 vector
            const auto* interstate_game = dynamic_cast<const InterstateGame*>(game_.get());
            const auto& resource_deck = interstate_game->GetResourceDeck();
            const auto& goal_deck = interstate_game->GetGoalDeck();

            deck_statuses_.resize(2);

            // DeckStatus 0 - Resource Deck
            deck_statuses_[0].idx = 0;
            // Initialize facedown_stack with all resource deck cards
            for (size_t i = 0; i < resource_deck.cards.size(); ++i) {
                deck_statuses_[0].facedown_stack.cards.push_back(std::make_tuple(0, static_cast<int>(i)));
            }
            // faceup_stack, discard_faceup_stack, discard_facedown_stack empty by default
            // facedown_spread empty by default
            // faceup_spread has 5 null spots
            deck_statuses_[0].faceup_spread.spots.resize(5, absl::nullopt);

            // DeckStatus 1 - Goal Deck
            deck_statuses_[1].idx = 1;
            // Initialize facedown_stack with all goal deck cards
            for (size_t i = 0; i < goal_deck.cards.size(); ++i) {
                deck_statuses_[1].facedown_stack.cards.push_back(std::make_tuple(1, static_cast<int>(i)));
            }
            // faceup_stack, discard_faceup_stack, discard_facedown_stack, facedown_spread, faceup_spread all empty by default

            player_infos_.clear();
        }

        std::string InterstateState::ToString() const
        {
            std::string str;
            for (int r = 0; r < kNumRows; ++r)
            {
                for (int c = 0; c < kNumCols; ++c)
                {
                    absl::StrAppend(&str, StateToString(BoardAt(r, c)));
                }
                if (r < (kNumRows - 1))
                {
                    absl::StrAppend(&str, "\n");
                }
            }

            // Create representation of edges
            std::string result = usa_map;
            absl::StrAppend(&result, "Edges:\n");

            // Get edges from the game configuration
            const auto* interstate_game = dynamic_cast<const InterstateGame*>(game_.get());
            const auto& edges = interstate_game->GetEdges();

            for (size_t e = 0; e < edges.size(); ++e) {
                absl::StrAppend(&result, edges[e].ToString());
                absl::StrAppend(&result, "\n");
            }

            // Quick printout of goal_deck_
            absl::StrAppend(&result, "\nGoal Deck:\n");
            const auto& goal_deck = interstate_game->GetGoalDeck();
            absl::StrAppend(&result, "  Deck idx: ", goal_deck.idx, ", Total cards: ", goal_deck.cards.size(), "\n");
            for (size_t i = 0; i < goal_deck.cards.size(); ++i) {
                const auto& card = goal_deck.cards[i];
                absl::StrAppend(&result, "  Card ", i, ": idx=", card.idx, ", deck_idx=", card.deck_idx);
                if (card.goal_idx.has_value()) {
                    absl::StrAppend(&result, ", goal_idx=", card.goal_idx.value());
                }
                absl::StrAppend(&result, "\n");
            }

            // Quick printout of deck_statuses_
            absl::StrAppend(&result, "\nDeck Statuses:\n");
            for (size_t d = 0; d < deck_statuses_.size(); ++d) {
                const auto& deck_status = deck_statuses_[d];
                absl::StrAppend(&result, "  DeckStatus ", d, " (idx=", deck_status.idx, "):\n");

                // Facedown stack
                absl::StrAppend(&result, "    facedown_stack: ", deck_status.facedown_stack.cards.size(), " cards [");
                for (size_t i = 0; i < std::min(size_t(5), deck_status.facedown_stack.cards.size()); ++i) {
                    if (i > 0) absl::StrAppend(&result, ", ");
                    absl::StrAppend(&result, "(", std::get<0>(deck_status.facedown_stack.cards[i]),
                                   ",", std::get<1>(deck_status.facedown_stack.cards[i]), ")");
                }
                if (deck_status.facedown_stack.cards.size() > 5) {
                    absl::StrAppend(&result, ", ...");
                }
                absl::StrAppend(&result, "]\n");

                // Faceup stack
                absl::StrAppend(&result, "    faceup_stack: ", deck_status.faceup_stack.cards.size(), " cards\n");

                // Faceup spread
                absl::StrAppend(&result, "    faceup_spread: ", deck_status.faceup_spread.spots.size(), " spots\n");

                // Facedown spread
                absl::StrAppend(&result, "    facedown_spread: ", deck_status.facedown_spread.spots.size(), " spots\n");

                // Discard stacks
                absl::StrAppend(&result, "    discard_faceup_stack: ", deck_status.discard_faceup_stack.cards.size(), " cards\n");
                absl::StrAppend(&result, "    discard_facedown_stack: ", deck_status.discard_facedown_stack.cards.size(), " cards\n");
            }

            // Print drawn_cards_
            absl::StrAppend(&result, "\nDrawn Cards: ", drawn_cards_.size(), " cards [");
            for (size_t i = 0; i < drawn_cards_.size(); ++i) {
                if (i > 0) absl::StrAppend(&result, ", ");
                absl::StrAppend(&result, "(", std::get<0>(drawn_cards_[i]),
                               ",", std::get<1>(drawn_cards_[i]), ")");
            }
            absl::StrAppend(&result, "]\n");

            return result;
        }

        bool InterstateState::IsChanceNode() const {
            return CurrentPlayer() == kChancePlayerId;
        }

        std::unique_ptr<StateStruct> InterstateState::ToStruct() const
        {
            InterstateStateStruct rv;
            std::vector<std::string> board;
            board.reserve(board_.size());
            for (const CellState &cell : board_)
            {
                board.push_back(StateToString(cell));
            }
            rv.current_player = PlayerToString(CurrentPlayer());
            rv.board = board;
            return std::make_unique<InterstateStateStruct>(rv);
        }

        bool InterstateState::IsTerminal() const
        {
            return outcome_ != kInvalidPlayer || IsFull();
        }

        std::vector<double> InterstateState::Returns() const
        {
            if (HasLine(Player{0}))
            {
                return {1.0, -1.0};
            }
            else if (HasLine(Player{1}))
            {
                return {-1.0, 1.0};
            }
            else
            {
                return {0.0, 0.0};
            }
        }

        std::string InterstateState::InformationStateString(Player player) const
        {
            SPIEL_CHECK_GE(player, 0);
            SPIEL_CHECK_LT(player, num_players_);
            return HistoryString();
        }

        std::string InterstateState::ObservationString(Player player) const
        {
            SPIEL_CHECK_GE(player, 0);
            SPIEL_CHECK_LT(player, num_players_);
            return ToString();
        }

        void InterstateState::ObservationTensor(Player player,
                                                absl::Span<float> values) const
        {
            SPIEL_CHECK_GE(player, 0);
            SPIEL_CHECK_LT(player, num_players_);

            // Treat `values` as a 2-d tensor.
            TensorView<2> view(values, {kCellStates, kNumCells}, true);
            for (int cell = 0; cell < kNumCells; ++cell)
            {
                view[{static_cast<int>(board_[cell]), cell}] = 1.0;
            }
        }

        void InterstateState::UndoAction(Player player, Action move)
        {
            board_[move] = CellState::kEmpty;
            current_player_ = player;
            outcome_ = kInvalidPlayer;
            num_moves_ -= 1;
            history_.pop_back();
            --move_number_;
        }

        std::unique_ptr<State> InterstateState::Clone() const
        {
            return std::unique_ptr<State>(new InterstateState(*this));
        }

        std::string InterstateGame::ActionToString(Player player,
                                                   Action action_id) const
        {
            if (player == kChancePlayerId)
            {
                if (action_id == 0){
                    return "DrawResourceCard";
                } else if (action_id == 1) {
                    return "DrawGoalCard";
                }
            }
            return "A" + std::to_string(action_id);
        }

        InterstateGame::InterstateGame(const GameParameters &params)
            : Game(kGameType, params),
              nodes_(InitializeNodes(params)),
              edges_(InitializeEdges(params)),
              goals_(InitializeGoals(params)),
              resource_deck_(InitializeResourceDeck(params)),
              goal_deck_(InitializeGoalDeck(goals_)),
              num_players_(ParameterValue<int>("players")),
              num_faceup_resource_cards_(
                  ParameterValue<int>("num_faceup_resource_cards", 5)),
              num_nodes_(
                  ParameterValue<int>("num_nodes", 14)),
              num_resources_(
                  ParameterValue<int>("num_resources", 5)),
              num_initial_player_goal_cards_(
                  ParameterValue<int>("num_initial_player_goal_cards", 3)),
              keep_min_initial_goal_cards_(
                  ParameterValue<int>("keep_min_initial_goal_cards", 2)),
              num_draw_goal_cards_(
                  ParameterValue<int>("num_draw_goal_cards", 3)),
              keep_min_goal_cards_(
                  ParameterValue<int>("keep_min_goal_cards", 1)),
              num_initial_resource_cards_(
                  ParameterValue<int>("num_initial_resource_cards", 3)),
              num_player_pieces_(
                  ParameterValue<int>("num_player_pieces", 45)),
              wild_resources_(InitializeWildResources(params)) {
            // Validate parameter ranges
            if (num_players_ < kGameType.min_num_players ||
                num_players_ > kGameType.max_num_players) {
                SpielFatalError(absl::StrCat(
                    "players must be between ", kGameType.min_num_players,
                    " and ", kGameType.max_num_players, ", got: ", num_players_));
            }

            if (num_faceup_resource_cards_ < 0 || num_faceup_resource_cards_ > 10) {
                SpielFatalError(absl::StrCat(
                    "num_faceup_resource_cards must be between 0 and 10, got: ",
                    num_faceup_resource_cards_));
            }

            if (num_nodes_ < 1 || num_nodes_ > 100) {
                SpielFatalError(absl::StrCat(
                    "num_nodes must be between 1 and 100, got: ",
                    num_nodes_));
            }

            if (num_resources_ < 1 || num_resources_ > 20) {
                SpielFatalError(absl::StrCat(
                    "num_resources must be between 1 and 20, got: ",
                    num_resources_));
            }

            if (num_initial_player_goal_cards_ < 1) {
                SpielFatalError(absl::StrCat(
                    "num_initial_player_goal_cards must be >= 1, got: ",
                    num_initial_player_goal_cards_));
            }

            if (keep_min_initial_goal_cards_ < 0) {
                SpielFatalError(absl::StrCat(
                    "keep_min_initial_goal_cards must be >= 0, got: ",
                    keep_min_initial_goal_cards_));
            }

            if (keep_min_initial_goal_cards_ > num_initial_player_goal_cards_) {
                SpielFatalError(absl::StrCat(
                    "keep_min_initial_goal_cards (", keep_min_initial_goal_cards_,
                    ") cannot exceed num_initial_player_goal_cards (", num_initial_player_goal_cards_, ")"));
            }

            if (num_draw_goal_cards_ < 1) {
                SpielFatalError(absl::StrCat(
                    "num_draw_goal_cards must be >= 1, got: ",
                    num_draw_goal_cards_));
            }

            if (keep_min_goal_cards_ < 0) {
                SpielFatalError(absl::StrCat(
                    "keep_min_goal_cards must be >= 0, got: ",
                    keep_min_goal_cards_));
            }

            if (keep_min_goal_cards_ > num_draw_goal_cards_) {
                SpielFatalError(absl::StrCat(
                    "keep_min_goal_cards (", keep_min_goal_cards_,
                    ") cannot exceed num_draw_goal_cards (", num_draw_goal_cards_, ")"));
            }

            if (num_initial_resource_cards_ < 0 || num_initial_resource_cards_ > 10) {
                SpielFatalError(absl::StrCat(
                    "num_initial_resource_cards must be between 0 and 10, got: ",
                    num_initial_resource_cards_));
            }

            if (num_player_pieces_ < 10 || num_player_pieces_ > 100) {
                SpielFatalError(absl::StrCat(
                    "num_player_pieces must be between 10 and 100, got: ",
                    num_player_pieces_));
            }

            // Validate that wild_resources length doesn't exceed num_resources
            if (static_cast<int>(wild_resources_.size()) > num_resources_) {
                SpielFatalError(absl::StrCat(
                    "wild_resources size (", wild_resources_.size(),
                    ") cannot exceed num_resources (", num_resources_, ")"));
            }

            // Validate that all wild resource indices are valid
            for (int wild_idx : wild_resources_) {
                if (wild_idx < 0 || wild_idx >= num_resources_) {
                    SpielFatalError(absl::StrCat(
                        "Invalid wild resource index ", wild_idx,
                        " (must be between 0 and ", num_resources_ - 1, ")"));
                }
            }

            // Validate that the initialized nodes match the parameter
            if (static_cast<int>(nodes_.size()) != num_nodes_) {
                SpielFatalError(absl::StrCat(
                    "Mismatch: num_nodes parameter is ", num_nodes_,
                    " but ", nodes_.size(), " nodes were initialized"));
            }

            // Validate that all goal node_idxs reference valid nodes
            for (const auto& goal : goals_) {
                for (int node_idx : goal.node_idxs) {
                    if (node_idx < 0 || node_idx >= num_nodes_) {
                        SpielFatalError(absl::StrCat(
                            "Goal ", goal.idx, " has invalid node_idx ", node_idx,
                            " (must be between 0 and ", num_nodes_ - 1, ")"));
                    }
                }
            }
        }

    } // namespace interstate
} // namespace open_spiel