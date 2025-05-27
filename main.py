import pygame
import sys
import random
from enum import Enum

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Texas Hold'em")
clock = pygame.time.Clock()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Card suits
class Suit(Enum):
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"
    SPADES = "S"

# Card ranks
class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

# Card class
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        rank_str = str(self.rank.value)
        if self.rank == Rank.JACK:
            rank_str = "J"
        elif self.rank == Rank.QUEEN:
            rank_str = "Q"
        elif self.rank == Rank.KING:
            rank_str = "K"
        elif self.rank == Rank.ACE:
            rank_str = "A"
        return f"{rank_str}{self.suit.value}"
    
    def draw(self, x, y, face_up=True):
        # Draw card
        card_width, card_height = 50, 70
        pygame.draw.rect(screen, WHITE, (x, y, card_width, card_height))
        pygame.draw.rect(screen, BLACK, (x, y, card_width, card_height), 2)
        
        if face_up:
            font = pygame.font.SysFont(None, 24)
            
            # Set suit color
            color = BLACK
            if self.suit == Suit.HEARTS or self.suit == Suit.DIAMONDS:
                color = RED
            
            # Draw rank and suit
            rank_str = str(self.rank.value)
            if self.rank == Rank.JACK:
                rank_str = "J"
            elif self.rank == Rank.QUEEN:
                rank_str = "Q"
            elif self.rank == Rank.KING:
                rank_str = "K"
            elif self.rank == Rank.ACE:
                rank_str = "A"
            
            rank_text = font.render(rank_str, True, color)
            suit_text = font.render(self.suit.value, True, color)
            
            screen.blit(rank_text, (x + 5, y + 5))
            screen.blit(suit_text, (x + 5, y + 25))
        else:
            # Draw card back
            pygame.draw.rect(screen, BLUE, (x + 5, y + 5, card_width - 10, card_height - 10))

# Deck class
class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(suit, rank))
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None

# Player class
class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_folded = False
        self.current_bet = 0
    
    def add_card(self, card):
        self.hand.append(card)
    
    def clear_hand(self):
        self.hand = []
        self.is_folded = False
        self.current_bet = 0
    
    def bet(self, amount):
        if amount <= self.chips:
            self.chips -= amount
            self.current_bet += amount
            return amount
        return 0
    
    def fold(self):
        self.is_folded = True

