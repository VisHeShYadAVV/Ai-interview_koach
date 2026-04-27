import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { environment } from '../environments/environment';

interface Message {
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'SmartKoach - AI Interview Coach';
  private readonly initialWelcomeMessage = 'Welcome to SmartKoach! I\'m your AI Interview Coach. Select a domain and difficulty level, then send a message to start your interview preparation.';
  private readonly initialDomain = 'DSA';
  private readonly initialDifficultyType = 'Beginner';
  private readonly initialDifficulty = 'Easy';
  messages: Message[] = [];
  userMessage = '';
  selectedDomain = this.initialDomain;
  selectedDifficultyType = this.initialDifficultyType;
  selectedDifficulty = this.initialDifficulty;
  isLoading = false;
  
  domains = ['DSA', 'ML', 'DBMS', 'OS', 'English', 'Botany', 'Math', 'Computer Networks', 'System Design', 'AI'];
  readonly difficultyTypes = ['Beginner', 'Intermediate', 'Advanced'];
  readonly difficulties = ['Easy', 'Medium', 'Hard'];
  difficulties = ['Easy', 'Medium', 'Hard'];
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {
    this.restoreInitialState();
  }

  sendMessage() {
    if (!this.userMessage.trim() || this.isLoading) {
      return;
    }

    const message = this.userMessage.trim();
    const domain = this.normalizeSelection(this.selectedDomain, this.initialDomain);
    const difficultyType = this.selectedDifficultyType;
    const difficulty = this.selectedDifficulty;
    this.userMessage = '';
    this.selectedDomain = domain;
    this.selectedDifficultyType = difficultyType;
    this.selectedDifficulty = difficulty;
    
    // Add user message to chat
    this.addUserMessage(message);
    
    // Show loading state
    this.isLoading = true;

    // Call backend API
    this.http.post<{ reply: string }>(`${this.apiUrl}/chat`, {
      message: message,
      domain: domain,
      difficultyType: difficultyType,
      difficulty: difficulty
    }).subscribe({
      next: (response) => {
        const aiReply = response.reply?.trim();
        this.addAIMessage(aiReply || 'Received an empty response from the server. Please try again.');
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error:', error);
        const backendError = typeof error?.error?.detail === 'string' ? error.error.detail : '';
        this.addAIMessage(backendError || 'Sorry, there was an error processing your request. Please check if the backend is running and try again.');
        this.isLoading = false;
      }
    });
  }

  resetChat() {
    this.http.post(`${this.apiUrl}/reset`, {}).subscribe({
      next: () => {
        this.restoreInitialState();
      },
      error: (error) => {
        console.error('Error resetting chat:', error);
      }
    });
  }

  private restoreInitialState() {
    this.messages = [];
    this.userMessage = '';
    this.selectedDomain = this.initialDomain;
    this.selectedDifficultyType = this.initialDifficultyType;
    this.selectedDifficulty = this.initialDifficulty;
    this.isLoading = false;
    this.addAIMessage(this.initialWelcomeMessage);
  }

  private addUserMessage(text: string) {
    this.messages.push({
      text,
      sender: 'user',
      timestamp: new Date()
    });
    this.scrollToBottom();
  }

  private addAIMessage(text: string) {
    this.messages.push({
      text,
      sender: 'ai',
      timestamp: new Date()
    });
    this.scrollToBottom();
  }

  private scrollToBottom() {
    setTimeout(() => {
      const chatContainer = document.querySelector('.chat-messages');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 100);
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  private normalizeSelection(value: string, fallback: string): string {
    const normalized = value?.trim();
    return normalized ? normalized : fallback;
  }
}
