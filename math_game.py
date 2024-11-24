import pygame
import random
import sys
import time
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
GREEN = (50, 205, 50)
YELLOW = (255, 215, 0)

# Game settings
TOTAL_QUESTIONS = 30
INITIAL_LIVES = 3

# Try to load sound effects
try:
    pygame.mixer.init()
    wrong_sound = pygame.mixer.Sound(os.path.join("sounds", "wrong.wav"))
    correct_sound = pygame.mixer.Sound(os.path.join("sounds", "correct.wav"))
    wrong_sound.set_volume(0.5)
    correct_sound.set_volume(0.3)
except:
    wrong_sound = None
    correct_sound = None

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.is_hovered = False

    def draw(self, surface):
        color = self.color if not self.is_hovered else tuple(min(c + 30, 255) for c in self.color)
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)
        
        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Math Challenge Game")
        self.clock = pygame.time.Clock()
        
        self.lives = INITIAL_LIVES
        self.score = 0
        self.current_question = 1
        self.answer = ""
        self.feedback = ""
        self.feedback_color = BLACK
        self.feedback_timer = 0
        self.shake_screen = False
        self.shake_frames = 0
        
        # Create number buttons
        self.number_buttons = []
        button_width = 60
        button_height = 60
        start_x = (WINDOW_WIDTH - (button_width * 3 + 20 * 2)) // 2
        start_y = 400
        
        for i in range(9):
            x = start_x + (i % 3) * (button_width + 10)
            y = start_y + (i // 3) * (button_height + 10)
            self.number_buttons.append(Button(x, y, button_width, button_height, str(i + 1), WHITE))
            
        # Add 0, decimal point, and backspace
        self.number_buttons.append(Button(start_x + button_width + 10, start_y + 3 * (button_height + 10), 
                                        button_width, button_height, "0", WHITE))
        self.number_buttons.append(Button(start_x, start_y + 3 * (button_height + 10), 
                                        button_width, button_height, ".", WHITE))
        self.number_buttons.append(Button(start_x + 2 * (button_width + 10), start_y + 3 * (button_height + 10), 
                                        button_width, button_height, "←", RED))
        
        # Submit button
        self.submit_button = Button(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 80, 
                                  120, 50, "Submit", GREEN)
        
        self.generate_question()

    def generate_question(self):
        operations = ['+', '-', '*']
        self.operation = random.choice(operations)
        
        if self.operation == '+':
            self.num1 = random.randint(1, 100)
            self.num2 = random.randint(1, 100)
        elif self.operation == '-':
            self.num1 = random.randint(1, 100)
            self.num2 = random.randint(1, self.num1)
        else:  # multiplication
            self.num1 = random.randint(1, 12)
            self.num2 = random.randint(1, 12)
        
        self.correct_answer = eval(f"{self.num1} {self.operation} {self.num2}")

    def draw_progress_bar(self):
        bar_width = 600
        bar_height = 20
        x = (WINDOW_WIDTH - bar_width) // 2
        y = 50
        
        # Draw background
        pygame.draw.rect(self.screen, WHITE, (x, y, bar_width, bar_height))
        
        # Draw progress
        progress_width = int(bar_width * (self.current_question - 1) / TOTAL_QUESTIONS)
        pygame.draw.rect(self.screen, GREEN, (x, y, progress_width, bar_height))
        
        # Draw border
        pygame.draw.rect(self.screen, BLACK, (x, y, bar_width, bar_height), 2)
        
        # Draw progress text
        font = pygame.font.Font(None, 24)
        progress_text = f"Question {self.current_question}/{TOTAL_QUESTIONS}"
        text_surface = font.render(progress_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, y + bar_height + 15))
        self.screen.blit(text_surface, text_rect)

    def draw_lives(self):
        heart = "❤️"
        font = pygame.font.Font(None, 40)
        text_surface = font.render(f"Lives: {heart * self.lives}", True, RED)
        text_rect = text_surface.get_rect(topleft=(20, 20))
        self.screen.blit(text_surface, text_rect)

    def draw_score(self):
        font = pygame.font.Font(None, 40)
        text_surface = font.render(f"Score: {self.score}", True, BLUE)
        text_rect = text_surface.get_rect(topright=(WINDOW_WIDTH - 20, 20))
        self.screen.blit(text_surface, text_rect)

    def draw_question(self):
        font = pygame.font.Font(None, 48)
        question_text = f"What is {self.num1} {self.operation} {self.num2}?"
        text_surface = font.render(question_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(text_surface, text_rect)

    def draw_answer(self):
        # Draw answer box
        answer_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 200, 200, 50)
        pygame.draw.rect(self.screen, WHITE, answer_rect)
        pygame.draw.rect(self.screen, BLACK, answer_rect, 2)
        
        # Draw answer text
        font = pygame.font.Font(None, 40)
        text_surface = font.render(self.answer, True, BLACK)
        text_rect = text_surface.get_rect(center=answer_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_feedback(self):
        if self.feedback and time.time() - self.feedback_timer < 2:
            font = pygame.font.Font(None, 40)
            text_surface = font.render(self.feedback, True, self.feedback_color)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 300))
            self.screen.blit(text_surface, text_rect)

    def show_game_over(self):
        self.screen.fill(BLUE)
        font = pygame.font.Font(None, 64)
        
        # Game Over text
        text_surface = font.render("Game Over!", True, WHITE)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(text_surface, text_rect)
        
        # Final score
        font = pygame.font.Font(None, 48)
        score_text = f"Final Score: {self.score}/{TOTAL_QUESTIONS}"
        score_surface = font.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_surface, score_rect)
        
        # Play again button
        play_again_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, 
                                 200, 50, "Play Again", GREEN)
        play_again_button.draw(self.screen)
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if play_again_button.handle_event(event):
                    self.__init__()
                    waiting = False

    def shake(self):
        self.shake_screen = True
        self.shake_frames = 10

    def run(self):
        running = True
        while running:
            screen_offset = (0, 0)
            if self.shake_screen and self.shake_frames > 0:
                screen_offset = (random.randint(-5, 5), random.randint(-5, 5))
                self.shake_frames -= 1
                if self.shake_frames <= 0:
                    self.shake_screen = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle number button clicks
                for button in self.number_buttons:
                    if button.handle_event(event):
                        if button.text == "←":
                            self.answer = self.answer[:-1]
                        elif len(self.answer) < 10:  # Limit answer length
                            if button.text == "." and "." in self.answer:
                                continue
                            self.answer += button.text
                
                # Handle submit button click
                if self.submit_button.handle_event(event):
                    try:
                        user_answer = float(self.answer) if self.answer else 0
                        if abs(user_answer - self.correct_answer) < 0.01:
                            self.score += 1
                            self.feedback = "Correct! ✨"
                            self.feedback_color = GREEN
                            if correct_sound:
                                correct_sound.play()
                        else:
                            self.lives -= 1
                            self.feedback = f"Wrong! Answer was {self.correct_answer}"
                            self.feedback_color = RED
                            if wrong_sound:
                                wrong_sound.play()
                            self.shake()
                        
                        self.feedback_timer = time.time()
                        self.answer = ""
                        self.current_question += 1
                        
                        if self.lives <= 0 or self.current_question > TOTAL_QUESTIONS:
                            self.show_game_over()
                        else:
                            self.generate_question()
                            
                    except ValueError:
                        self.feedback = "Please enter a valid number!"
                        self.feedback_color = RED
                        self.feedback_timer = time.time()
            
            # Draw everything
            self.screen.fill(BLUE)
            
            # Apply screen shake
            if screen_offset != (0, 0):
                self.screen.blit(self.screen, screen_offset)
            
            self.draw_progress_bar()
            self.draw_lives()
            self.draw_score()
            self.draw_question()
            self.draw_answer()
            self.draw_feedback()
            
            # Draw buttons
            for button in self.number_buttons:
                button.draw(self.screen)
            self.submit_button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