# Game class
class TexasHoldem:
    def __init__(self):
        self.deck = Deck()
        self.community_cards = []
        self.players = [Player("Player"), Player("CPU1"), Player("CPU2"), Player("CPU3")]
        self.current_player_index = 0
        self.pot = 0
        self.game_state = "waiting"  # waiting, preflop, flop, turn, river, showdown
        self.current_bet = 0
        self.small_blind = 5
        self.big_blind = 10
        self.last_action = None
        self.action_messages = []
        self.round_complete = False
    
    def start_new_hand(self):
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.round_complete = False
        
        # Clear all player hands
        for player in self.players:
            player.clear_hand()
        
        # Deal 2 cards to each player
        for _ in range(2):
            for player in self.players:
                player.add_card(self.deck.deal())
        
        # Set blind bets
        self.players[0].bet(self.small_blind)
        self.players[1].bet(self.big_blind)
        self.pot = self.small_blind + self.big_blind
        self.current_bet = self.big_blind
        
        self.current_player_index = 2 % len(self.players)
        self.game_state = "preflop"
        self.last_action = None
    
    def deal_flop(self):
        # Burn card
        self.deck.deal()
        # Deal 3 flop cards
        for _ in range(3):
            self.community_cards.append(self.deck.deal())
        self.game_state = "flop"
        self.current_player_index = 0
        self.current_bet = 0
        self.round_complete = False
        for player in self.players:
            player.current_bet = 0
        # Reset last action when moving to a new betting round
        self.last_action = None
    
    def deal_turn(self):
        # Burn card
        self.deck.deal()
        # Deal turn card
        self.community_cards.append(self.deck.deal())
        self.game_state = "turn"
        self.current_player_index = 0
        self.current_bet = 0
        self.round_complete = False
        for player in self.players:
            player.current_bet = 0
        # Reset last action when moving to a new betting round
        self.last_action = None
    
    def deal_river(self):
        # Burn card
        self.deck.deal()
        # Deal river card
        self.community_cards.append(self.deck.deal())
        self.game_state = "river"
        self.current_player_index = 0
        self.current_bet = 0
        self.round_complete = False
        for player in self.players:
            player.current_bet = 0
        # Reset last action when moving to a new betting round
        self.last_action = None
    
    def next_player(self):
        # Store the starting player index to check if we've gone around the table
        start_index = self.current_player_index
        
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        # Skip folded players
        while self.players[self.current_player_index].is_folded:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            # If all players are folded except one, we're done
            if all(p.is_folded for p in self.players if p != self.players[self.current_player_index]):
                self.round_complete = True
                return
        
        # Check if we've gone around the table back to the first player who acted in this round
        # or if we've reached the player after the last raiser
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) <= 1:
            self.round_complete = True
        elif all(p.current_bet == self.current_bet for p in active_players):
            # If everyone has matched the current bet, mark the round as complete
            # This is needed for the case where everyone checks
            if self.current_player_index == 0:  # Back to the first player
                self.round_complete = True
    
    def check_round_end(self):
        # Check if all players have bet or folded
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) == 1:
            # If only one player remains, they win
            active_players[0].chips += self.pot
            self.game_state = "waiting"
            return True
        
        # Check if all active players have made equal bets and the round is complete
        bet_amounts = [p.current_bet for p in active_players]
        
        # All players have had a chance to act and all bets are equal
        if len(set(bet_amounts)) == 1 and self.round_complete:
            # Move to next stage
            if self.game_state == "preflop":
                self.deal_flop()
            elif self.game_state == "flop":
                self.deal_turn()
            elif self.game_state == "turn":
                self.deal_river()
            elif self.game_state == "river":
                self.game_state = "showdown"
                # Simple win determination (actual poker hand evaluation is complex)
                winner = random.choice(active_players)
                winner.chips += self.pot
                
                # Display winner message
                font = pygame.font.SysFont(None, 36)
                winner_text = f"{winner.name} wins {self.pot} chips!"
                winner_surface = font.render(winner_text, True, WHITE)
                winner_rect = winner_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(winner_surface, winner_rect)
                pygame.display.flip()
                pygame.time.delay(3000)  # Show winner for 3 seconds
            
            # Reset round_complete flag
            self.round_complete = False
            return True
        return False
    
    def player_action(self, action, amount=0):
        player = self.players[self.current_player_index]
        
        if action == "fold":
            player.fold()
            # Check if only one player remains
            active_players = [p for p in self.players if not p.is_folded]
            if len(active_players) == 1:
                self.round_complete = True
        elif action == "check":
            if player.current_bet < self.current_bet:
                return False  # Can't check
            # チェックはベットがない状態で「パス」するだけなので、ラウンド完了の判定は次のプレイヤーに移動するときに行う
        elif action == "call":
            call_amount = self.current_bet - player.current_bet
            if call_amount > 0:
                bet_amount = player.bet(call_amount)
                self.pot += bet_amount
                
                # レイズに対するコールの場合、全員がコールしたかチェック
                active_players = [p for p in self.players if not p.is_folded]
                if all(p.current_bet == self.current_bet for p in active_players):
                    # 最後のプレイヤーがコールした場合、またはすべてのアクティブプレイヤーがコールした場合
                    # 最後のレイズをしたプレイヤーの次のプレイヤーまで一周した場合
                    self.round_complete = True
        elif action == "raise":
            if amount > self.current_bet:
                raise_amount = amount - player.current_bet
                bet_amount = player.bet(raise_amount)
                self.pot += bet_amount
                self.current_bet = player.current_bet
                # After a raise, reset round completion status and mark this player as the last raiser
                self.round_complete = False
            else:
                return False  # Invalid raise amount
        
        # Store the last action for display purposes
        self.last_action = {
            "player": player.name,
            "action": action,
            "amount": amount if action == "raise" else self.current_bet
        }
        
        # Move to next player
        self.next_player()
        self.check_round_end()
        return True

# Game instance
game = TexasHoldem()

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.is_hovered = False
    
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Create buttons
start_button = Button(350, 500, 100, 40, "Start", GREEN)
fold_button = Button(200, 500, 100, 40, "Fold", RED)
check_button = Button(310, 500, 100, 40, "Check", BLUE)
call_button = Button(420, 500, 100, 40, "Call", BLUE)
raise_button = Button(530, 500, 100, 40, "Raise", GREEN)

# Slider class
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.dragging = False
        self.handle_rect = pygame.Rect(x, y - 10, 10, height + 20)
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Calculate handle position
        handle_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width - self.handle_rect.width / 2
        self.handle_rect.x = handle_x
        
        pygame.draw.rect(screen, RED, self.handle_rect)
        
        # Display value
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(str(self.value), True, BLACK)
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.y - 20))
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            self.value = int(self.min_val + (self.max_val - self.min_val) * (rel_x / self.rect.width))
            self.value = max(self.min_val, min(self.max_val, self.value))

# Raise slider
raise_slider = Slider(200, 550, 400, 10, 20, 100)

# Main game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True
        
        # Handle slider events
        raise_slider.handle_event(event)
    
    # Clear screen
    screen.fill(GREEN)
    
    # Draw based on game state
    if game.game_state == "waiting":
        start_button.check_hover(mouse_pos)
        start_button.draw()
        
        # Game title and instructions
        font = pygame.font.SysFont(None, 36)
        title_text = font.render("Texas Hold'em Poker", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        
        font = pygame.font.SysFont(None, 24)
        instruction_text = font.render("Click 'Start' button to begin the game", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 150))
        
        # Game rules
        font = pygame.font.SysFont(None, 20)
        rules = [
            "GAME FLOW:",
            "1. Each player receives 2 cards",
            "2. Betting rounds: Preflop -> Flop (3 cards) -> Turn (1 card) -> River (1 card)",
            "3. Choose actions: Bet, Check, Call, Raise, or Fold during each round",
            "4. The player with the best hand or last player remaining wins"
        ]
        
        y_pos = 200
        for rule in rules:
            rule_text = font.render(rule, True, WHITE)
            screen.blit(rule_text, (WIDTH//2 - rule_text.get_width()//2, y_pos))
            y_pos += 25
        
        if start_button.is_clicked(mouse_pos, mouse_click):
            game.start_new_hand()
    else:
        # Draw community cards
        for i, card in enumerate(game.community_cards):
            card.draw(300 + i * 60, 250)
        
        # Draw player hands
        font = pygame.font.SysFont(None, 24)
        
        # Player's cards
        text = font.render(f"{game.players[0].name} (Chips: {game.players[0].chips})", True, WHITE)
        screen.blit(text, (350, 400))
        for i, card in enumerate(game.players[0].hand):
            card.draw(350 + i * 60, 430)
        
        # CPU cards (face down)
        for p_idx, player in enumerate(game.players[1:], 1):
            text = font.render(f"{player.name} (Chips: {player.chips})", True, WHITE)
            if p_idx == 1:  # Left
                screen.blit(text, (100, 200))
                for i, card in enumerate(player.hand):
                    card.draw(100 + i * 60, 230, face_up=False)
            elif p_idx == 2:  # Top
                screen.blit(text, (350, 50))
                for i, card in enumerate(player.hand):
                    card.draw(350 + i * 60, 80, face_up=False)
            elif p_idx == 3:  # Right
                screen.blit(text, (600, 200))
                for i, card in enumerate(player.hand):
                    card.draw(600 + i * 60, 230, face_up=False)
        
        # Display pot
        pot_text = font.render(f"Pot: {game.pot}", True, WHITE)
        screen.blit(pot_text, (350, 350))
        
        # Display game state
        state_text = font.render(f"State: {game.game_state}", True, WHITE)
        screen.blit(state_text, (50, 50))
        
        # Display current player
        current_player = game.players[game.current_player_index]
        current_player_text = font.render(f"Current Player: {current_player.name}", True, WHITE)
        screen.blit(current_player_text, (50, 80))
        
        # Display current bet
        bet_text = font.render(f"Current Bet: {game.current_bet}", True, WHITE)
        screen.blit(bet_text, (50, 110))
        
        # Display last action
        if game.last_action:
            action_name = game.last_action["action"].upper()
            player_name = game.last_action["player"]
            
            if action_name == "RAISE":
                action_text = f"Last action: {player_name} {action_name}D to {game.last_action['amount']}"
            else:
                action_text = f"Last action: {player_name} {action_name}ED"
                
            last_action_text = font.render(action_text, True, WHITE)
            screen.blit(last_action_text, (50, 140))
        
        # Action explanations
        action_title = font.render("ACTION GUIDE:", True, WHITE)
        screen.blit(action_title, (600, 50))
        
        action_font = pygame.font.SysFont(None, 18)
        actions = [
            "Fold: Give up your hand and exit this round",
            "Check: Pass without betting (if no bet is required)",
            "Call: Match the current bet amount",
            "Raise: Increase the bet amount"
        ]
        
        y_pos = 80
        for action in actions:
            action_text = action_font.render(action, True, WHITE)
            screen.blit(action_text, (600, y_pos))
            y_pos += 20
        
        # Player's turn - show action buttons
        if game.current_player_index == 0 and game.game_state != "showdown":
            # Check if this is the first action in a new betting round
            is_first_action = game.last_action is None
            
            # Available actions depend on game state and position
            fold_button.check_hover(mouse_pos)
            
            # Only show check if no bet has been made or it's the first action after flop/turn/river
            if game.players[0].current_bet == game.current_bet:
                check_button.check_hover(mouse_pos)
                check_button.draw()
            else:
                call_button.check_hover(mouse_pos)
                call_button.draw()
            
            raise_button.check_hover(mouse_pos)
            
            fold_button.draw()
            raise_button.draw()
            
            # Button descriptions
            font = pygame.font.SysFont(None, 18)
            fold_text = font.render("Discard your hand", True, WHITE)
            raise_text = font.render("Increase bet", True, WHITE)
            
            screen.blit(fold_text, (fold_button.rect.x, fold_button.rect.y + fold_button.rect.height + 5))
            
            if game.players[0].current_bet == game.current_bet:
                check_text = font.render("Pass without betting", True, WHITE)
                screen.blit(check_text, (check_button.rect.x, check_button.rect.y + check_button.rect.height + 5))
            else:
                call_text = font.render("Match current bet", True, WHITE)
                screen.blit(call_text, (call_button.rect.x, call_button.rect.y + call_button.rect.height + 5))
                
            screen.blit(raise_text, (raise_button.rect.x, raise_button.rect.y + raise_button.rect.height + 5))
            
            # Draw raise slider
            raise_slider.draw()
            
            # Slider description
            slider_text = font.render("<- Drag to adjust raise amount ->", True, WHITE)
            screen.blit(slider_text, (raise_slider.rect.x + 120, raise_slider.rect.y + 20))
            
            # Button click handling
            if fold_button.is_clicked(mouse_pos, mouse_click):
                game.player_action("fold")
                # Display player action
                action_message = "You chose to FOLD"
                action_font = pygame.font.SysFont(None, 24)
                action_surface = action_font.render(action_message, True, WHITE)
                action_rect = action_surface.get_rect(center=(WIDTH//2, 180))
                screen.blit(action_surface, action_rect)
                pygame.display.flip()
                pygame.time.delay(1000)  # Show the action for 1 second
                
            elif check_button.is_clicked(mouse_pos, mouse_click):
                if game.players[0].current_bet == game.current_bet:
                    game.player_action("check")
                    # Display player action
                    action_message = "You chose to CHECK"
                    action_font = pygame.font.SysFont(None, 24)
                    action_surface = action_font.render(action_message, True, WHITE)
                    action_rect = action_surface.get_rect(center=(WIDTH//2, 180))
                    screen.blit(action_surface, action_rect)
                    pygame.display.flip()
                    pygame.time.delay(1000)  # Show the action for 1 second
                    
            elif call_button.is_clicked(mouse_pos, mouse_click):
                game.player_action("call")
                # Display player action
                action_message = "You chose to CALL"
                action_font = pygame.font.SysFont(None, 24)
                action_surface = action_font.render(action_message, True, WHITE)
                action_rect = action_surface.get_rect(center=(WIDTH//2, 180))
                screen.blit(action_surface, action_rect)
                pygame.display.flip()
                pygame.time.delay(1000)  # Show the action for 1 second
                
            elif raise_button.is_clicked(mouse_pos, mouse_click):
                game.player_action("raise", raise_slider.value)
                # Display player action
                action_message = f"You chose to RAISE to {raise_slider.value}"
                action_font = pygame.font.SysFont(None, 24)
                action_surface = action_font.render(action_message, True, WHITE)
                action_rect = action_surface.get_rect(center=(WIDTH//2, 180))
                screen.blit(action_surface, action_rect)
                pygame.display.flip()
                pygame.time.delay(1000)  # Show the action for 1 second
        
        # CPU's turn - simple AI
        elif game.current_player_index != 0 and game.game_state != "showdown":
            # Simple AI: random action with weighted probabilities
            current_player = game.players[game.current_player_index]
            
            # Available actions depend on game state and position
            if current_player.current_bet == game.current_bet:
                # Can check if no bet has been made
                actions = ["fold", "check", "raise"]
                weights = [0.1, 0.6, 0.3]  # 10% fold, 60% check, 30% raise
            else:
                # Must call, raise or fold
                actions = ["fold", "call", "raise"]
                weights = [0.3, 0.5, 0.2]  # 30% fold, 50% call, 20% raise
            
            action = random.choices(actions, weights=weights)[0]
            
            # Display CPU action
            font = pygame.font.SysFont(None, 24)
            
            if action == "raise":
                raise_amount = random.randint(game.current_bet + 10, game.current_bet + 50)
                action_text = f"{current_player.name} chooses to {action.upper()} to {raise_amount}"
            else:
                action_text = f"{current_player.name} chooses to {action.upper()}"
                
            action_surface = font.render(action_text, True, WHITE)
            action_rect = action_surface.get_rect(center=(WIDTH//2, 180))
            screen.blit(action_surface, action_rect)
            pygame.display.flip()
            pygame.time.delay(1000)  # Show the action for 1 second
            
            # Execute the action
            if action == "fold":
                game.player_action("fold")
            elif action == "check":
                game.player_action("check")
            elif action == "call":
                game.player_action("call")
            elif action == "raise":
                game.player_action("raise", raise_amount)
    
    # Update display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
